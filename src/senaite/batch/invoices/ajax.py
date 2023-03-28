# -*- coding: utf-8 -*-

from collections import OrderedDict
from pkg_resources import resource_filename
from senaite.impress.ajax import AjaxPublishView as AP
from senaite.impress.interfaces import IMultiReportView
from senaite.impress.interfaces import IReportWrapper
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

    def get_report_template(self, template=None):
        """Returns the path of report template
        """
        # TODO: create a utility template as done in senaite.impress
        path = "browser/batch/templates/MultiBatchInvoice.pt"
        template = resource_filename("senaite.batch.invoices", path)
        return template

    def ajax_render_reports(self, *args):
        """Renders all reports and returns the html

        This method also groups the reports by client
        """
        # update the request form with the parsed json data
        data = self.get_json()

        uids = data.get("items", [])
        template = data.get("template")
        # Lookup the requested template
        path = "browser/batch/templates/MultiBatchInvoice.pt"
        template = resource_filename("senaite.batch.invoices", path)
        paperformat = data.get("format", "A4")
        orientation = data.get("orientation", "portrait")
        # custom report options
        report_options = data.get("report_options", {})

        # generate the reports
        reports = self.generate_reports_for(uids,
                                            group_by="getClientUID",
                                            template=template,
                                            paperformat=paperformat,
                                            orientation=orientation,
                                            report_options=report_options)

        return "\n".join(map(lambda r: r.html, reports))

    def render_report(self, model, template, paperformat, orientation, **kw):
        """Render a SuperModel to HTML
        """
        # get the report view controller
        view = self.get_report_view_controller(model, IMultiReportView)

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
        path = "browser/batch/templates/MultiBatchInvoice.pt"
        template = resource_filename("senaite.batch.invoices", path)

        # get the selected paperformat
        paperformat = data.get("format")

        # get the selected orientation
        orientation = data.get("orientation", "portrait")

        # get the publisher instance
        publisher = self.publisher
        parser = publisher.get_parser(html)
        # get INVOICE number
        batch_invoice_number = parser.find_all(attrs={'name': 'batch_invoice_number'})
        batch_invoice_number = batch_invoice_number.pop()
        batch_invoice_number = batch_invoice_number.text.strip()
        kwargs = {"batch_invoice_number": batch_invoice_number}
        total_VAT = parser.find_all(attrs={'name': 'total_VAT'})
        total_VAT = total_VAT.pop()
        total_VAT = total_VAT.text.strip()
        kwargs["total_VAT"] = float(total_VAT)
        # VAT, S
        total_amount = parser.find_all(attrs={'name': 'total_amount'})
        total_amount = total_amount.pop()
        total_amount = total_amount.text.strip()
        kwargs["total_amount"] = float(total_amount)
        # sub_total
        sub_total = parser.find_all(attrs={'name': 'sub_total'})
        sub_total = sub_total.pop()
        sub_total = sub_total.text.strip()
        kwargs["sub_total"] = float(sub_total)

        # get a timestamp
        timestamp = DateTime().ISO()

        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Print CSS: {}".format(css))

        # get the publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)

        # split the html per report
        # NOTE: each report is an instance of <bs4.Tag>
        html_reports = publisher.parse_reports(html)

        # extract the UIDs of each HTML report
        # NOTE: UIDs are injected in `.analysisrequest.reportview.render`
        report_uids = map(
            lambda report: report.get("uids", "").split(","), html_reports)

        # get the storage multi-adapter to save the generated PDFs
        storage = getMultiAdapter(
            (self.context, self.request), IPdfReportStorage)

        report_groups = []
        for html, uids in zip(html_reports, report_uids):
            # ensure we have valid UIDs here
            uids = filter(api.is_uid, uids)
            # convert the bs4.Tag back to pure HTML
            html = publisher.to_html(html)
            # wrap the report
            report = getMultiAdapter((html,
                                      map(self.to_model, uids),
                                      template,
                                      paperformat,
                                      orientation,
                                      None,
                                      publisher), interface=IReportWrapper)

            # BBB: inject contained UIDs into metadata
            metadata = report.get_metadata(
                contained_requests=uids, timestamp=timestamp)
            # store the report(s)
            objs = storage.store(report.pdf, html, uids, metadata=metadata, **kwargs)
            # append the generated reports to the list
            report_groups.append(objs)

        # NOTE: The reports might be stored in multiple places (clients),
        #       which makes it difficult to redirect to a single exit URL
        #       based on the action the users clicked (save/email)
        exit_urls = map(lambda reports: self.get_exit_url_for(
            reports, action=action), report_groups)

        if not exit_urls:
            return api.get_url(self.context)

        # Group the urls by path. This makes possible to at least return a
        # single url for multiple uids when the base path (e.g. client) is the
        # same. This is required for Single Reports, for which there are as many
        # report groups as samples, regardless of clients
        groups = OrderedDict()
        for url in exit_urls:
            base_path, uids = url.split("?uids=")
            path_uids = groups.get(base_path, "")
            groups[base_path] = ",".join(filter(None, [path_uids, uids]))
        exit_url = "{}/{}?uids={}".format(api.get_url(self.context), action, uids)
        return exit_url
