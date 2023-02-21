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

from Products.CMFPlone.utils import _createObjectByType
from senaite.core.workflow import SAMPLE_WORKFLOW
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

from bika.lims import api
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IAnalysisRequestSecondary
from bika.lims.interfaces import IReceived
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import (
    to_services_uids,
    apply_hidden_services,
    do_rejection,
    resolve_rejection_reasons)
from bika.lims.workflow import doActionFor
from bika.lims.workflow.analysisrequest import do_action_to_analyses


def create_analysisrequest(client, request, values, analyses=None,
                           results_ranges=None, prices=None):
    """Creates a new AnalysisRequest (a Sample) object
    :param client: The container where the Sample will be created
    :param request: The current Http Request object
    :param values: A dict, with keys as AnalaysisRequest's schema field names
    :param analyses: List of Services or Analyses (brains, objects, UIDs,
        keywords). Extends the list from values["Analyses"]
    :param results_ranges: List of Results Ranges. Extends the results ranges
        from the Specification object defined in values["Specification"]
    :param prices: Mapping of AnalysisService UID -> price. If not set, prices
        are read from the associated analysis service.
    """
    # Don't pollute the dict param passed in
    values = dict(values.items())

    # Resolve the Service uids of analyses to be added in the Sample. Values
    # passed-in might contain Profiles and also values that are not uids. Also,
    # additional analyses can be passed-in through either values or services
    service_uids = to_services_uids(values=values, services=analyses)

    # Remove the Analyses from values. We will add them manually
    values.update({"Analyses": []})

    # Create the Analysis Request and submit the form
    ar = _createObjectByType('AnalysisRequest', client, tmpID())
    ar.processForm(REQUEST=request, values=values)

    # Set the analyses manually
    ar.setAnalyses(service_uids, prices=prices, specs=results_ranges)

    # Handle hidden analyses from template and profiles
    # https://github.com/senaite/senaite.core/issues/1437
    # https://github.com/senaite/senaite.core/issues/1326
    apply_hidden_services(ar)

    # Handle rejection reasons
    rejection_reasons = resolve_rejection_reasons(values)
    ar.setRejectionReasons(rejection_reasons)

    # Handle secondary Analysis Request
    primary = ar.getPrimaryAnalysisRequest()
    if primary:
        # Mark the secondary with the `IAnalysisRequestSecondary` interface
        alsoProvides(ar, IAnalysisRequestSecondary)

        # Rename the secondary according to the ID server setup
        renameAfterCreation(ar)

        # Set dates to match with those from the primary
        ar.setDateSampled(primary.getDateSampled())
        ar.setSamplingDate(primary.getSamplingDate())
        ar.setDateReceived(primary.getDateReceived())

        # Force the transition of the secondary to received and set the
        # description/comment in the transition accordingly.
        if primary.getDateReceived():
            primary_id = primary.getId()
            comment = "Auto-received. Secondary Sample of {}".format(primary_id)
            changeWorkflowState(ar, SAMPLE_WORKFLOW, "sample_received",
                                action="receive", comments=comment)

            # Mark the secondary as received
            alsoProvides(ar, IReceived)

            # Initialize analyses
            do_action_to_analyses(ar, "initialize")

            # Notify the ar has ben modified
            modified(ar)

            # Reindex the AR
            ar.reindexObject()

            # If rejection reasons have been set, reject automatically
            if rejection_reasons:
                do_rejection(ar)

            # In "received" state already
            return ar

    # Try first with to_be_invoiced transition, cause it is the most common config
    setup = api.get_setup()
    schema = setup.Schema()
    financials = schema['Financials'].getAccessor(setup)()
    invfor = schema['InvoiceForPublishedSamplesOnly'].getAccessor(setup)()
    if financials and not invfor:
        success, message = doActionFor(ar, "to_be_invoiced")
    elif financials and invfor:
        success, message = doActionFor(ar, "no_sampling_workflow")
    if not success:
        doActionFor(ar, "to_be_sampled")

    # If rejection reasons have been set, reject the sample automatically
    if rejection_reasons:
        do_rejection(ar)

    return ar
