# -*- coding: utf-8 -*-

import six
import transaction

from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collections import OrderedDict
from plone.memoize import view
from string import Template
from zope.interface import implements
from zope.lifecycleevent import modified
from zope.publisher.interfaces import IPublishTraverse

from bika.lims import api
from bika.lims.api import mail as mailapi
from bika.lims.interfaces import IBatch
# from bika.lims.utils import to_utf8
from bika.lims.browser.publish.emailview import EmailView as EV

from senaite.batch.invoices import _
from senaite.batch.invoices import logger


class EmailView(EV):
    """Overrride Email Attachments View
    """

    implements(IPublishTraverse)
    template = ViewPageTemplateFile("templates/email.pt")
    email_template = ViewPageTemplateFile("templates/email_template.pt")

    def __init__(self, context, request):
        super(EmailView, self).__init__(context, request)

    def store_multireports_individually(self):
        """Returns the configured setting from the registry
        """
        store_individually = api.get_registry_record(
            "senaite.impress.store_multireports_individually")
        return store_individually

    @property
    @view.memoize
    def batches(self):
        """Return the objects from the UIDs given in the request
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", [])
        # handle 'uids' GET parameter coming from a redirect
        if isinstance(uids, six.string_types):
            uids = uids.split(",")
        uids = filter(api.is_uid, uids)
        unique_uids = OrderedDict().fromkeys(uids).keys()
        batch_invoices = map(self.get_object_by_uid, unique_uids)
        batches = []
        for ba in batch_invoices:
            batch = api.get_object_by_uid(ba.batch)
            if not IBatch.providedBy(batch):
                continue
            if not self.store_multireports_individually():
                batches.extend(map(self.get_object_by_uid, ba.containedbatcheinvoices))
                break
            else:
                batches.append(batch)
        return batches

    @property
    def exit_url(self):
        """Exit URL for redirect
        """
        endpoint = "batch_invoices"
        if IBatch.providedBy(self.context):
            endpoint = "invoices-issued"
        return "{}/{}".format(
            api.get_url(self.context), endpoint)

    def get_recipients_data(self, batches):
        """Recipients data to be used in the template
        """

        if not batches:
            return []

        recipients = []
        setup = api.get_setup()

        send_copy_to = setup.Schema()['SendInvoiceCopiesTo'].getAccessor(setup)()
        for copy in send_copy_to:
            if copy == "ClientInvoiceEAddr":
                client = self.batches[0].getClient()
                client_billing_email = client.Schema()['BillingEmailAddress'].getAccessor(client)()
                if client_billing_email:
                    name = "{} Client Billing EmailAddress".format(client_billing_email)
                    address = mailapi.to_email_address(client_billing_email, name=name)
                    record = {
                        "name": name,
                        "email": client_billing_email,
                        "address": address,
                        "valid": True,
                    }
                    recipients.append(record)

            if copy == "LabAccEAddr":
                lab_billing_email = self.laboratory.Schema()['BillingEmailAddress'].getAccessor(self.laboratory)()
                if lab_billing_email:
                    name = "Laboratory Billing EmailAddress"
                    address = mailapi.to_email_address(lab_billing_email, name=name)
                    record = {
                        "name": name,
                        "email": lab_billing_email,
                        "address": address,
                        "valid": True,
                    }
                    recipients.append(record)

        return recipients

    def get_responsibles_data(self, batches):
        """Responsibles data to be used in the template
        """
        if not batches:
            return []

        recipients = []
        recipient_names = []

        samples = []
        for batch in batches:
            samples.extend(batch.getAnalysisRequests())

        for num, sample in enumerate(samples):
            # recipient names of this report
            report_recipient_names = []
            responsibles = sample.getResponsible()
            for manager_id in responsibles.get("ids", []):
                responsible = responsibles["dict"][manager_id]
                name = responsible.get("name")
                email = responsible.get("email")
                address = mailapi.to_email_address(email, name=name)
                record = {
                    "name": name,
                    "email": email,
                    "address": address,
                    "valid": True,
                }
                if record not in recipients:
                    recipients.append(record)
                # remember the name of the recipient for this report
                report_recipient_names.append(name)
            recipient_names.append(report_recipient_names)

        # recipient names, which all of the reports have in common
        common_names = set(recipient_names[0]).intersection(*recipient_names)
        # mark recipients not in common
        for recipient in recipients:
            if recipient.get("name") not in common_names:
                recipient["valid"] = False

        return recipients

    def get_report_data(self, report):
        """Report data to be used in the template
        """
        # TODO: BUG
        pdf = report.invoice_pdf
        filesize = "{} Kb".format(pdf.getSize())
        filename = "{}.pdf".format(report.id)

        return {
            "sample": report,
            "attachments": {},
            "pdf": pdf,
            "obj": report,
            "uid": api.get_uid(report),
            "filesize": filesize,
            "filename": filename,
        }

    @property
    def batch_id(self):
        """Returns the client name
        """
        return safe_unicode(self.context.id)

    @property
    def batch_url(self):
        """Returns the client name
        """
        return safe_unicode(self.context.absolute_url())

    @property
    def batch_description(self):
        """Returns the client name
        """
        return safe_unicode(self.context.description)

    @property
    def client_batch_id(self):
        """Returns the client name
        """
        return safe_unicode(self.context.getClientBatchID())

    @property
    def email_subject(self):
        """Email subject line to be used in the template
        """
        # request parameter has precedence
        subject = self.request.get("subject", None)
        if subject is not None:
            return subject
        subject = self.context.translate(_("Batch Invoice {}"))
        return subject.format(_(self.reports[0].getId()))

    def publish_samples(self):
        """Invoice all batches of the reports
        """

        # collect primary + contained samples of the reports
        # invoice all batches + their samples
        for report in self.batches:
            self.invoice_batch(report)

    def invoice_batch(self, batch):
        """Set status to prepublished/published/republished
        """
        logger.info("Invoicing batch {}".format(api.get_id(batch)))
        try:
            # Manually update the view on the database to avoid conflict errors
            batch.getClient()._p_jar.sync()
            batch.batch_invoiced_state = "invoiced"
            batch.reindexObject()
            self.do_action_to_samples(batch)
            # Commit the changes
            transaction.commit()
        except WorkflowException as e:
            logger.error(e)

    @property
    def email_attachments(self):
        attachments = []

        # Convert report PDFs -> email attachments
        for report in self.reports:
            pdf = report.invoice_pdf
            if pdf is None:
                logger.error("Skipping empty PDF for report {}"
                             .format(report.getId()))
                continue
            filename = pdf.filename
            filedata = pdf.data
            attachments.append(
                mailapi.to_email_attachment(filedata, filename))

        # Convert additional attachments
        for attachment in self.attachments:
            af = attachment.getAttachmentFile()
            filedata = af.data
            filename = af.filename
            attachments.append(
                mailapi.to_email_attachment(filedata, filename))

        return attachments

    def do_action_to_samples(self, batch):
        """Cascades the transition to the analysis request analyses. If all_analyses
        is set to True, the transition will be triggered for all analyses of this
        analysis request, those from the descendant partitions included.
        """
        samples = batch.getAnalysisRequests()
        for sample in samples:
            sample.invoiced_state = "invoiced"
            sample.reindexObject()
            modified(sample)

    def form_action_send(self):
        """Send form handler
        """
        # send email to the selected recipients and responsibles
        success = self.send_email(self.email_recipients_and_responsibles,
                                  self.email_subject,
                                  self.email_body,
                                  attachments=self.email_attachments)

        if success:
            message = _(u"Message sent to {}".format(
                ", ".join(self.email_recipients_and_responsibles)))
            self.add_status_message(message, "info")
        else:
            message = _("Failed to send Email(s)")
            self.add_status_message(message, "error")

        self.request.response.redirect(self.exit_url)

    @property
    def client_name(self):
        """Returns the client name
        """
        return safe_unicode(self.batches[0].getClient().Title())

    @property
    def email_body(self):
        """Email body text to be used in the template
        """
        # request parameter has precedence
        body = self.request.get("body", None)
        if body is not None:
            return body

        setup = api.get_setup()
        schema = setup.Schema()
        body = schema['InvoiceEmailBody'].getAccessor(setup)()
        if not body:
            return self.context.translate(_(self.email_template(self)))

        template_context = {
            "client_name": self.client_name,
            "lab_name": self.lab_name,
            "lab_address": self.lab_address,
            "batches": ",".join([b.getId() for b in self.batches]),
        }
        rendered_body = self.render_email_template(
            body, template_context=template_context)
        return rendered_body

    def render_email_template(self, template, template_context=None):
        """Return the rendered email template

        This method interpolates the $recipients variable with the selected
        recipients from the email form.

        :params template: Email body text
        :returns: Rendered email template
        """

        # allow to add translation for initial template
        template = self.context.translate(_(template))
        recipients = self.email_recipients_and_responsibles
        if template_context is None:
            template_context = {
                "recipients": "<br/>".join(recipients),
                "batches": ",".join([b.getId() for b in self.batches]),
            }

        email_template = Template(safe_unicode(template)).safe_substitute(
            **template_context)

        return email_template
