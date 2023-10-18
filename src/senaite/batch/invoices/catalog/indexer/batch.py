# -*- coding: utf-8 -*-

from bika.lims.interfaces import IBatch
from plone.indexer import indexer


@indexer(IBatch)
def batch_invoiced_state(instance):

    status = "uninvoiced"
    for sample in instance.getAnalysisRequests():
        try:
            status = sample.invoiced_state
        except Exception:
            status = "uninvoiced"
    return status
