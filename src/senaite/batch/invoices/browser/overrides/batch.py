# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import ModifyPortalContent

from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.utils import t
from bika.lims.utils import get_image
from bika.lims.browser.batch.analysisrequests import \
    AnalysisRequestsView as ARV

from senaite.batch.invoices import _
from senaite.batch.invoices import is_installed


class AnalysisRequestsView(ARV):
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        setup = api.get_setup()
        finacials = setup.Schema()['Financials'].getAccessor(setup)()
        can_view = check_permission(ModifyPortalContent, context)
        if is_installed and finacials and can_view:
            invoiced = {"id": "invoiced",
                        "title": get_image("invoiced.png",
                                           title=t(_("Invoiced"))),
                        "columns": self.columns.keys(),
                        "contentFilter": {"invoiced_state": "invoiced"}
                        }

            uninvoiced = {"id": "uninvoiced",
                          "title": get_image("uninvoiced.png",
                                             title=t(_("To be invoiced"))),
                          "columns": self.columns.keys(),
                          "contentFilter": {"invoiced_state": "uninvoiced"},
                          }
            self.review_states.append(invoiced)
            self.review_states.append(uninvoiced)
