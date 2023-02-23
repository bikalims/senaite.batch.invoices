# -*- coding: utf-8 -*-

from senaite.batch.invoices import _
from bika.lims.browser.batch.analysisrequests import \
    AnalysisRequestsView as ARV


class AnalysisRequestsView(ARV):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        invoiced = {"id": "invoiced",
                    "title": _("Invoiced"),
                    "columns": self.columns.keys(),
                    "contentFilter": {"invoiced_state": "invoiced"}
                    }

        uninvoiced = {"id": "uninvoiced",
                    "title": _("To be invoiced"),
                    "columns": self.columns.keys(),
                    "contentFilter": {"invoiced_state": "uninvoiced"}
                    }
        self.review_states.append(invoiced)
        self.review_states.append(uninvoiced)
