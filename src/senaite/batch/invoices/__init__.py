# -*- coding: utf-8 -*-
"""Init and utils."""
import logging
from zope.i18nmessageid import MessageFactory
from senaite.api import get_request
from senaite.batch.invoices.interfaces import ISenaiteBatchInvoicesLayer

PRODUCT_NAME = "senaite.batch.invoices"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)
logger = logging.getLogger(PRODUCT_NAME)


_ = MessageFactory('senaite.batch.invoices')


def is_installed():
    """Returns whether the product is installed or not"""
    request = get_request()
    return ISenaiteBatchInvoicesLayer.providedBy(request)
