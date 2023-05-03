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
from ._base import AjaxnavBrowserView as _Base
from ._schema import SchemaAwareBrowserView
from visaplan.plone.ajaxnavigation.utils import embed_view_name

DEFAULT_FOLDER_EMBED = embed_view_name('folder_listing')  # folder_listing_embed

# Logging / Debugging:
from visaplan.tools.debug import trace_this

__all__ = [
        'AjaxnavBrowserView',
        # 'EmbedBrowserView',  # we'll try to get along without ..._embed views
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


# class EmbedBrowserView(SchemaAwareBrowserView):
# deleted, because not used anymore, and identical to the version from
#  ../../../../../../visaplan.plone.base/src/visaplan/plone/base/views/folder.py
