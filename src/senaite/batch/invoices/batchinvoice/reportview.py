# -*- coding: utf-8 -*-

from string import Template

from decimal import Decimal
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
            "total_subtotal": Decimal("0.0"),
            "total_discount": Decimal("0.0"),
            "total_vat": Decimal("0.0"),
            "total_price": Decimal("0.0"),
        }
        for sample in samples:
            sample_data = {
                "ClientSID": sample.getClientSampleID(),
                "SampleID": sample.getId(),
                "SampleTypeTitle": sample.getSampleTypeTitle(),
                "DateReceived": sample.getDateReceived(),
                "Description": sample.description,
                "Subtotal": sample.getSubtotal(),
                "TotalPrice": sample.getTotalPrice(),
                "Total": sample.getTotal(),
                "VATAmount": sample.getVATAmount(),
                "DiscountAmount": sample.getDiscountAmount(),
                "VAT": self.setup.getVAT(),
            }
            data.append(sample_data)
            batch_data["total_subtotal"] += sample.getSubtotal()
            batch_data["total_discount"] += sample.getDiscountAmount()
            batch_data["MemberDiscount"] = "{}% Discount".format(
                self.setup.getMemberDiscount()
            )
            batch_data["VAT"] = "{}% VAT".format(self.setup.getVAT())
            batch_data["total_vat"] += sample.getVATAmount()
            batch_data["total_price"] += sample.getTotalPrice()

        return {"samples": data, "batch_data": batch_data}
