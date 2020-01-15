# -*- coding: utf-8 -*-
from __future__ import absolute_import
from visaplan.plone.ajaxnavigation.testing import FUNCTIONAL_TESTING
from visaplan.plone.ajaxnavigation.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest

# very basic JSON used here, e.g. no Decimals:
from json import loads as json_loads


class ViewsIntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Collection', 'my-collection')

    def test_ajax_nav_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='ajax-nav'
        )
        result = view()
        self.assertTrue(result, 'ajax-nav yields a result')
        parsed = json_loads(result)

    def test_ajax_nav_in_my_collection(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['my-collection'], self.portal.REQUEST),
                name='ajax-nav'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
