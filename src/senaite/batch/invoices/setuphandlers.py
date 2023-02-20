# -*- coding: utf-8 -*-

from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

from bika.lims import api
from senaite.batch.invoices import PRODUCT_NAME
from senaite.batch.invoices import PROFILE_ID
from senaite.batch.invoices import logger
from senaite.core.setuphandlers import add_dexterity_items


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
    setup_id_formatting(portal)
    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


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
        ("batch_invoices",  # ID
         "Batch Invoices",  # Title
         "BatchInvoices"),  # FTI
    ]
    setup = api.get_setup()
    add_dexterity_items(portal, items)
    add_dexterity_items(setup, items)


def setup_handler(context):
    """Generic setup handler"""
    if context.readDataFile("{}.txt".format(PRODUCT_NAME)) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    # portal = context.getSite()

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))
