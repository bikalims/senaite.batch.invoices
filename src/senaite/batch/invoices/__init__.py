# -*- coding: utf-8 -*-
"""Init and utils."""
import logging
from zope.i18nmessageid import MessageFactory
PRODUCT_NAME = "senaite.batch.invoices"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)
logger = logging.getLogger(PRODUCT_NAME)


_ = MessageFactory('senaite.batch.invoices')
