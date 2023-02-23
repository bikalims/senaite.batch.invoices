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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.


from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.batchfolder import BatchFolderContentsView as BFCV


class BatchFolderContentsView(BFCV):
    """Listing view for Batches
    """

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)

        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        if finacials:
            invoiced = {"id": "invoiced",
                        "title": _("Invoiced"),
                        "columns": self.columns.keys(),
                        "contentFilter": {"batch_invoiced_state": "invoiced"}
                        }
            to_be_invoiced = {"id": "uninvoiced",
                              "title": _("To be invoiced"),
                              "columns": self.columns.keys(),
                              "contentFilter": {"batch_invoiced_state": "uninvoiced"}
                              }
            self.review_states.append(invoiced)
            self.review_states.append(to_be_invoiced)
