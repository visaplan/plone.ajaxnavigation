# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import, print_function

from importlib_metadata import PackageNotFoundError
from importlib_metadata import version as pkg_version

# Standard library:
from posixpath import sep

# Zope:
from AccessControl.Permissions import view as view_permission
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.component.interfaces import ComponentLookupError

# Plone:
from plone.uuid.interfaces import IUUID

# visaplan:
from visaplan.plone.tools.decorators import returns_json

# Local imports:
from visaplan.plone.ajaxnavigation.data import (
    CALLING_CONTEXT_KEY,
    PERMISSION_ALIASES,
    )
from visaplan.plone.ajaxnavigation.exceptions import TemplateNotFound
from visaplan.plone.ajaxnavigation.utils import (
    embed_view_name,
    parse_current_url,
    pop_ajaxnav_vars,
    view_choice_tuple,
    )
from visaplan.plone.ajaxnavigation.views.helpers import _get_tool_1

# Logging / Debugging:
from logging import getLogger

logger = getLogger('visaplan.plone.ajaxnavigation:views')
# Logging / Debugging:
from pdb import set_trace
from visaplan.tools.debug import pp

try:
    pkg_version('zope.deprecation')
except PackageNotFoundError:
    HAVE_DEPRECATION = False
else:
    HAVE_DEPRECATION = True
    from zope.deprecation import deprecated

# Local imports:
from ._base import AjaxnavBrowserView
from ._load import AjaxLoadBrowserView
from ._login import PleaseLoginBrowserView
from ._schema import SchemaAwareBrowserView

__all__ = [  # public interface:
        # for @@ajax-nav views (JSON):
        'AjaxnavBrowserView',  # for @@ajax-nav views
        'NoAjaxBrowserView',       # ... not (yet) ready for AJAX
        # for @@embed and other content views (HTML):
        'AjaxLoadBrowserView',     # reuse full-page templates
        'SchemaAwareBrowserView',  # ... use schema data
        'PleaseLoginBrowserView',  # ... inject came_from and prompt for login
        'AccessDeniedBrowserView', # ... inject came_from and prompt for login
        'VoidBrowserView',         # ... empty result (None)
        # MarginInfoBaseBrowserView  (nothing interesting yet)
        ]

if HAVE_DEPRECATION:
    AjaxnavBaseBrowserView = AjaxnavBrowserView
    deprecated(AjaxnavBaseBrowserView,
               'was renamed to AjaxnavBrowserView')
    __all__.append('AjaxnavBaseBrowserView')


class NoAjaxBrowserView(AjaxnavBrowserView):
    """
    Use this BrowserView class for cases where AJAX loading won't work (currently, at least),
    and you'd rather deliver a (slower) full-page view than a faulty AJAX version
    """
    @returns_json
    def __call__(self, *args, **kwargs):
        context = self.context
        request = self.request

        pm = getToolByName(context, 'portal_membership')
        can_view = pm.checkPermission(view_permission, context)
        if can_view:
            # view permitted, but (sorry) no AJAX yet:
            return {
                '@noajax': True,
                'content': None,
                }

        state = getMultiAdapter((context, request),
                                name='plone_context_state')
        title = state.object_title()
        visible_url = self.get_visible_url(context, request)
        res = {
            # for history (like for incoming external links):
            '@url': visible_url,
            }

        if pm.isAnonymousUser():
            view_name = self.please_login_viewname()
            title =     self.please_login_title(title)
        else:
            view_name = self.insufficient_rights_viewname()
            title =     self.insufficient_rights_title(title)
        the_view = queryMultiAdapter((context, request),
                                     name=view_name)
        if the_view is None:
            logger.error('%(context)r: view %(view_name)r not found!', locals())
            res.update({
                '@noajax': True,
                })
            return res

        content = the_view()
        res.update({
            'content': content,
            '@title': title,
            })
        return res


class AccessDeniedBrowserView(AjaxLoadBrowserView):

    def __call__(self):
        context = self.context
        the_view = context.restrictedTraverse('insufficient_privileges')
        if the_view is None:
            raise TemplateNotFound('insufficient_privileges')
        return the_view()


class VoidBrowserView(BrowserView):
    """
    A trivial BrowserView which will simply return None;
    typically this is used as a default (to avoid errors)
    while not-None BrowserViews are mapped to certain interfaces.
    """
    def __call__(self, *args, **kwargs):
        return None


class MarginInfoBaseBrowserView(BrowserView):
    """
    A place to add common requirements for BrowserViews
    which are used to feed @@margin-info views.

    For now, we see no reason to set ajax_load here,
    since this class is not intended to feed full page templates.
    """
