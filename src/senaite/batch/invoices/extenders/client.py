# -*- coding: utf-8 -*-

from Products.Archetypes.Widget import StringWidget
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implementer

from .fields import ExtStringField
from bika.lims.interfaces import IClient
from senaite.batch.invoices import _
from senaite.batch.invoices.interfaces import ISenaiteBatchInvoicesLayer

billing_email_address = ExtStringField(
    "BillingEmailAddress",
    mode="rw",
    schemata="default",
    widget=StringWidget(
        label=_(u"Billing Email Address"),
        description=_(u"Client billing email address"),
    ),
    validators=("isEmail", )
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class ClientSchemaExtender(object):
    adapts(IClient)
    layer = ISenaiteBatchInvoicesLayer

    fields = [
        billing_email_address,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
