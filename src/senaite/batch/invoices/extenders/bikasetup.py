# -*- coding: utf-8 -*-

from Products.Archetypes.Widget import BooleanWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.Widget import RichWidget
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implementer

from .fields import ExtBooleanField, ExtTextField, ExtStringField, ExtLinesField
from bika.lims.interfaces import IBikaSetup
from senaite.batch.invoices import _
from senaite.batch.invoices.interfaces import ISenaiteBatchInvoicesLayer

financials_field = ExtBooleanField(
    "Financials",
    mode="rw",
    schemata="Accounting",
    widget=BooleanWidget(
        label=_(u"Batch Invoicing"),
        description=_(u"Enables batch invoicing functionality"),
    )
)

invoiceforpublishedsamplesonly_field = ExtBooleanField(
    "InvoiceForPublishedSamplesOnly",
    mode="rw",
    schemata="Accounting",
    widget=BooleanWidget(
        label=_(u"Invoice for published samples only"),
        description=_(u"If left disabled, samples will be invoiced after registration"),
    )
)

invoice_email_body_field = ExtTextField(
    "InvoiceEmailBody",
    mode="rw",
    default_content_type="text/html",
    default_output_type="text/x-html-safe",
    schemata="Accounting",
    # Needed to fetch the default value from the registry
    widget=RichWidget(
        label=_(
            "label_bikasetup_invoice_email_body",
            "Email body for Batch Invoicing notifications"),
        description=_(
            "description_bikasetup_invoice_email_body",
            default="Set the email body text to be used by default when "
            "sending out result reports to the selected recipients. "
            "You can use reserved keywords: "
            "$client_name, $recipients, $lab_name, $lab_address, $batches"),
        default_mime_type="text/x-html",
        output_mime_type="text/x-html",
        allow_file_upload=False,
        rows=15,
    ),
)

send_invoice_copies_to = ExtLinesField(
    "SendInvoiceCopiesTo",
    mode="rw",
    schemata="Accounting",
    vocabulary=[(_(u'ClientInvoiceEAddr'), _(u'Client invoice email address')),
                (_(u'LabAccEAddr'), _(u'Lab accounts email address'))],
    widget=MultiSelectionWidget(
        label=_(u"Send Invoice copies to:"),
        description=_(u"Select who to send invoices to. \n"
                      u"Press Ctrl also to select multiple values"),
        select_format="checkbox"
    )
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    layer = ISenaiteBatchInvoicesLayer

    fields = [
        financials_field,
        invoiceforpublishedsamplesonly_field,
        send_invoice_copies_to,
        invoice_email_body_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
