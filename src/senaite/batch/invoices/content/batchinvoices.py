# -*- coding: utf-8 -*-

from senaite.core.interfaces import IHideActionsMenu
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implementer
from senaite.batch.invoices.interfaces import IBatchInvoices


class IBatchInvoicesSchema(model.Schema):
    pass


@implementer(IBatchInvoices, IBatchInvoicesSchema, IHideActionsMenu)
class BatchInvoices(Container):
    pass
