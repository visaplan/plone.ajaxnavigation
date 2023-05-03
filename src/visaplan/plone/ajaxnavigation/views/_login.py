# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import, print_function

from six.moves.urllib.parse import urlsplit, urlunsplit

from zope.component import getMultiAdapter
from ._load import AjaxLoadBrowserView

from visaplan.plone.ajaxnavigation.exceptions import TemplateNotFound

# Logging / Debugging:
from visaplan.tools.debug import pp

TAIL = '@@ajax-nav'
TAIL_LEN = len(TAIL)
class PleaseLoginBrowserView(AjaxLoadBrowserView):  # - [ PleaseLoginBV ... [

    def __init__(self, context, request):
        AjaxLoadBrowserView.__init__(self, context, request)
        self._interesting_request_vars(context, request)
        request.set('ajax_load', 1)
        self.set_came_from(context, request)

    def set_came_from(self, context, request):
        """
        We need a came_from value for the login_form;
        any host name component (netloc) is removed
        """
        came_from = request.get('came_from', '') or None
        if came_from is not None:
            came_from_parsed = urlsplit(came_from)
            came_from_list = list(came_from_parsed)
            if came_from_parsed.netloc:
                came_from_list[:2] = ['', '']
                request.set('came_from', urlunsplit(came_from_list))
            return

        val = request['ACTUAL_URL']
        val_parsed = urlsplit(val)
        val_list = list(val_parsed)
        val_list[:2] = ['', '']
        if val_parsed.path.endswith(TAIL):
            val_list[2] = val_list[2][:-TAIL_LEN]
        request.set('came_from', urlunsplit(val_list))

    def __call__(self):
        context = self.context
        request = self.request
        the_view = context.restrictedTraverse('login_form')
        if the_view is None:
            raise TemplateNotFound('login_form')
        return the_view()

    def data(self):
        context = self.context
        request = self.request
        state = getMultiAdapter((context, request),
                                name='plone_context_state')
        res = {
            'title': state.object_title(),
            # for history (like for incoming external links):
            'url': context.absolute_url() + '/',
            }
        pp((('res:', res),
            ))
        return res
    # ---------------------------------- ] ... class PleaseLoginBrowserView ]
