# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

# Zope:
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

# visaplan:
from visaplan.plone.tools.decorators import returns_json
from visaplan.tools.minifuncs import check_kwargs

# Local imports:
from visaplan.plone.ajaxnavigation.utils import embed_view_name
from ._schema import SchemaAwareBrowserView
from ._base import AjaxnavBrowserView as _Base

DEFAULT_FOLDER_EMBED = embed_view_name('folder_listing')  # folder_listing_embed
# Logging / Debugging:
from visaplan.tools.debug import trace_this

__all__ = [
        'AjaxnavBrowserView',
        # 'EmbedBrowserView', @embed for IFolderish is currently commented-out
        ]


class AjaxnavBrowserView(_Base):

    base__views_to_try = _Base.views_to_try

    def views_to_try(self, context, viewname=None, **kwargs):
        """
        For folders: call getLayout, and replace the final _view by _embed

        Will be called after checking the View permission;
        if missing, the 'please_login' or 'insufficient_rights' view names
        are used (as returned by the please_login_viewname and
        insufficient_rights_viewname methods, respectively).

        Note: additional keyword arguments are accepted but currently ignored
              (they might be used by other methods)
        """
        # from pdb import set_trace; set_trace()
        if viewname is None:
            viewname = self.get_given_viewname() or 0

        # for folders, we check the default_page first
        # and use its layout:
        dp_view = getMultiAdapter((context, self.request),
                                  name='default_page')
        page_id = dp_view.getDefaultPage()
        if page_id:
            the_page = context.restrictedTraverse(page_id)
            if the_page:
                for vn in self.base__views_to_try(the_page, viewname, **kwargs):
                    # since we have resolved the page_id,
                    # we should yield it:
                    yield (the_page, vn)

        # if no default page configured or not found,
        # continue standard processing:
        for tup in self.base__views_to_try(context, viewname, **kwargs):
            yield tup

        yield DEFAULT_FOLDER_EMBED

    # __call__ = trace_this(_Base.__call__)


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
        check_kwargs(kwargs)  # raises TypeError, if necessary
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
