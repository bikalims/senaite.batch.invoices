# -*- coding: utf-8 -*-

from senaite.impress.publishview import PublishView as PV
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BatchInvoiceView(PV):
    """Analyses Invoice View
    """
    template = ViewPageTemplateFile("templates/publish.pt")

    def __init__(self, context, request):
        super(BatchInvoiceView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # disable the editable border
        self.request.set("disable_border", 1)
        return self.template()

    def setup(self):
        return self.portal.bika_setup
