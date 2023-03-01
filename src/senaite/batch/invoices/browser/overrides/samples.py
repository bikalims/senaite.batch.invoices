# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.utils import t
from bika.lims.utils import get_image
from senaite.batch.invoices import _
from senaite.core.browser.samples.view import SamplesView as SV


class SamplesView(SV):
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        if finacials:
            invoice_allowed_states = ("sample_due", "sample_received")
            invoiced = {"id": "invoiced",
                        "title": get_image("invoiced.png",
                                           title=t(_("Invoiced"))),
                        "columns": self.columns.keys(),
                        "contentFilter": {
                            "invoiced_state": "invoiced",
                            "review_state": invoice_allowed_states},
                        }
            to_be_invoiced = {"id": "uninvoiced",
                              "title": get_image("uninvoiced.png",
                                                 title=t(_("To be invoiced"))),
                              "columns": self.columns.keys(),
                              "contentFilter": {
                                  "invoiced_state": "uninvoiced",
                                  "review_state": invoice_allowed_states},
                              }
            self.review_states.append(to_be_invoiced)
            self.review_states.append(invoiced)
