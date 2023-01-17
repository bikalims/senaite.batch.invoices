# -*- coding: utf-8 -*-

from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implementer

from .fields import ExtBooleanField
from bika.lims.interfaces import IBikaSetup
from senaite.batch.invoices import _
from senaite.batch.invoices.interfaces import ISenaiteBatchInvoicesLayer

financials_field = ExtBooleanField(
    "Financials",
    mode="rw",
    schemata="Accounting",
    widget=BooleanWidget(
        label=_(u"Finacials"),
        description=_(u"Enables batch invoicing functionality"),
    )
)

email_invoices_field = ExtBooleanField(
    "EmailInvoices",
    mode="rw",
    schemata="Notifications",
    widget=BooleanWidget(
        label=_(u"Email Invoices to Client Y/N"),
        description=_(u"Enable to email invoices directly to the client's billing email address"),
    )
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    layer = ISenaiteBatchInvoicesLayer

    fields = [
        financials_field,
        email_invoices_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
