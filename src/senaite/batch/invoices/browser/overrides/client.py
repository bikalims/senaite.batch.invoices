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
from bika.lims.utils import t
from bika.lims.utils import get_image
from bika.lims.browser.batchfolder import BatchFolderContentsView
from senaite.batch.invoices import _


class ClientBatchesView(BatchFolderContentsView):

    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"
        self.contentFilter['getClientUID'] = self.context.UID()
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        if finacials:
            invoiced = {"id": "invoiced",
                        "title": get_image("invoiced.png",
                                           title=t(_("Invoiced"))),
                        "columns": self.columns.keys(),
                        "contentFilter": {"batch_invoiced_state": "invoiced"}
                        }
            to_be_invoiced = {"id": "uninvoiced",
                              "title": get_image("uninvoiced.png",
                                                 title=t(_("To be invoiced"))),
                              "columns": self.columns.keys(),
                              "contentFilter": {"batch_invoiced_state": "uninvoiced"}
                              }
            self.review_states.append(to_be_invoiced)
            self.review_states.append(invoiced)
