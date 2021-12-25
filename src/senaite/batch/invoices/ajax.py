# -*- coding: utf-8 -*-

from pkg_resources import resource_filename
from senaite.impress.ajax import AjaxPublishView as AP
from senaite.impress.interfaces import IReportView
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter


class AjaxPublishView(AP):
    def __init__(self, context, request):
        super(AP, self).__init__(context, request)
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def ajax_render_reports(self, *args):
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
        path = "browser/batch/templates/BatchInvoice.pt"
        template = resource_filename("senaite.batch.invoices", path)

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

    def render_report(self, model, template, paperformat, orientation, **kw):
        """Render a SuperModel to HTML
        """
        # get the report view controller
        view = self.get_report_view_controller(model, IReportView)

        options = kw
        # pass through the calculated dimensions to the template
        options.update(self.calculate_dimensions(paperformat, orientation))
        template = self.read_template(template, view, **options)
        return view.render(template, **options)

    def get_report_view_controller(self, model_or_collection, interface):
        """Get a suitable report view controller

        Query the controller view as a multi-adapter to allow 3rd party
        overriding with a browser layer.
        """
        name = self.get_report_type()

        context = self.context
        request = self.request

        # Give precedence to multiadapters that adapt the context as well
        view = queryMultiAdapter(
            (context, model_or_collection, request), interface, name=name)
        if view is None:
            # Return the default multiadapter
            return getMultiAdapter(
                (model_or_collection, request), interface, name=name)
        return view

    def get_report_type(self):
        """Returns the (portal-) for the report
        """
        # We fall back to AnalysisRequest here, because this is the primary
        # report object we need at the moment.
        # However, we can later easy provide with this mechanism reports for
        # any other content type as well.
        return self.request.form.get("type", "Batch")
