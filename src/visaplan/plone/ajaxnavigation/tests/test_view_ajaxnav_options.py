# -*- coding: utf-8 -*-
from visaplan.plone.ajaxnavigation.testing import VISAPLAN_PLONE_AJAXNAVIGATION_FUNCTIONAL_TESTING
from visaplan.plone.ajaxnavigation.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Collection', 'my-collection')

    def test_ajaxnav_options_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='ajaxnav-options'
        )
        self.assertTrue(view(), 'ajaxnav-options is not found')
        self.assertTrue(
            'Sample View' in view(),
            'Sample View is not found in ajaxnav-options'
        )

    def test_ajaxnav_options_in_my_collection(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['my-collection'], self.portal.REQUEST),
                name='ajaxnav-options'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = VISAPLAN_PLONE_AJAXNAVIGATION_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
