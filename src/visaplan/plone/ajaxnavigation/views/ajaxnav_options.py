# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from visaplan.plone.ajaxnavigation.interfaces import IAjaxNavigationSettings
from visaplan.plone.ajaxnavigation.data import clientside_map
from visaplan.plone.ajaxnavigation.decorators import returns_json


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
        return res
