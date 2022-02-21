# -*- coding: utf-8 -*-

import six
from collections import OrderedDict
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import view
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from bika.lims import api
from bika.lims.interfaces import IBatch
from bika.lims.api import mail as mailapi
from bika.lims.utils import to_utf8
from bika.lims.browser.publish.emailview import EmailView as EV

from senaite.batch.invoices import _


class EmailView(EV):
    """Overrride Email Attachments View
    """

    implements(IPublishTraverse)
    template = ViewPageTemplateFile("templates/email.pt")
    email_template = ViewPageTemplateFile("templates/email_template.pt")

    def __init__(self, context, request):
        super(EmailView, self).__init__(context, request)

    @property
    @view.memoize
    def reports(self):
        """Return the objects from the UIDs given in the request
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", [])
        # handle 'uids' GET parameter coming from a redirect
        if isinstance(uids, six.string_types):
            uids = uids.split(",")
        uids = filter(api.is_uid, uids)
        unique_uids = OrderedDict().fromkeys(uids).keys()
        # TODO: uids
        return self.get_object_by_uid(uids[0])

    @property
    def reports_data(self):
        """Returns a list of report data dictionaries
        """
        reports = self.reports
        return [self.get_report_data(reports)]

    @property
    def exit_url(self):
        """Exit URL for redirect
        """
        endpoint = "reports_listing"
        if IBatch.providedBy(self.context):
            endpoint = "invoices-issued"
        return "{}/{}".format(
            api.get_url(self.context), endpoint)

    def get_recipients_data(self, batch):
        """Recipients data to be used in the template
        """

        if not batch:
            return []

        recipients = []
        recipient_names = []

        samples = batch.getAnalysisRequests()

        for num, sample in enumerate(samples):
            report_recipient_names = []
            for recipient in super(EmailView, self).get_recipients(sample):
                name = recipient.get("Fullname")
                email = recipient.get("EmailAddress")
                address = mailapi.to_email_address(email, name=name)
                record = {
                    "name": name,
                    "email": email,
                    "address": address,
                    "valid": True,
                }
                if record not in recipients:
                    recipients.append(record)
                # remember the name of the recipient for this sample
                report_recipient_names.append(name)
            recipient_names.append(report_recipient_names)

        # recipient names, which all of the reports have in common
        common_names = set(recipient_names[0]).intersection(*recipient_names)
        # mark recipients not in common
        for recipient in recipients:
            if recipient.get("name") not in common_names:
                recipient["valid"] = False
        lab_billing_email = self.laboratory.Schema()['BillingEmailAddress'].getAccessor(self.laboratory)()
        if lab_billing_email:
            address = mailapi.to_email_address(lab_billing_email, name="Laboratory Billing EmailAddress")
            record = {
                "name": "Laboratory Billing EmailAddress",
                "email": lab_billing_email,
                "address": address,
                "valid": True,
            }
            recipients.append(record)

        for sample in samples:
            # get client from the sample
            client_billing_email = sample.aq_parent.Schema()['BillingEmailAddress'].getAccessor(sample.aq_parent)()
            if client_billing_email:
                name = "{} Billing EmailAddress".format(sample.getName()) 
                address = mailapi.to_email_address(client_billing_email, name=name)
                record = {
                    "name": name,
                    "email": client_billing_email,
                    "address": address,
                    "valid": True,
                }
                recipients.append(record)
                break
        return recipients

    def get_responsibles_data(self, batch):
        """Responsibles data to be used in the template
        """
        if not batch:
            return []

        recipients = []
        recipient_names = []

        samples = batch.getAnalysisRequests()
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
        pdf = report.batch_invoice_pdf
        filesize = "{} Kb".format(self.get_filesize(pdf))
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
        return subject.format(_(self.reports.Title()))
