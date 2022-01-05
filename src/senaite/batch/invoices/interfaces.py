# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewletManager


class ISenaiteBatchInvoicesLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IInvoice(Interface):
    """Invoice
    """

class IInvoices(Interface):
    """Invoice
    """
class ISenaiteImpressBatchInvoiceHtmlHead(IViewletManager):
    """Invoice
    """
