# -*- coding: utf-8 -*-

from ...browser.batch.batchinvoice_listing import ReportsListingView


class BatchInvoicesView(ReportsListingView):
    """Displays all available sample containers in a table
    """

    def __init__(self, context, request):
        super(BatchInvoicesView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "BatchInvoice",
            "sort_on": "created",
            "sort_order": "descending",
        }
