# -*- coding: utf-8 -*-

from senaite.batch.invoices.interfaces import IBatchInvoice
from plone.indexer import indexer


@indexer(IBatchInvoice)
def client(instance):
    if not instance.client:
        return instance.getClient().UID()
    return instance.client
