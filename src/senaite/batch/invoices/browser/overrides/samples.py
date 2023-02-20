# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.batch.invoices import _
from senaite.core.browser.samples.view import SamplesView as SV


class SamplesView(SV):
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        inv_pub = setup.Schema()['InvoiceForPublishedSamplesOnly'].getAccessor(setup)()
        if finacials and inv_pub:
            invoiced = {"id": "invoiced",
                        "title": _("Invoiced"),
                        "columns": self.columns.keys(),
                        "contentFilter": {"review_state": "invoiced"}
                        }
            self.review_states.insert(1, invoiced)

            to_be_invoiced = {"id": "to_be_invoiced",
                              "title": _("To be invoiced"),
                              "columns": self.columns.keys(),
                              "contentFilter": {"review_state": "to_be_invoiced"}
                              }
            self.review_states.insert(1, to_be_invoiced)
