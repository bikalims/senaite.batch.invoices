# -*- coding: utf-8 -*-

from string import Template
from decimal import Decimal
from DateTime import DateTime

from bika.lims import api
from senaite.impress import logger
from senaite.impress.analysisrequest.reportview import ReportView
from senaite.impress.analysisrequest.reportview import MultiReportView as MRV


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

    def get_samples(self, model_or_collection):
        """Returns a flat list of all analyses for the given model or collection
        """
        return {}
        samples = model_or_collection.instance.getAnalysisRequests()
        data = []
        batch_data = {
            "date": self.to_localized_time(self.timestamp, **{"long_format": False}),
            "total_subtotal": Decimal("0.0"),
            "total_discount": Decimal("0.0"),
            "total_vat": Decimal("0.0"),
            "total_price": Decimal("0.0"),
            "MemberDiscount": "{}% Discount".format(self.setup.getMemberDiscount()),
            "VAT": "{}% VAT".format(self.setup.getVAT()),
        }
        for sample in samples:
            sample_data = {
                "ClientSID": sample.getClientSampleID(),
                "SampleID": sample.getId(),
                "SampleTypeTitle": sample.getSampleTypeTitle(),
                "DateReceived": self.to_localized_time(sample.getDateReceived()),
                "Description": sample.description,
                "Subtotal": sample.getSubtotal(),
                "TotalPrice": sample.getTotalPrice(),
                "Total": sample.getTotal(),
                "VATAmount": sample.getVATAmount(),
                "DiscountAmount": sample.getDiscountAmount(),
            }
            data.append(sample_data)
            batch_data["total_subtotal"] += sample.getSubtotal()
            batch_data["total_discount"] += sample.getDiscountAmount()
            batch_data["total_vat"] += sample.getVATAmount()
            batch_data["total_price"] += sample.getTotalPrice()

        batch_data["total_subtotal"] = "{:.2f}".format(batch_data["total_subtotal"])
        batch_data["total_discount"] = "{:.2f}".format(batch_data["total_discount"])
        batch_data["total_vat"] = "{:.2f}".format(batch_data["total_vat"])
        batch_data["total_price"] = "{:.2f}".format(batch_data["total_price"])

        return {"samples": data, "batch_data": batch_data}

    def get_batch_invoice_number(self, model):
        instance = model.instance
        today = DateTime()
        query = {
            "portal_type": "BatchInvoice",
            "path": {"query": api.get_path(instance)},
            "created": {"query": today.Date(), "range": "min"},
            "sort_on": "created",
            "sort_order": "descending",
        }
        brains = api.search(query, "portal_catalog")
        num = 1
        if len(brains):
            coa = brains[0]
            num = coa.Title.split("-INV")[-1]
            num = int(num)
            num += 1
        coa_num = "{}-INV{:02d}".format(instance.getId(), num)
        return coa_num


class MultiReportView(MRV):
    """View for Multi Reports
    """

    def __init__(self, collection, request):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        super(MultiReportView, self).__init__(collection, request)
        self.collection = collection
        self.request = request

    def render(self, template, **kw):
        """Wrap the template and render
        """
        context = self.get_template_context(self.collection, **kw)
        template = Template(template).safe_substitute(context)
        return MULTI_TEMPLATE.safe_substitute(context, template=template)

    def get_invoice_lines(self, model_or_collection):
        batch_data = {}

        sub_total = 0
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
                        batch_data[a_title] =  {
                            "qty":0, 
                            "price": Decimal(analysis.getPrice()), 
                            }
                    batch_data[a_title]["qty"] +=1
                    
        batch_keys = batch_data.keys()
        for b_key in batch_keys:
            batch_data[b_key]["amount"] = batch_data[b_key]["qty"] * batch_data[b_key]["price"]

        invoice_data = {}
        invoice_data["batch_data"] = batch_data
        invoice_data["sub_total"] = "{:.2f}".format(total_amount - total_VAT)
        invoice_data["VAT_label"] =  "{}% VAT".format(self.setup.getVAT())
        invoice_data["total_VAT"] = "{:.2f}".format(total_VAT)

        invoice_data["total_amount"] = "{:.2f}".format(total_amount)

        return invoice_data

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
