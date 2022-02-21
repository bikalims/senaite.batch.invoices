# -*- coding: utf-8 -*-

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

    def store(self, pdf, html, uid, metadata=None, csv_text=None, coa_num=None):
        """Store the PDF

        :param pdf: generated PDF batchinvoice (binary)
        :param html: report HTML (string)
        :param csv: report CSV (string)
        :param uids: UIDs of the objects contained in the PDF
        :param metadata: dict of metadata to store
        """

        if metadata is None:
            metadata = {}

        # get the contained objects
        obj = api.get_object_by_uid(uid)

        report = self.create_report(
            obj, pdf, html, uid, metadata, csv_text=csv_text, coa_num=coa_num)

        return report

    @synchronized(max_connections=1)
    def create_report(self, parent, pdf, html, uid, metadata, csv_text=None, coa_num=None):
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
        report = api.create(parent, portal_type="BatchInvoice",
            **{"title":coa_num,
               "client": parent.getClient()})
        report.batch_invoice_pdf = NamedBlobFile(pdf, filename=filename)
            # Html=html,
            # CSV=csv_text,
            # Metadata=metadata)
        transaction.commit()
        logger.info("Create Report for {} [DONE]".format(parent_id))

        return report
