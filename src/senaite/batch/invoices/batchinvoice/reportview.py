# -*- coding: utf-8 -*-

from string import Template
from decimal import Decimal
from DateTime import DateTime
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18n.locales import locales

from bika.lims import api
from senaite.impress import logger
from senaite.impress.analysisrequest.reportview import ReportView
from senaite.impress.analysisrequest.reportview import MultiReportView as MRV

LOGO = "/++plone++bika.coa.static/images/bikalimslogo.png"

SINGLE_TEMPLATE = Template(
    """<!-- Batch Invoice Report -->
<div class="report" uids="${uids}" client_uid="${client_uid}">
  <script type="text/javascript">
    console.log("*** BEFORE TEMPLATE RENDER ***");
  </script>
  ${template}
</div>
"""
)


MULTI_TEMPLATE = Template("""<!-- Multi Report -->
<div class="report" uids="${uids}" client_uid="${client_uid}">
  <script type="text/javascript">
    console.log("*** BEFORE MULTI TEMPLATE RENDER ***");
  </script>
  ${template}
</div>
""")


class BatchInvoiceReportView(ReportView):
    """View for Single Reports
    """

    def __init__(self, model, request):
        logger.info("BatchInvoiceReportView::__init__:model={}".format(model))
        super(BatchInvoiceReportView, self).__init__(model, request)
        self.model = model
        self.request = request

    def render(self, template, **kw):
        context = self.get_template_context(self.model, **kw)
        template = Template(template).safe_substitute(context)
        return SINGLE_TEMPLATE.safe_substitute(context, template=template)


class MultiReportView(MRV):
    """View for Multi Reports
    """

    def __init__(self, collection, request):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        super(MultiReportView, self).__init__(collection, request)
        self.collection = collection
        self.request = request

    def get_batch_invoice_number(self, model):
        query = {"portal_type": "BatchInvoice",
                 "sort_on": "created",
                 "sort_order": "descending",
                 }
        brains = api.search(query, "portal_catalog")
        if len(brains):
            coa = brains[0]
            title_split = coa.getId.split("-")
            if len(title_split) == 2 and len(title_split[-1]) == 5:
                string = title_split[0]
                num = int(title_split[-1])
                num += 1
                coa_num = u"{}-{:04d}".format(string, num)
            else:
                coa_num = "Invalid Number, please check IDServer"
        return coa_num

    def get_client(self, collection):
        return collection[0].getClient()

    def get_coa_styles(self):
        registry = getUtility(IRegistry)
        styles = {}
        try:
            ac_style = registry["senaite.coa_logo_accredition_styles"]
        except (AttributeError, KeyError):
            styles["ac_styles"] = "max-height:68px;"
        css = map(lambda ac_style: "{}:{};".format(*ac_style), ac_style.items())
        css.append("max-width:200px;")
        styles["ac_styles"] = " ".join(css)

        try:
            logo_style = registry["senaite.coa_logo_styles"]
        except (AttributeError, KeyError):
            styles["logo_styles"] = "height:15px;"
        css = map(lambda logo_style: "{}:{};".format(*logo_style), logo_style.items())
        styles["logo_styles"] = " ".join(css)
        return styles

    def get_toolbar_logo(self):
        registry = getUtility(IRegistry)
        portal_url = self.portal_url
        try:
            logo = registry["senaite.toolbar_logo"]
        except (AttributeError, KeyError):
            logo = LOGO
        if not logo:
            logo = LOGO
        return portal_url + logo

    def render(self, template, **kw):
        """Wrap the template and render
        """
        context = self.get_template_context(self.collection, **kw)
        template = Template(template).safe_substitute(context)
        return MULTI_TEMPLATE.safe_substitute(context, template=template)

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale("en")
        setup = api.get_setup()
        currency = setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    @view.memoize
    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        setup = api.get_setup()
        return setup.getDecimalMark()

    def format_price(self, price):
        """Formats the price with the set decimal mark and currency
        """
        # ensure we have a float
        price = api.to_float(price, default=0.0)
        dm = self.get_decimal_mark()
        cur = self.get_currency_symbol()
        price = "%s %.2f" % (cur, price)
        return price.replace(".", dm)

    def get_invoice_lines(self, model_or_collection):
        batch_data = {}

        total_VAT = 0
        total_amount = 0
        for batch in model_or_collection:
            ars = batch.instance.getAnalysisRequests()
            for ar in ars:
                total_VAT += ar.getVATAmount()
                total_amount += ar.getTotalPrice()
                analyses = ar.getAnalyses()
                for a in analyses:
                    a_title = a.Title
                    if a_title not in batch_data:
                        analysis = a.getObject()
                        batch_data[a_title] = {
                            "qty": 0,
                            "price": Decimal(analysis.getPrice()),
                            "f_price": self.format_price(analysis.getPrice()),
                        }
                    batch_data[a_title]["qty"] += 1

        batch_keys = batch_data.keys()
        for b_key in batch_keys:
            batch_data[b_key]["amount"] = batch_data[b_key]["qty"] * batch_data[b_key]["price"]
            batch_data[b_key]["amount"] = self.format_price(batch_data[b_key]["amount"])

        invoice_data = {}
        invoice_data["batch_data"] = batch_data
        invoice_data["sub_total"] = "{:.2f}".format(total_amount - total_VAT)
        invoice_data["f_sub_total"] = self.format_price(total_amount - total_VAT)
        invoice_data["VAT_label"] = "{}% VAT".format(self.setup.getVAT())
        invoice_data["total_VAT"] = "{:.2f}".format(total_VAT)
        invoice_data["f_total_VAT"] = self.format_price(total_VAT)

        invoice_data["total_amount"] = "{:.2f}".format(total_amount)
        invoice_data["f_total_amount"] = self.format_price(total_amount)
        today = DateTime()
        invoice_data["today"] = today.strftime("%d %B %Y")

        return invoice_data

    def get_footer_text(self):
        """Returns the footer text from the setup
        """
        setup = api.get_setup()
        schema = setup.Schema()
        footer = schema['InvoiceFooter'].getAccessor(setup)()
        return footer

    def get_pages(self, options):
        if options.get("orientation", "") == "portrait":
            num_per_page = 5
        elif options.get("orientation", "") == "landscape":
            num_per_page = 8
        else:
            logger.error("get_pages: orientation unknown")
            num_per_page = 5
        logger.info(
            "get_pages: col len = {}; num_per_page = {}".format(
                len(self.collection), num_per_page
            )
        )
        pages = []
        new_page = []
        for idx, col in enumerate(self.collection):
            if idx % num_per_page == 0:
                if len(new_page):
                    pages.append(new_page)
                    logger.info("New page len = {}".format(len(new_page)))
                new_page = [col]
                continue
            new_page.append(col)

        if len(new_page) > 0:
            pages.append(new_page)
            logger.info("Last page len = {}".format(len(new_page)))
        return pages

    def to_localized_date(self, date):
        return self.to_localized_time(date)[:10]

    def get_template_context(self, collection, **kw):
        if not collection:
            return {}
        uids = map(lambda m: m.uid, collection)
        client_uid = collection[0].getClientUID()
        context = {
            "uids": ",".join(uids),
            "client_uid": client_uid,
        }
        context.update(kw)
        return context
