# -*- coding: utf-8 -*-

from senaite.core.interfaces import IHideActionsMenu
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implementer


class IBatchInvoices(model.Schema):
    pass


@implementer(IBatchInvoices, IHideActionsMenu)
class BatchInvoices(Container):
    pass
