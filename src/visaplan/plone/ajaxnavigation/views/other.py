# -*- coding: utf-8 -*-

from __future__ import absolute_import
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from zExceptions import Redirect


class SiteInfoView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = aq_inner(self.context)
        portal_state = context.restrictedTraverse('@@plone_portal_state')
        navroot = portal_state.navigation_root_url()
        raise Redirect(navroot + '/@@ajax-siteinfo')
