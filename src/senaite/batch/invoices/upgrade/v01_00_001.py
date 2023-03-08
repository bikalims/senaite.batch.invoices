# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.QUEUE.
#
# SENAITE.QUEUE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
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
# Copyright 2019-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.catalog import SAMPLE_CATALOG, SENAITE_CATALOG
from senaite.batch.invoices import PRODUCT_NAME
from senaite.batch.invoices import PROFILE_ID
from senaite.batch.invoices import logger
from senaite.batch.invoices.setuphandlers import add_dexterity_setup_items
from senaite.batch.invoices.setuphandlers import setup_catalogs
from senaite.batch.invoices.setuphandlers import remove_batch_invoice_action

from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "1.0.1"


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    setup.runImportStepFromProfile(PROFILE_ID, "typeinfo")
    setup.runImportStepFromProfile(PROFILE_ID, "workflow")
    setup.runImportStepFromProfile(PROFILE_ID, "plone.app.registry")
    add_dexterity_setup_items(portal)
    setup_catalogs(portal)
    add_sample_invoiced_state(portal)
    add_batch_invoiced_state(portal)
    remove_batch_invoice_action(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def add_batch_invoiced_state(portal):
    logger.info("Fix Batches...")
    query = {
        "portal_type": "Batch",
    }
    batches = api.search(query, SENAITE_CATALOG)
    total = len(batches)
    for num, batch in enumerate(batches):
        if num and num % 10 == 0:
            logger.info("Processed batches: {}/{}".format(num, total))

        # Extract the parent(s) from this batch
        batch = api.get_object(batch)
        # Reindex both the partition and parent(s)
        if not hasattr(batch, 'batch_invoiced_state'):
            batch.reindexObject()
        else:
            if not batch.batch_invoiced_state:
                batch.reindexObject()


def add_sample_invoiced_state(portal):
    logger.info("Fix AnalysisRequests PrimaryAnalysisRequest ...")
    query = {
        "portal_type": "AnalysisRequest",
    }
    samples = api.search(query, SAMPLE_CATALOG)
    total = len(samples)
    for num, sample in enumerate(samples):
        if num and num % 10 == 0:
            logger.info("Processed samples: {}/{}".format(num, total))

        # Extract the parent(s) from this sample
        sample = api.get_object(sample)
        batch = sample.getBatch()
        if not batch:
            # Not in a batch Processed already
            continue
        # Reindex both the partition and parent(s)
        if not hasattr(sample, 'invoiced_state'):
            sample.reindexObject()
        else:
            if not sample.invoiced_state:
                sample.reindexObject()
