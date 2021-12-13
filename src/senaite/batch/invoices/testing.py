# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import senaite.batch.invoices


class SenaiteBatchInvoicesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=senaite.batch.invoices)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'senaite.batch.invoices:default')


SENAITE_BATCH_INVOICES_FIXTURE = SenaiteBatchInvoicesLayer()


SENAITE_BATCH_INVOICES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(SENAITE_BATCH_INVOICES_FIXTURE,),
    name='SenaiteBatchInvoicesLayer:IntegrationTesting',
)


SENAITE_BATCH_INVOICES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SENAITE_BATCH_INVOICES_FIXTURE,),
    name='SenaiteBatchInvoicesLayer:FunctionalTesting',
)


SENAITE_BATCH_INVOICES_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        SENAITE_BATCH_INVOICES_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='SenaiteBatchInvoicesLayer:AcceptanceTesting',
)
