# -*- coding: utf-8 -*-

from bika.lims.interfaces import IBatch, IClient
from senaite.batch.invoices import _
from senaite.core.interfaces import IHideActionsMenu

from plone.dexterity.content import Item
from plone.supermodel import model

from plone.formwidget.contenttree import ObjPathSourceBinder
from zope import schema
from zope.interface import implementer
from z3c.relationfield.schema import RelationChoice


class IBatchInvoice(model.Schema):
    batch_invoice_pdf = schema.NamedFile(title=_(u"Batch Invoice PDF"))
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
    invoice_date = schema.Datetime(
        title='Batch Invoice Date',
        description='Batch Date invoice was generated',
        required=False,
    )


@implementer(IBatchInvoice, IHideActionsMenu)
class BatchInvoice(Item):
    _catalogs = ['portal_catalog']
