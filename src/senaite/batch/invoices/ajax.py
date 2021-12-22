# -*- coding: utf-8 -*-

import StringIO
import csv
from bika.coa import logger
from bika.lims import api
from DateTime import DateTime
from senaite.app.supermodel.interfaces import ISuperModel
from senaite.impress.interfaces import IPdfReportStorage
from senaite.impress.interfaces import ITemplateFinder
from senaite.impress.ajax import AjaxPublishView as AP
from zope.component import getMultiAdapter
from zope.component import getAdapter
from zope.component import getUtility


class AjaxPublishView(AP):
    def __init__(self, context, request):
        super(AP, self).__init__(context, request)
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def ajax_templates(self):
        """Returns the available templates
        """
        finder = getUtility(ITemplateFinder)
        templates = finder.get_templates(extensions=[".pt", ".html"])
        return sorted([item[0] for item in templates if 'bika' in item[0]])

    def ajax_render_reports(self, *args):
        super(AjaxPublishView, self).ajax_render_reports(self)
        """Renders all reports and returns the html

        This method also groups the reports by client
        """
        # update the request form with the parsed json data
        data = self.get_json()

        paperformat = data.get("format", "A4")
        orientation = data.get("orientation", "portrait")
        # custom report options
        report_options = data.get("report_options", {})

        # Create a collection of the requested UIDs
        collection = self.get_collection([self.context.UID()])

        # Lookup the requested template
        template = '/home/lunga/workspace/plone/bika/src/senaite.batch.invoices/src/senaite/batch/invoices/browser/batch/templates/BatchInvoice.pt'
        is_multi_template = self.is_multi_template(template)

        htmls = []

        # always group ARs by client
        grouped_by_client = self.group_items_by("getClientUID", collection)

        # iterate over the ARs of each client
        for client_uid, collection in grouped_by_client.items():
            # render single report
            for model in collection:
                html = self.render_report(model,
                                          template,
                                          paperformat=paperformat,
                                          orientation=orientation,
                                          report_options=report_options)
                htmls.append(html)

        return "\n".join(htmls)
