# -*- coding: utf-8 -*-
from __future__ import absolute_import

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from Acquisition import aq_inner

from visaplan.plone.tools.decorators import returns_json

from visaplan.plone.ajaxnavigation.views import AjaxnavBaseBrowserView
from visaplan.plone.ajaxnavigation.views import SchemaAwareBrowserView
from visaplan.plone.ajaxnavigation.utils import embed_view_name

DEFAULT_FOLDER_EMBED = embed_view_name('folder_listing')  # folder_listing_embed
from visaplan.tools.debug import trace_this


class AjaxnavBrowserView(AjaxnavBaseBrowserView):

    def views_to_try(self, context):
        """
        For folders: call getLayout, and replace the final _view by _embed

        Will be called after checking the View permission;
        if missing, the 'please_login' or 'insufficient_rights' view names
        are used (as returned by the please_login_viewname and
        insufficient_rights_viewname methods, respectively).
        """
        cls = self.__class__
        dp_view = getMultiAdapter((context, self.request),
                                  name='default_page')
        page_id = dp_view.getDefaultPage()
        if page_id:
            yield (page_id, 'embed')

        layout = context.getLayout()
        if layout:
            view = embed_view_name(layout)
            if view:
                yield view
        yield DEFAULT_FOLDER_EMBED

    # __call__ = trace_this(AjaxnavBaseBrowserView.__call__)


class EmbedBrowserView(SchemaAwareBrowserView):

    def children(self, context=None, **kwargs):
        """
        Stand-alone view method to return a list of the folder's children

        All optional arguments (save the context) must be given by name!

        acquire_inner -- use aq_inner, default: True
        use_context_state -- use the plone_context_state, currently:
                             for the object titles;
                             default: True
        include_objects -- include the objects in an addtional 'o' value;
                           default: 'href' and 'title' only

        For unknown keyword arguments a TypeError is raised.
        """

        request = kwargs.pop('request', None)
        acquire_inner     = kwargs.pop('acquire_inner',     True)
        use_context_state = kwargs.pop('use_context_state', True)
        include_objects   = kwargs.pop('include_objects',   False)
        if kwargs:
            raise TypeError('Surplus keyword arguments: %s'
                    % (list(kwargs.keys()),
                       ))
        if context is None:
            context = self.context
        if acquire_inner:
            context = aq_inner(context)
        if use_context_state:
            # we need the request in this case, right?
            if request is None:
                request = self.request
        root = context.absolute_url() + '/'
        children = []
        # no contentFilter for now:
        for o in context.listFolderContents():
            o_id = o.id
            href = root + o_id
            if use_context_state:
                state = getMultiAdapter((o, request),
                                        name='plone_context_state')
                title = state.object_title()
            else:
                title = o.title
            dic = {
                'href': href,
                'title': title,
                }
            if include_objects:
                dic['o'] = o
            children.append(dic)
        return children
