# -*- coding: utf-8 -*-

import transaction
from bika.lims import api
from DateTime import DateTime
from senaite.impress import logger
from senaite.impress.decorators import synchronized
from senaite.impress.storage import PdfReportStorageAdapter as PRSA
from plone.namedfile.file import NamedBlobFile


class PdfReportStorageAdapter(PRSA):
    """Storage adapter for PDF batchinvoices
    """

    def store(self, pdf, html, uids, metadata=None, **kwargs):
        """Store the PDF

        :param pdf: generated PDF report (binary)
        :param html: report HTML (string)
        :param uids: UIDs of the objects contained in the PDF
        :param metadata: dict of metadata to store
        """

        if metadata is None:
            metadata = {}

        # get the contained objects
        objs = map(api.get_object_by_uid, uids)

        # # handle primary object storage
        # if not self.store_multireports_individually():
        #     # reduce the list to the primary object only
        #     objs = [self.get_primary_report(objs)]

        # generate the reports
        reports = []
        for obj in objs:
            report = self.create_report(obj, pdf, html, uids, metadata, **kwargs)
            reports.append(report)

        return reports

    @synchronized(max_connections=1)
    def create_report(self, parent, pdf, html, uids, metadata, **kwargs):
        """Create a new batchinvoice object

        NOTE: We limit the creation of reports to 1 to avoid conflict errors on
              simultaneous publication.

        :param parent: parent object where to create the report inside
        :returns: BatchInvoice
        """

        parent_id = api.get_id(parent)
        logger.info("Create BatchInvoice for {} ...".format(parent_id))

        # Manually update the view on the database to avoid conflict errors
        parent._p_jar.sync()
        today = DateTime()
        batch_invoice_number = kwargs.get("batch_invoice_number")

        # Create the report object
        filename = u"{}.pdf".format(batch_invoice_number)
        report = api.create(
            parent, "BatchInvoice",
            title=batch_invoice_number,
            batch=api.get_uid(parent),
            containedbatcheinvoices=uids,
            client=parent.getClient().UID(),
            subtotal=kwargs.get("sub_total"),
            vat=kwargs.get("total_VAT"),
            total=kwargs.get("total_amount"),
            # invoice_date=today.Date(),
        )
        report.invoice_pdf = NamedBlobFile(
            data=pdf, contentType='application/pdf', filename=filename)
        transaction.commit()
        logger.info("Create Report for {} [DONE]".format(parent_id))

        return report
