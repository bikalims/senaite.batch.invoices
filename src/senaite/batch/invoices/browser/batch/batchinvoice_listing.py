# -*- coding: utf-8 -*-

import collections
from Products.CMFPlone.utils import safe_unicode
from ZODB.POSException import POSKeyError

from bika.lims import api
from bika.lims import bikaMessageFactory as _BMF
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from bika.lims.utils import to_utf8
from senaite.app.listing import ListingView


class ReportsListingView(ListingView):
    """Listing view of all generated reports
    """

    def __init__(self, context, request):
        super(ReportsListingView, self).__init__(context, request)

        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "BatchInvoice",
            "path": {
                "query": api.get_path(self.context),
            },
            "sort_on": "created",
            "sort_order": "descending",
        }
        self.form_id = "batchinvoice_listing"

        t = self.context.translate
        self.title = t(_("Batch Invoices"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "++resource++bika.lims.images/invoiced.png"
        )
        self.context_actions = {}

        self.allow_edit = False
        self.show_select_column = True
        self.show_workflow_action_buttons = True
        self.pagesize = 30

        help_email_text = _(
            "Open email form to send the selected reports to the recipients. "
            "This will also publish the contained samples of the reports "
            "after the email was successfully sent.")

        self.send_email_transition = {
            "id": "send_email",
            "title": _("Email"),
            "url": "email",
            "css_class": "btn btn-outline-secondary",
            "help": help_email_text,
        }

        help_publish_text = _(
            "Manually publish all contained samples of the selected reports.")

        self.publish_samples_transition = {
            "id": "publish_samples",
            "title": _("Publish"),
            # see senaite.core.browser.workflow
            "url": "workflow_action?action=publish_samples",
            "css_class": "btn-outline-success",
            "help": help_publish_text,
        }

        help_download_reports_text = _(
            "Download selected reports")

        self.download_reports_transition = {
            "id": "download_reports",
            "title": _("Download"),
            # see senaite.core.browser.workflow
            "url": "workflow_action?action=download_reports",
            "css_class": "btn-outline-secondary",
            "help": help_download_reports_text,
        }

        self.columns = collections.OrderedDict((
            ("BatchInvoiceID", {
                "title": _("Batch Invoice ID"),
                "index": "sortable_title",
                "toggle": True},),
            ("Batches", {
                "title": _("Batches"),
                "index": "sortable_title",
                "toggle": True},),
            ("Client", {
                "title": _("Client"),
                "index": "sortable_title"},),
            ("Batches", {
                "title": _("Batches"),
                "index": "sortable_title",
                "toggle": False},),
            ("State", {
                "title": _("Review State")},),
            ("PDF", {
                "title": _("Download PDF")},),
            ("FileSize", {
                "title": _("Filesize")},),
            ("Subtotal", {
                "title": _("Subtotal")},),
            ("VAT", {
                "title": _("VAT")},),
            ("Total", {
                "title": _("Total")},),
            ("Date", {
                "title": _("Invoice Date")},),
            ("PublishedBy", {
                "title": _("Invoiced By")},),
            ("Recipients", {
                "title": _("Recipients"),
                "toggle": False},),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": "All",
                "contentFilter": {},
                "columns": self.columns.keys(),
                "custom_transitions": [
                    self.send_email_transition,
                    self.publish_samples_transition,
                    self.download_reports_transition,
                ]
            },
        ]

    def get_filesize(self, pdf):
        """Compute the filesize of the PDF
        """
        try:
            filesize = float(pdf.getSize())
            return filesize / 1024
        except (POSKeyError, TypeError):
            return 0

    def localize_date(self, date):
        """Return the localized date
        """
        return self.ulocalized_time(date, long_format=1)

    def get_pdf(self, obj):
        """Get the report PDF
        """
        try:
            return obj.invoice_pdf  # obj.getPdf()
        except (POSKeyError, TypeError):
            return None

    def folderitem(self, obj, item, index):
        """Augment folder listing item
        """

        obj = api.get_object(obj)
        uid = api.get_uid(obj)
        review_state = api.get_workflow_status_of(obj)
        status_title = review_state.capitalize().replace("_", " ")

        item["replace"]["BatchInvoiceID"] = get_link(
            obj.absolute_url(), value=obj.id
        )
        client = obj.getClient()
        item["replace"]["Client"] = get_link(
            client.absolute_url(), value=client.Title()
        )

        pdf = self.get_pdf(obj)
        filesize = self.get_filesize(pdf)
        if filesize > 0:
            url = "{}/@@download/invoice_pdf".format(obj.absolute_url())
            item["replace"]["PDF"] = get_link(
                url, value="PDF", target="_blank")

        item["State"] = _BMF(status_title)
        item["state_class"] = "state-{}".format(review_state)
        item["FileSize"] = "{:.2f} Kb".format(filesize)
        fmt_date = self.localize_date(obj.created())
        item["Date"] = fmt_date
        item["PublishedBy"] = self.user_fullname(obj.Creator())

        # N.B. There is a bug in the current publication machinery, so that
        # only the primary contact get stored in the Attachment as recipient.
        #
        # However, we're interested to show here the full list of recipients,
        # so we use the recipients of the containing AR instead.
        recipients = []

        for recipient in self.get_recipients(obj):
            email = safe_unicode(recipient["EmailAddress"])
            fullname = safe_unicode(recipient["Fullname"])
            if email:
                value = u"<a href='mailto:{}'>{}</a>".format(email, fullname)
                recipients.append(value)
            else:
                message = _("No email address set for this contact")
                value = u"<span title='{}' class='text text-danger'>" \
                        u"⚠ {}</span>".format(message, fullname)
                recipients.append(value)

        item["replace"]["Recipients"] = ", ".join(recipients)

        # No recipient with email set preference found in the AR, so we also
        # flush the Recipients data from the Attachment
        if not recipients:
            item["Recipients"] = ""

        return item

    def get_recipients(self, obj):
        return []
        """Return the AR recipients in the same format like the AR Report
        expects in the records field `Recipients`
        """
        plone_utils = api.get_tool("plone_utils")

        def is_email(email):
            if not plone_utils.validateSingleEmailAddress(email):
                return False
            return True

        def recipient_from_contact(contact):
            if not contact:
                return None
            email = contact.getEmailAddress()
            return {
                "UID": api.get_uid(contact),
                "Username": contact.getUsername(),
                "Fullname": to_utf8(contact.Title()),
                "EmailAddress": email,
            }

        def recipient_from_email(email):
            if not is_email(email):
                return None
            return {
                "UID": "",
                "Username": "",
                "Fullname": email,
                "EmailAddress": email,
            }

        # # Primary Contacts
        # to = filter(None, [recipient_from_contact(ar.getContact())])
        # # CC Contacts
        # cc = filter(None, map(recipient_from_contact, ar.getCCContact()))
        # # CC Emails
        # cc_emails = ar.getCCEmails(as_list=True)
        # cc_emails = filter(None, map(recipient_from_email, cc_emails))

        # return to + cc + cc_emails
