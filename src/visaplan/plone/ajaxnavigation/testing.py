# -*- coding: utf-8 -*-
"""Setup testing infrastructure.

For Plone 5 we need to install plone.app.contenttypes.

Tile for collective.cover is only tested in Plone 4.3.
"""
from __future__ import absolute_import

import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', ImportWarning)

    from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
    # from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
    from plone.app.testing import FunctionalTesting
    from plone.app.testing import IntegrationTesting
    from plone.app.testing import PloneSandboxLayer
    from plone.testing import z2

import pkg_resources


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    from plone.app.testing import PLONE_FIXTURE
    HAS_DEXTERITY = False
else:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE as PLONE_FIXTURE
    HAS_DEXTERITY = True

try:
    pkg_resources.get_distribution('collective.cover')
except pkg_resources.DistributionNotFound:
    HAS_COVER = False
else:
    HAS_COVER = True


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        if HAS_COVER:
            import collective.cover
            self.loadZCML(package=collective.cover)

        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import visaplan.js.urlsplit
        self.loadZCML(package=visaplan.js.urlsplit)
        import visaplan.plone.ajaxnavigation
        self.loadZCML(package=visaplan.plone.ajaxnavigation)

    def setUpPloneSite(self, portal):
        if HAS_COVER:
            self.applyProfile(portal, 'collective.cover:default')

        self.applyProfile(portal, 'visaplan.js.urlsplit:default')
        self.applyProfile(portal, 'visaplan.plone.ajaxnavigation:default')


FIXTURE = Fixture()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='visaplan.plone.ajaxnavigation:Integration',
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='visaplan.plone.ajaxnavigation:Functional',
)


# VISAPLAN_PLONE_AJAXNAVIGATION_ACCEPTANCE_TESTING = FunctionalTesting(
#     bases=(
#         FIXTURE,
#         REMOTE_LIBRARY_BUNDLE_FIXTURE,
#         z2.ZSERVER_FIXTURE,
#     ),
#     name='visaplan.plone.ajaxnavigation:Acceptance',
# )
