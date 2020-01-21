# -*- coding: utf-8 -*-
from __future__ import absolute_import

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from visaplan.plone.tools.decorators import returns_json
from plone.api.portal import get_navigation_root


class SiteInfoView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @returns_json
    def __call__(self):
        context = aq_inner(self.context)
        navroot = get_navigation_root(context).absolute_url()
        return {
            'site_url': navroot,
            }
