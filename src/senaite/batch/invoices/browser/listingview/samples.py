# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import t
from bika.lims.utils import get_image
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.batch.invoices import _
from senaite.batch.invoices import is_installed


class SamplesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        if finacials:
            invoice_allowed_states = ("sample_due", "sample_received")
            invoiced = {"id": "invoiced",
                        "title": get_image("invoiced.png",
                                           title=t(_("Invoiced"))),
                        "columns": self.listing.columns.keys(),
                        "contentFilter": {
                            "invoiced_state": "invoiced",
                            "review_state": invoice_allowed_states},
                        }
            to_be_invoiced = {"id": "uninvoiced",
                              "title": get_image("uninvoiced.png",
                                                 title=t(_("To be invoiced"))),
                              "columns": self.listing.columns.keys(),
                              "contentFilter": {
                                  "invoiced_state": "uninvoiced",
                                  "review_state": invoice_allowed_states},
                              }
            self.listing.review_states.append(to_be_invoiced)
            self.listing.review_states.append(invoiced)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        return item
