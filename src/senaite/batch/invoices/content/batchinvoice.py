# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.namedfile.field import NamedBlobFile
from plone.formwidget.contenttree import ObjPathSourceBinder
from zope import schema
from zope.interface import implementer
from zope.interface import Interface
from z3c.relationfield.schema import RelationChoice

from bika.lims import api
from bika.lims.interfaces import IBatch, IClient
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridField, DataGridRow

from senaite.batch.invoices import _
from senaite.core.interfaces import IHideActionsMenu
from senaite.batch.invoices.interfaces import IBatchInvoice


class IMetadataSchema(Interface):
    paper_format = schema.TextLine(title=_(u"Paper format"), required=False,)
    timestamp = schema.Datetime(title=_(u"Timestamp"), required=False,)
    orientation = schema.List(
        title=_(u"orientation"),
        value_type=schema.Choice(values=["Portrait", "Landscape"],),
        required=False,
    )
    template = schema.TextLine(title=_(u"Template"), required=False,)
    contained_batches = UIDReferenceField(
        title=_(u"Container Type"),
        allowed_types=("Batches",),
        multi_valued=True,
        required=False,
    )


class ISendLogSchema(Interface):
    actor = schema.TextLine(title=_(u"Actor"), required=False,)
    actor_fullname = schema.TextLine(title=_(u"Actor Fullname"), required=False,)
    email_send_date = schema.Datetime(title=_(u"Email Send Date"), required=False,)
    email_recipients = schema.TextLine(title=_(u"Email Recipients"), required=False,)
    email_responsibles = schema.TextLine(title=_(u"Email Responsible"), required=False,)
    email_subject = schema.TextLine(title=_(u"Email Subject"), required=False,)
    email_body = schema.TextLine(title=_(u"Email Body"), required=False,)
    email_attachments = schema.TextLine(title=_(u"Email Attachments"), required=False,)


class IRecipientSchema(Interface):
    uid = schema.TextLine(title=_(u"UID"), required=False,)
    username = schema.TextLine(title=_(u"Username"), required=False,)
    fullname = schema.TextLine(title=_(u"Fullname"), required=False,)
    email = schema.TextLine(title=_(u"Email"), required=False,)
    publication_mode = schema.TextLine(title=_(u"PublicationModes"), required=False,)


class IBatchInvoiceSchema(model.Schema):
    invoice_pdf = NamedBlobFile(title=_(u"Batch Invoice PDF"), required=False)
    invoice_html = schema.TextLine(title=_(u"Batch Invoice HTML"), required=False,)
    client = UIDReferenceField(
        title=_(u"Client"),
        allowed_types=("Client",),
        multi_valued=False,
        required=False,
    )
    batch = UIDReferenceField(
        title=_(u"Batch"),
        allowed_types=("Batch",),
        multi_valued=False,
        required=False,
    )
    containedbatcheinvoices = UIDReferenceField(
        title=_(u"Batches"),
        allowed_types=("Batch",),
        multi_valued=True,
        required=False,
    )
    invoice_date = schema.Datetime(title=_(u"Batch Invoice Date"), required=False,)
    metadata = DataGridField(
        title=_("Metadata"),
        value_type=DataGridRow(title=u"Table", schema=IMetadataSchema),
        default=[],
        required=False,
    )
    sendlog = DataGridField(
        title=_("SendLog"),
        value_type=DataGridRow(title=u"Table", schema=ISendLogSchema),
        default=[],
        required=False,
    )
    recipients = DataGridField(
        title=_("Recipients"),
        value_type=DataGridRow(title=u"Table", schema=IRecipientSchema),
        default=[],
        required=False,
    )
    subtotal = schema.Float(title=u"Subtotal", required=False,)
    vat = schema.Float(title=u"VAT", required=False,)
    total = schema.Float(title=u"Total", required=False,)


@implementer(IBatchInvoice, IBatchInvoiceSchema, IHideActionsMenu)
class BatchInvoice(Item):
    _catalogs = ["portal_catalog"]
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
