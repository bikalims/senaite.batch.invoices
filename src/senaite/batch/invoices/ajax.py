# -*- coding: utf-8 -*-

from pkg_resources import resource_filename
from senaite.impress.ajax import AjaxPublishView as AP
from senaite.impress.interfaces import IReportView
from senaite.impress.decorators import timeit
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from DateTime import DateTime
from senaite.impress import logger
from senaite.impress.interfaces import IPdfReportStorage
from bika.lims import api


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
        model = collection[0] if collection else None

        # Lookup the requested template
        path = "browser/batch/templates/BatchInvoice.pt"
        template = resource_filename("senaite.batch.invoices", path)

        htmls = []

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

    @timeit()
    def ajax_save_reports(self):
        """Render all reports as PDFs and store them as AR Reports
        """
        # Data sent via async ajax call as JSON data from the frontend
        data = self.get_json()

        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # NOTE: It might also contain multiple reports!
        html = data.get("html")

        # get the triggered action (Save|Email)
        action = data.get("action", "save")

        # get the selected template
        template = data.get("template")

        # get the selected paperformat
        paperformat = data.get("format")

        # get the selected orientation
        orientation = data.get("orientation", "portrait")

        # get a timestamp
        timestamp = DateTime().ISO8601()

        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Print CSS: {}".format(css))

        # get the publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)

        # get batch_invoice_number 
        parser = publisher.get_parser(html)
        batch_invoice_number = parser.find_all(attrs={'name': 'batch_invoice_number'})
        batch_invoice_number = batch_invoice_number.pop()
        batch_invoice_number = batch_invoice_number.text.strip()

        # split the html per report
        # NOTE: each report is an instance of <bs4.Tag>
        html_report = publisher.parse_reports(html)

        # generate a PDF for each HTML report
        pdf_reports = map(publisher.write_pdf, html_report)

        # extract the UIDs of each HTML report
        # NOTE: UIDs are injected in `.analysisrequest.reportview.render`
        # TODO: uids returns list should be single uid
        batch_invoice_uid = html_report[0].get("uids", "").split(",")[0]

        # get the storage multi-adapter to save the generated PDFs
        storage = getMultiAdapter(
            (self.context, self.request), IPdfReportStorage)

        report_groups = []
        pdf, html = pdf_reports, html_report
        # prepare some metadata
        # NOTE: We are doing it in the loop to ensure a new dictionary is
        #       created for each report.
        metadata = {
            "template": template,
            "paperformat": paperformat,
            "orientation": orientation,
            "timestamp": timestamp,
        }
        # ensure we have valid UIDs here
        uid = api.is_uid(batch_invoice_uid)
        # convert the bs4.Tag back to pure HTML
        # TODO: html returns a list
        html = publisher.to_html(html[0])
        # BBB: inject contained UIDs into metadata
        metadata["contained_requests"] = batch_invoice_uid
        # store the report(s)
        objs = storage.store(pdf[0], html, batch_invoice_uid, metadata=metadata, coa_num=batch_invoice_number)
        exit_url = "{}/{}?uids={}".format(
            api.get_url(self.context), action, ",".join([objs.UID()]))

        return exit_url
