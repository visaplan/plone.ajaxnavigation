# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from visaplan.plone.ajaxnavigation.decorators import returns_json
from zExceptions import Redirect


class SiteInfoView(BrowserView):

    @returns_json
    def __call__(self):
        context = aq_inner(self.context)
        portal_state = context.restrictedTraverse('@@plone_portal_state')
        navroot = portal_state.navigation_root_url()
        url = context.absolute_url()
        if url == navroot:
            return {
                'site_url': navroot,
                }
        else:
            raise Redirect(navroot + '/@@ajax-siteinfo')
