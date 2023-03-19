# -*- coding: utf-8 -*-

from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

from bika.lims import api
from senaite.batch.invoices import PRODUCT_NAME
from senaite.batch.invoices import PROFILE_ID
from senaite.batch.invoices import logger
from senaite.core.setuphandlers import add_dexterity_items, setup_other_catalogs
from senaite.core.catalog import SAMPLE_CATALOG, SENAITE_CATALOG

# Tuples of (catalog, index_name, index_attribute, index_type)
INDEXES = [
    (SAMPLE_CATALOG, "invoiced_state", "", "FieldIndex"),
    (SENAITE_CATALOG, "batch_invoiced_state", "", "FieldIndex"),
    ("portal_catalog", "client", "", "FieldIndex"),
]

# Tuples of (catalog, column_name)
COLUMNS = [
    (SAMPLE_CATALOG, "invoiced_state"),
    (SENAITE_CATALOG, "batch_invoiced_state"),
    ("portal_catalog", "client"),
]

ID_FORMATTING = [
    # An array of dicts. Each dict represents an ID formatting configuration
    {
        'portal_type': 'BatchInvoice',
        'form': 'Inv-{seq:05d}',
        'sequence_type': 'generated',
        'split_length': 1
    },
]


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'senaite.batch.invoices:uninstall',
        ]


def post_install(portal_setup):
    """Post install script"""
    # Do something at the end of the installation of this package.
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)
    portal = context.getSite()  # noqa

    add_dexterity_setup_items(portal)
    setup_catalogs(portal)
    setup_id_formatting(portal)
    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def setup_catalogs(portal):
    """Setup catalogs"""
    setup_other_catalogs(portal, indexes=INDEXES, columns=COLUMNS)


def setup_id_formatting(portal, format=None):
    """Setup default ID Formatting for sampleimporter content types
    """
    if not format:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING:
            setup_id_formatting(portal, format=formatting)
        return

    bs = portal.bika_setup
    p_type = format.get("portal_type", None)
    if not p_type:
        return
    id_map = bs.getIDFormatting()
    id_format = filter(lambda id: id.get("portal_type", "") == p_type, id_map)
    if id_format:
        logger.info("ID Format for {} already set: '{}' [SKIP]"
                    .format(p_type, id_format[0]["form"]))
        return

    form = format.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in id_map:
        if record.get('portal_type', '') == p_type:
            continue
        ids.append(record)
    ids.append(format)
    bs.setIDFormatting(ids)


def add_dexterity_setup_items(portal):
    """Adds the Dexterity Container in the Setup Folder

    N.B.: We do this in code, because adding this as Generic Setup Profile in
          `profiles/default/structure` flushes the contents on every import.
    """
    # Tuples of ID, Title, FTI
    items = [
        ("batch_invoices", "Batch Invoices", "BatchInvoices"),
    ]
    setup = api.get_setup()
    # ##############ADD ITEMS IN PORTAL NAVIGATION#############
    add_dexterity_items(portal, items)
    # Move BatchInvoices after Methods nav item
    position = portal.getObjectPosition("methods")
    portal.moveObjectToPosition("batch_invoices", position + 1)
    ###########################################################

    # Reindex order
    portal.plone_utils.reindexOnReorder(portal)
    add_dexterity_items(setup, items)


def setup_handler(context):
    """Generic setup handler"""
    if context.readDataFile("{}.txt".format(PRODUCT_NAME)) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    # portal = context.getSite()

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))


def remove_batch_invoice_action(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Batch")

    # removed location listing
    actions = fti.listActions()
    for idx, action in enumerate(actions):
        if action.id == "invoice":
            fti.deleteActions(
                [
                    idx,
                ]
            )
