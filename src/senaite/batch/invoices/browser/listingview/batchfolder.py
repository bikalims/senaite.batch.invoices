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


from bika.lims.api.security import check_permission

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import t
from bika.lims.utils import get_image
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.batch.invoices import _
from senaite.batch.invoices import is_installed


class BatchFolderViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def update(self):
        """Before template render hook
        """
        import pdb; pdb.set_trace()
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        can_view = True  # check_permission(ModifyPortalContent, self.context)
        if is_installed and finacials and can_view:
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
            self.listing.review_states.append(invoiced)
            self.listing.review_states.append(to_be_invoiced)


    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        super(BatchFolderViewAdapter, self).update(obj, item, index)
        return item
