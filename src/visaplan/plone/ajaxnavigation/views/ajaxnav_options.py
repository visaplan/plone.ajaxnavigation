# -*- coding: utf-8 -*-
from __future__ import absolute_import

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from Globals import DevelopmentMode

from visaplan.plone.ajaxnavigation.interfaces import IAjaxNavigationSettings
from visaplan.plone.ajaxnavigation.data import clientside_map
from visaplan.plone.ajaxnavigation.utils import NoneOrBool
from visaplan.plone.tools.decorators import returns_json


class AjaxnavOptions(BrowserView):

    @returns_json
    def __call__(self):
        """
        Default options for AjaxNav

        (@@ajaxnav-options-default)
        """
        proxy = getToolByName(self.context, 'portal_registry')
        settings = proxy.forInterface(IAjaxNavigationSettings)
        res = {}
        for key, dotted in clientside_map.items():
            res[key] = proxy[dotted]

        key = 'development_mode'
        res[key] = False
        return res
        val = NoneOrBool(proxy.get(key, 'auto'))
        if val is None:
            val = bool(DevelopmentMode)
        res[key] = val
        return res
