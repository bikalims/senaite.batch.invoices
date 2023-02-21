# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.browser.client.views.analysisrequests import \
    ClientAnalysisRequestsView as CARV

from senaite.batch.invoices import _
from .batchfolder import BatchFolderContentsView


class ClientBatchesView(BatchFolderContentsView):

    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"
        self.contentFilter['getClientUID'] = self.context.UID()


class ClientAnalysisRequestsView(CARV):
    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        inv_pub = setup.Schema()['InvoiceForPublishedSamplesOnly'].getAccessor(setup)()
        if finacials and not inv_pub:
            invoiced = {"id": "invoiced",
                        "title": _("Invoiced"),
                        "columns": self.columns.keys(),
                        "contentFilter": {"review_state": "invoiced"}
                        }
            self.review_states.insert(1, invoiced)

            to_be_invoiced = {"id": "to_be_invoiced",
                              "title": _("To be invoiced"),
                              "columns": self.columns.keys(),
                              "contentFilter": {"review_state": "to_be_invoiced"}
                              }
            self.review_states.insert(1, to_be_invoiced)

        if finacials and inv_pub:
            invoiced = {"id": "invoiced",
                        "title": _("Invoiced"),
                        "columns": self.columns.keys(),
                        "contentFilter": {"review_state": "invoiced"}
                        }
            index = self.review_states.index([state  for state in self.review_states if state['id']=='published'][0])
            self.review_states.insert(1+index, invoiced)

            to_be_invoiced = {"id": "to_be_invoiced",
                              "title": _("To be invoiced"),
                              "columns": self.columns.keys(),
                              "contentFilter": {"review_state": "to_be_invoiced"}
                              }
            self.review_states.insert(1+index, to_be_invoiced)
