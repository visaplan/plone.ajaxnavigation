# -*- coding: utf-8 -*-
import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', ImportWarning)

    # from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
    from plone.app.testing import applyProfile
    from plone.app.testing import FunctionalTesting
    from plone.app.testing import IntegrationTesting
    from plone.app.testing import PLONE_FIXTURE
    from plone.app.testing import PloneSandboxLayer
    from plone.testing import z2

import visaplan.plone.ajaxnavigation


class VisaplanPloneAjaxnavigationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import visaplan.js.urlsplit
        self.loadZCML(package=visaplan.js.urlsplit)
        self.loadZCML(package=visaplan.plone.ajaxnavigation)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'visaplan.js.urlsplit:default')
        applyProfile(portal, 'visaplan.plone.ajaxnavigation:default')


VISAPLAN_PLONE_AJAXNAVIGATION_FIXTURE = VisaplanPloneAjaxnavigationLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(VISAPLAN_PLONE_AJAXNAVIGATION_FIXTURE,),
    name='VisaplanPloneAjaxnavigationLayer:IntegrationTesting',
)


VISAPLAN_PLONE_AJAXNAVIGATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(VISAPLAN_PLONE_AJAXNAVIGATION_FIXTURE,),
    name='VisaplanPloneAjaxnavigationLayer:FunctionalTesting',
)


# VISAPLAN_PLONE_AJAXNAVIGATION_ACCEPTANCE_TESTING = FunctionalTesting(
#     bases=(
#         VISAPLAN_PLONE_AJAXNAVIGATION_FIXTURE,
#         REMOTE_LIBRARY_BUNDLE_FIXTURE,
#         z2.ZSERVER_FIXTURE,
#     ),
#     name='VisaplanPloneAjaxnavigationLayer:AcceptanceTesting',
# )
