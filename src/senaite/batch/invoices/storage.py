# -*- coding: utf-8 -*-

from cStringIO import StringIO
import transaction
from plone import api as ploneapi
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

        # handle primary object storage
        if not self.store_multireports_individually():
            # reduce the list to the primary object only
            objs = [self.get_primary_report(objs)]

        # generate the reports
        reports = []
        for obj in objs:
            report = self.create_report(obj, pdf, html, uids, metadata, **kwargs)
            reports.append(report)

        return reports


    @synchronized(max_connections=1)
    def create_report(self, parent, pdf, html, uids, metadata, coa_num=None, **kwargs):
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

        if coa_num is None:
            query = {
                'portal_type': 'BatchInvoice',
                'path': {
                    'query': api.get_path(parent)
                },
                'modified': {
                    'query': today.Date(),
                    'range': 'min'
                }
            }
            brains = api.search(query, 'portal_catalog')
            coa_num = '{}-INV{:02d}'.format(parent.getId(), len(brains) + 1)

        # Create the report object
        filename = u"{}.pdf".format(coa_num)
        import pdb; pdb.set_trace()
        report = api.create(
                parent, "BatchInvoice",
                title=coa_num,
                batch=api.get_uid(parent),
                containedbatcheinvoices=uids,
                client=parent.getClient().UID(),
                subtotal=kwargs.get("total_subtotal"),
                vat=kwargs.get("total_VAT"),
                total=kwargs.get("total_amount"),
                )
        report.invoice_pdf = NamedBlobFile(data=pdf, contentType='application/pdf',filename=filename)
            # Html=html,
            # CSV=csv_text,
            # Metadata=metadata)
        transaction.commit()
        logger.info("Create Report for {} [DONE]".format(parent_id))

        return report
