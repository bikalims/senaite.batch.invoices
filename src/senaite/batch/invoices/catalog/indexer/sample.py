# -*- coding: utf-8 -*-

from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer


@indexer(IAnalysisRequest)
def invoiced_state(instance):
    """Returns `invoiced`, `uninvoiced` or 'not_applicable' depending on the
    state of the analysisrequest contains. Return `uninvoiced` if
    the Analysis Request has at least one 'active' analysis in `uninvoiced`
    status. Returns 'invoiced' if all 'active' analyses of the sample are
    invoiced to a Worksheet. Returns 'not_applicable' if no 'active' analyses
    for the given sample exist
    """
    try:
        invoiced_state = instance.invoiced_state
    except Exception as e:
        return "uninvoiced"
    return invoiced_state
