# -*- coding: utf-8 -*-

from string import Template
from decimal import Decimal
from DateTime import DateTime

from bika.lims import api
from senaite.impress import logger
from senaite.impress.analysisrequest.reportview import ReportView


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

    def get_template_context(self, model, **kw):
        context = {
            "uids": model.UID(),
            "client_uid": model.getClientUID(),
        }
        context.update(kw)
        return context

    def get_samples(self, model_or_collection):
        """Returns a flat list of all analyses for the given model or collection
        """
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
