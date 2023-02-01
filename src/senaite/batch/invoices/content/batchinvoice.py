# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.interfaces import IBatch, IClient
from senaite.batch.invoices import _
from senaite.core.interfaces import IHideActionsMenu

from plone.dexterity.content import Item
from plone.supermodel import model

from plone.formwidget.contenttree import ObjPathSourceBinder
from zope import schema
from zope.interface import implementer
from z3c.relationfield.schema import RelationChoice
from plone.namedfile.field import NamedBlobFile
from senaite.batch.invoices.interfaces import IBatchInvoice


class IBatchInvoiceSchema(model.Schema):
    invoice_pdf = NamedBlobFile(title=_(u"Batch Invoice PDF"), required=False)
    client = RelationChoice(
        title=_(u"Client"),
        source=ObjPathSourceBinder(object_provides=IClient.__identifier__),
        required=False,
    )
    batch = RelationChoice(
        title=_(u"Batch"),
        source=ObjPathSourceBinder(object_provides=IBatch.__identifier__),
        required=False,
    )
    # invoice_date = schema.Datetime(
    #     title='Batch Invoice Date',
    #     description='Batch Date invoice was generated',
    #     required=False,
    # )


@implementer(IBatchInvoice, IBatchInvoiceSchema, IHideActionsMenu)
class BatchInvoice(Item):
    _catalogs = ['portal_catalog']
    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname):
        """Return the field accessor for the fieldname"""
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname"""
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        result = schema[fieldname].set
        self.reindexObject()
        return result
