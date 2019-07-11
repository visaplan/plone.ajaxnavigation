# -*- coding: utf-8 -*-
from visaplan.plone.ajaxnavigation.testing import VISAPLAN_PLONE_AJAXNAVIGATION_FUNCTIONAL_TESTING
from visaplan.plone.ajaxnavigation.testing import VISAPLAN_PLONE_AJAXNAVIGATION_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest

from visaplan.plone.ajaxnavigation.interfaces import (
	IAjaxNavigationClientSettings, IAjaxNavigationInternalSettings,
	)

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

registry = getUtility(IRegistry)


class ViewsIntegrationTest(unittest.TestCase):

    layer = VISAPLAN_PLONE_AJAXNAVIGATION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Collection', 'my-collection')

    def test_registry_client_view_ids(self):
        """ client-side settings contain 'view_ids'
        """
	settings = registry.forInterface(IAjaxNavigationClientSettings, check=False)
        keys = settings.keys()
        self.assertTrue(
            'view_ids' in settings,
            'view_ids key not found in client-side settings'
            ' (keys: %(keys)r)'
            % locals())
        val = settings['view_ids']
        self.assertTrue(
            isinstance(val, list),
            'view_ids value %(val)r is not a list' % locals())

    def test_registry_internal_selectors(self):
        """ "internal" settings contain 'selectors'
        """
	settings = registry.forInterface(IAjaxNavigationInternalSettings, check=False)
        keys = settings.keys()
        self.assertTrue(
            'selectors' in settings,
            'selectors key not found in internal settings'
            ' (keys: %(keys)r)'
            % locals())
        val = settings['view_ids']
        self.assertTrue(
            isinstance(val, dict),
            'view_ids value %(val)r is not a dict' % locals())


class ViewsFunctionalTest(unittest.TestCase):

    layer = VISAPLAN_PLONE_AJAXNAVIGATION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
