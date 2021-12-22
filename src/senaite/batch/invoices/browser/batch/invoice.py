# -*- coding: utf-8 -*-

from bika.lims.browser import BrowserView
from senaite.impress.publishview import PublishView as PV
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BatchInvoiceView(PV):
    """Analyses Invoice View
    """
    # implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/publish.pt")

    def __init__(self, context, request):
        super(BatchInvoiceView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        # disable the editable border
        self.request.set("disable_border", 1)
        import pdb; pdb.set_trace()
        return self.template()

    def get_report_type(self):
        """Returns the (portal-) for the report
        """
        # We fall back to AnalysisRequest here, because this is the primary
        # report object we need at the moment.
        # However, we can later easy provide with this mechanism reports for
        # any other content type as well.
        return self.request.form.get("type", "Batch")

    def get_uids(self):
        """Parse the UIDs from the request `items` parameter
        """
        return [self.context.UID()]

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
