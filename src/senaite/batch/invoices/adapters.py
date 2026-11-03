# -*- coding: utf-8 -*-

from zope.component import adapter
from zope.interface import implementer

from senaite.core.interfaces import IIdServerVariables


@adapter(object)
@implementer(IIdServerVariables)
class IDServerGetVariables(object):

    def __init__(self, context):
        self.context = context

    def get_variables(context, **kw):
        """Prepares a dictionary of key->value pairs usable for ID formatting
        """
        parent = kw.get("container")
        if hasattr(parent, "getClientID"):
            variables = {
                "clientId": parent.getClientID(),
            }
            return variables
        return {}
