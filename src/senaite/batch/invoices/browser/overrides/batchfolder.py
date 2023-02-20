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

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.batchfolder import BatchFolderContentsView as BFCV
from senaite.core.catalog import SENAITE_CATALOG


class BatchFolderContentsView(BFCV):
    """Listing view for Batches
    """

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)

        self.catalog = SENAITE_CATALOG
        self.contentFilter = {
            "portal_type": "Batch",
            "sort_on": "created",
            "sort_order": "descending",
            "is_active": True,
        }

        self.title = self.context.translate(_("Batches"))
        self.description = ""

        self.show_select_column = True
        self.form_id = "batches"
        self.context_actions = {}
        self.icon = "{}{}".format(self.portal_url, "/senaite_theme/icon/batch")

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "title", }),
            ("Progress", {
                "title": _("Progress"),
                "index": "getProgress",
                "sortable": True,
                "toggle": True}),
            ("BatchID", {
                "title": _("Batch ID"),
                "index": "getId", }),
            ("Description", {
                "title": _("Description"),
                "sortable": False, }),
            ("BatchDate", {
                "title": _("Date"), }),
            ("Client", {
                "title": _("Client"),
                "index": "getClientTitle", }),
            ("ClientID", {
                "title": _("Client ID"),
                "index": "getClientID", }),
            ("ClientBatchID", {
                "title": _("Client Batch ID"),
                "index": "getClientBatchID", }),
            ("state_title", {
                "title": _("State"),
                "sortable": False, }),
            ("created", {
                "title": _("Created"),
                "index": "created",
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "contentFilter": {"review_state": "open"},
                "title": _("Open"),
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "closed",
                "contentFilter": {"review_state": "closed"},
                "title": _("Closed"),
                "transitions": [],
                "columns": self.columns.keys(),
            }, {
                "id": "cancelled",
                "title": _("Cancelled"),
                "transitions": [],
                "contentFilter": {"is_active": False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "transitions": [],
                "columns": self.columns.keys(),
            },
        ]
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        if finacials:
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
