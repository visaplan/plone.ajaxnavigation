# -*- coding: utf-8 -*-
from __future__ import absolute_import

from plone import api
from plone.app.testing import logout
from plone.registry.interfaces import IRegistry
from visaplan.plone.ajaxnavigation.config import PROJECTNAME
from visaplan.plone.ajaxnavigation.interfaces import IAjaxNavigationSettings
from visaplan.plone.ajaxnavigation.testing import INTEGRATION_TESTING
from zope.component import getUtility

import unittest


class ControlPanelTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.controlpanel = self.portal['portal_controlpanel']

    def test_controlpanel_has_view(self):
        view = api.content.get_view(u'ajaxnav-settings', self.portal, self.request)
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_is_protected(self):
        from AccessControl import Unauthorized
        logout()
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse('@@ajaxnav-settings')

    def test_controlpanel_installed(self):
        actions = [
            a.getAction(self)['id'] for a in self.controlpanel.listActions()]
        self.assertIn('ajaxnav', actions)

    def test_controlpanel_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

        actions = [
            a.getAction(self)['id'] for a in self.controlpanel.listActions()]
        self.assertNotIn('ajaxnav', actions)


class RegistryTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IAjaxNavigationSettings)

    # -------------------- [ settings for client-side processing ... [
    def test_whitelist_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'whitelist'))
       self.assertEqual(
           self.settings.whitelist, ['body'])

    def test_blacklist_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'blacklist'))
       self.assertEqual(
           self.settings.blacklist, [])

    def test_nested_blacklist_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'nested_blacklist'))
       self.assertFalse(
           self.settings.nested_blacklist)

    def test_view_ids_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'view_ids'))
       self.assertEqual(
           self.settings.view_ids,
           ['view',
            'edit',
            'base_edit',
            ])

    def test_view_prefixes_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'view_prefixes'))
       self.assertEqual(
           self.settings.view_prefixes,
           ['manage_',
            ])

    def test_view_suffixes_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'view_suffixes'))
       self.assertEqual(
           self.settings.view_suffixes,
           ['_view',
            ])

    def test_blacklist_view_ids_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'blacklist_view_ids'))
       self.assertEqual(
           self.settings.blacklist_view_ids,
           ['manage',
            'edit',
            'base_edit',
            'logout',
            ])

    def test_blacklist_view_prefixes_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'blacklist_view_prefixes'))
       self.assertEqual(
           self.settings.blacklist_view_prefixes,
           ['manage_',
            ])

    def test_blacklist_view_suffixes_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'blacklist_view_suffixes'))
       self.assertEqual(
           self.settings.blacklist_view_suffixes,
           ['_edit',
            ])

    def test_selectors_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'selectors'))
       self.assertEqual(
           self.settings.selectors,
           {'content': "#content",
            })

    # --------------------------------- [ @scrollto feature ... [
    def test_scrollto_default_selector_record_in_registry(self):
		self.assertTrue(hasattr(self.settings, 'scrollto_default_selector'))
        # By default, we don't scroll to the top of an element
        # but of the entire document, using window.scrollTo
		self.assertEqual(
			self.settings.scrollto_default_selector,
			None)

    def test_scrollto_default_deltay_record_in_registry(self):
		self.assertTrue(hasattr(self.settings, 'scrollto_default_deltay'))
		self.assertEqual(
			self.settings.scrollto_default_deltay,
			0)

    def test_scrollto_auto_key_record_in_registry(self):
		self.assertTrue(hasattr(self.settings, 'scrollto_auto_key'))
        # if the @scrollto value is '@auto' (default from scrollto_default_selector, see above),
        # we use the selector mapped (by the "selectors" setting, above)
        # to the key given here
		self.assertEqual(
			self.settings.scrollto_auto_key,
			'content')
    # --------------------------------- ] ... @scrollto feature ]
    # -------------------- ] ... settings for client-side processing ]

    # ----------------------- [ settings for internal processing ... [
    def test_layout4ajax_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'layout4ajax'))
       self.assertEqual(
           self.settings.layout4ajax,
           { # nothing yet ...
            })

    def test_view4ajax_record_in_registry(self):
       self.assertTrue(hasattr(self.settings, 'view4ajax'))
       self.assertEqual(
           self.settings.view4ajax,
           { # nothing yet ...
            })
    # ----------------------- ] ... settings for internal processing ]

    def test_records_removed_on_uninstall(self):
        qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=[PROJECTNAME])

        records = [
            IAjaxNavigationSettings.__identifier__ + '.whitelist',
            IAjaxNavigationSettings.__identifier__ + '.blacklist',
            IAjaxNavigationSettings.__identifier__ + '.nested_blacklist',
            IAjaxNavigationSettings.__identifier__ + '.view_ids',
            IAjaxNavigationSettings.__identifier__ + '.view_prefixes',
            IAjaxNavigationSettings.__identifier__ + '.view_suffixes',
            IAjaxNavigationSettings.__identifier__ + '.blacklist_view_ids',
            IAjaxNavigationSettings.__identifier__ + '.blacklist_view_prefixes',
            IAjaxNavigationSettings.__identifier__ + '.blacklist_view_suffixes',
            IAjaxNavigationSettings.__identifier__ + '.selectors',
            IAjaxNavigationSettings.__identifier__ + '.layout4ajax',
            IAjaxNavigationSettings.__identifier__ + '.view4ajax',
        ]

        for r in records:
            self.assertNotIn(r, self.registry)
