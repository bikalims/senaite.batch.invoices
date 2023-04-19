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

from zope.lifecycleevent import modified

from bika.lims import api
from bika.lims.utils.analysisrequest import create_analysisrequest as crar
from senaite.batch.invoices import is_installed


def create_analysisrequest(client, request, values, analyses=None,
                           results_ranges=None, prices=None):

    ar = crar(client, request, values, analyses=None,
              results_ranges=None, prices=None)
    if not is_installed:
        return ar

    setup = api.get_setup()
    schema = setup.Schema()
    financials = schema['Financials'].getAccessor(setup)()
    if financials:
        ar.invoiced_state = "uninvoiced"
        modified(ar)

    return ar
