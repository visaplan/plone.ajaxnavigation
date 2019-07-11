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


class ViewsIntegrationTest(unittest.TestCase):

    layer = VISAPLAN_PLONE_AJAXNAVIGATION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Collection', 'my-collection')

    def test_registry_client_view_ids(self):
        """ client-side settings contain 'view_ids'
        """
        proxy = self.registry  #.forInterface(IAjaxNavigationClientSettings, check=False)
        val = proxy['visaplan.plone.ajaxnavigation.view_id']
        self.assertTrue(
            isinstance(val, list),
            'view_ids value %(val)r is not a list' % locals())

    def test_registry_internal_selectors(self):
        """ "internal" settings contain 'selectors'
        """
        proxy = self.registry  #.forInterface(IAjaxNavigationInternalSettings, check=False)
        val = proxy['visaplan.plone.ajaxnavigation.selectors']
        self.assertTrue(
            isinstance(val, dict),
            'selectors value %(val)r is not a dict' % locals())


class ViewsFunctionalTest(unittest.TestCase):

    layer = VISAPLAN_PLONE_AJAXNAVIGATION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
