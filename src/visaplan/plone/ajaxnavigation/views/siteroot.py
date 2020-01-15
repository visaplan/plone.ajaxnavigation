# -*- coding: utf-8 -*-

from __future__ import absolute_import
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from visaplan.plone.tools.decorators import returns_json


class SiteInfoView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @returns_json
    def __call__(self):
        context = aq_inner(self.context)
        portal_state = context.restrictedTraverse('@@plone_portal_state')
        navroot = portal_state.navigation_root_url()
        return {
            'site_url': navroot,
            }
