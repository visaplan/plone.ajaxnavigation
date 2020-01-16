# -*- coding: utf-8 -*-
from __future__ import absolute_import

from Products.CMFCore.utils import getToolByName
from visaplan.plone.ajaxnavigation.views import AjaxnavBaseBrowserView as BrowserView
from zope.component import queryMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Acquisition import aq_inner
from AccessControl.Permissions import view as view_permission
from plone.uuid.interfaces import IUUID
from logging import getLogger

from visaplan.plone.tools.decorators import returns_json
from visaplan.plone.ajaxnavigation.data import PERMISSION_ALIASES
from visaplan.plone.ajaxnavigation.utils import view_choice_tuple
from visaplan.plone.ajaxnavigation.utils import embed_view_name
from visaplan.plone.ajaxnavigation.utils import pop_ajaxnav_vars


from pdb import set_trace
import six
logger = getLogger('visaplan.plone.ajaxnavigation:views')

__all__ = [  # public interface:
        'AjaxnavBaseBrowserView',  # for @@ajax-nav views
        # MarginInfoBaseBrowserView  (nothing interesting yet)
        ]


class AjaxnavBaseBrowserView(BrowserView):  # - [ AjaxnavBaseBV (dbg) ... [
    """
    BrowserView for @@ajax-nav views:
    these override the __call__ method to return a JSON "object"
    """

    # ------------- [ choose the view for the 'context' JSON key ... [
    def views_to_try(self, context):
        """
        Override this method to inject special views.

        The yielded values can be simply strings representing view names
        (like 'embed'), or 2-tuples (page_id, view_name), where page_id
        may be None; see ..utils.view_choice_tuple().
        """
        cls = self.__class__
        pp(('context:', context), ('cls:', cls), ('classname:', cls.__name__))
	set_trace()

        dp_view = queryMultiAdapter((context, self.request),
                                    name='default_page')
        if dp_view:
            page_id = dp_view.getDefaultPage()
            if page_id:
                yield (page_id, 'embed')
	else:
	    logger.devel('defaultpage adapter not available for %(context)r',
                         locals())
	

        layout = context.getLayout()
        pp(('layout:', layout))
        if layout:
            view = embed_view_name(layout)
            pp(('layout:', layout), ('view:', view))
            if view:
                yield view
        yield 'embed'

    # ----- [ choose the view for the 'context' JSON key (DEBUG) ... [
    def choose_view(self, context):
        """
        This method is called *after* performing the View permission check;
        see as well the please_login_viewname and insufficient_rights_viewname
        methods which are used alternatively.

        There shouldn't be normally the need to override this method;
        instead, override --> views_to_try.
        """
        tried = []
        cls = self.__class__
        request = self.request
        pp(('context:', context), ('cls:', cls), ('request:', request))
	pt = context.portal_type
	if pt not in AJAXNAV_WHITELIST:
            pp(('portal_type:', pt), ('AJAXNAV_WHITELIST:', AJAXNAV_WHITELIST))
            set_trace()
	
        for val in self.views_to_try(context):
            pp([('val:', val)])
            tup = view_choice_tuple(val)
            pp([('tried:', tried), ('tup:', tup)])
            if tup in tried:
                continue
            tried.append(tup)
            page_id, view_name = tup
            pp([('page_id:', page_id), ('view_name:', view_name)])
            if page_id is None:
                o = context
            else:
                o = context.restrictedTraverse(page_id)
                if not o:
                    continue
            try:
                the_view = queryMultiAdapter((context, self.request),
                                             name=view_name)
            except ComponentLookupError as e:
                logger.error('%(e)r looking for %(view_name)r (%(context)r)',
                             locals())
            else:
                if the_view:
                    return the_view
                # necessary to use e.g. mainpage_embed from skin layer;
                # @@mainpage_embed *didn't* work:
                the_view = context.restrictedTraverse(view_name)
                if the_view:
                    return the_view
                logger.error('%(context)r: view %(view_name)r not found!',
                             locals())
        cls = self.__class__
        if tried:
            logger.error('%(context)r, %(cls)r: no appropriate view found; '
                         'tried %(tried)s', locals())
        else:
            logger.error('%(context)r, %(cls)r: no view names!',
                         locals())
        return None
    # ------------- ] ... choose the view for the 'context' JSON key ]
    # ------------------------- ] ... class AjaxnavBaseBrowserView (dbg) ]
