# -*- coding: utf-8 -*-
from __future__ import absolute_import

from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from visaplan.plone.tools.decorators import returns_json
from visaplan.plone.ajaxnavigation.data import CALLING_CONTEXT_KEY

from pdb import set_trace
from visaplan.tools.debug import pp


class SiteInfoView(BrowserView):

    @returns_json
    def __call__(self):
        # context = aq_inner(self.context)
        portal_state = getMultiAdapter((self.context, self.request),
                                       name='plone_portal_state')
        navroot = portal_state.navigation_root_url()
        return {
            'site_url': navroot,
            }


class PleaseLoginBrowserView(BrowserView):

    def data(self):
        assert self.__name__ == 'please_login'
        request = self.request
        context = request.get(CALLING_CONTEXT_KEY,  # <-- @@ajax-nav
                              self.context)         # (directly called)
        state = getMultiAdapter((context, request),
                                name='plone_context_state')
        res = {
            'title': state.object_title(),
            # for history (like for incoming external links):
            'url': context.absolute_url() + '/',
            }
        pp((('res:', res),
            ))
        # set_trace()
        return res


