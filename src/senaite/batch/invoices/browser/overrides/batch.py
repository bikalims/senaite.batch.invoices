# -*- coding: utf-8 -*-

from senaite.batch.invoices import _
from bika.lims.browser.batch.analysisrequests import \
    AnalysisRequestsView as ARV


class AnalysisRequestsView(ARV):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        invoiced = {"id": "to_be_invoiced",
                    "title": _("To be invoiced"),
                    "columns": self.columns.keys(),
                    "contentFilter": {"review_state": "to_be_invoiced"}
                    }
        self.review_states.append(invoiced)
