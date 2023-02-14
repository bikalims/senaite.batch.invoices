# -*- coding: utf-8 -*-

from senaite.batch.invoices import _
from senaite.core.browser.samples.view import SamplesView as SV


class SamplesView(SV):
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        invoiced = {"id": "to_be_invoiced",
                    "title": _("To be invoiced"),
                    "columns": self.columns.keys(),
                    "contentFilter": {"review_state": "to_be_invoiced"}
                    }
        self.review_states.append(invoiced)
