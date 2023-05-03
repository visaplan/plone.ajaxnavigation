# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

# Zope:
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from zExceptions import Redirect
from zope.component import getMultiAdapter

__all__ = [
        'SiteInfoView',
        ]


class SiteInfoView(BrowserView):

    def __call__(self):
        # context = aq_inner(self.context)
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        navroot = portal_state.navigation_root_url()
        raise Redirect(navroot + '/@@ajax-siteinfo')
