# -*- coding: utf-8 -*-

from senaite.core.interfaces import IHideActionsMenu
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implementer
from senaite.batch.invoices.interfaces import IBatchInvoices


class IBatchInvoicesSchema(model.Schema):
    """A container for sample containers
    """


@implementer(IBatchInvoices, IBatchInvoicesSchema, IHideActionsMenu)
class BatchInvoices(Container):
    """A container for sample containers
    """
