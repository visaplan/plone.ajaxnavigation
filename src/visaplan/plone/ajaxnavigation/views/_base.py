# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import, print_function

from six import string_types as six_string_types

# Setup tools:
import pkg_resources

# Standard library:
from posixpath import sep

# Zope:
# from Acquisition import aq_inner
from AccessControl import Unauthorized
from AccessControl.Permissions import view as view_permission
from Globals import DevelopmentMode
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.component.interfaces import ComponentLookupError

# visaplan:
from visaplan.plone.tools.decorators import returns_json

# Local imports:
from visaplan.plone.ajaxnavigation import _
from visaplan.plone.ajaxnavigation.data import CALLING_CONTEXT_KEY
from visaplan.plone.ajaxnavigation.exceptions import ToolNotFound
from visaplan.plone.ajaxnavigation.utils import (
    embed_view_name,
    view_choice_tuple,
    )
from visaplan.plone.ajaxnavigation.views.helpers import _get_tool_1

# Logging / Debugging:
from logging import getLogger

logger = getLogger('visaplan.plone.ajaxnavigation:views._base')
# Local imports:
from ._load import AjaxLoadBrowserView

# Logging / Debugging:
from pdb import set_trace
from visaplan.tools.debug import pp


class AjaxnavBrowserView(AjaxLoadBrowserView): # [ AjaxnavBrowserView ... [
    """
    BrowserView for @@ajax-nav views:
    these override the __call__ method to return a JSON "object"
    """

    def __init__(self, context, request):
        try:
            AjaxLoadBrowserView.__init__(self, context, request)
        except TypeError as e:
            logger.error('AjaxnavBrowserView(): %(e)r', locals())
            logger.exception(e)
            if DevelopmentMode and 0:
                print('*** NOCHMAL, MIT DEBUGGER:')
                set_trace()
                AjaxLoadBrowserView.__init__(self, context, request)
                print('*** WIEDER ZURUECK')
            else:
                raise
        # for developer information:
        self._view_names_tried = []

    # ------------- [ choose the view for the 'context' JSON key ... [
    # ------------------------------------ [ views_to_try() ... [
    def views_to_try(self, context, viewname=None, **kwargs):
        """
        Override this method to inject special views.

        The yielded values can be simply strings representing view names
        (like 'embed'), or 2-tuples (object_or_id, view_name), where object_or_id
        may be None; see ..utils.view_choice_tuple().

        Note: additional keyword arguments are accepted but currently ignored
              (they might be used by other methods)
        """
        request = self.request
        if viewname is None:
            viewname = self.get_given_viewname() or 0
        # if a viewname was extracted from clientside code, we try this first:
        if viewname:
            yield embed_view_name(viewname)
            yield viewname

        if kwargs:
            logger.info('Ignoring keyword arguments %s',
                        ', '.join(kwargs.keys()))

        try:
            layout = context.getLayout()
        except AttributeError as e:
            cls = self.__class__.__name__
            logger.error('%(cls)s.views_to_try: '
                         '%(context)r lacks a getLayout attribute', locals())
            logger.exception(e)
        else:
            if layout:
                view = embed_view_name(layout)
                if view:
                    yield view
                yield layout
        # last resort:
        yield 'embed'
        yield 'view'
        # -------------------------------- ] ... views_to_try() ]

    def _iterate_viewnames(self, context, **kwargs):
        """
        Try the given or - usually - generated view names
        and return the first existing view
        """
        if 'names' in kwargs:
            names = kwargs.pop('names')
        else:
            # pp(locals(), 'woher kommt ..._embed?')
            names = self.views_to_try(context, **kwargs)
            logger.info('names=%(names)r', locals())
        tried = []
        tried_names = self._view_names_tried
        request = self.request
        for val in names:
            tup = view_choice_tuple(val)
            object_or_id, view_name = tup
            tried_names.append(view_name)
            if tup in tried:
                continue
            tried.append(tup)

            if object_or_id is None:
                o = context
            elif isinstance(object_or_id, six_string_types):
                o = context.restrictedTraverse(object_or_id)
                if not o:
                    continue
            else:  # e.g. folder.AjaxnavBrowserView.views_to_try looks for
                   # default pages and yields them, since it has sought them:
                o = object_or_id
            try:
                the_view = queryMultiAdapter((o, request),
                                             name=view_name)
            except ComponentLookupError as e:
                logger.error('%(e)r looking for %(view_name)r (%(context)r)',
                             locals())
            else:
                if the_view:
                    return the_view
                # continue
                # necessary to use e.g. mainpage_embed from skin layer;
                # @@mainpage_embed *didn't* work:
                try:
                    the_view = _get_tool_1(view_name, o, request)
                except ToolNotFound:
                    logger.error('%(context)r: view %(view_name)r not found!',
                                 locals())
                    continue
                else:
                    if the_view:
                        return the_view
        cls = self.__class__
        if tried:
            logger.error('%(context)r, %(cls)r: no appropriate view found; '
                         'tried %(tried)s', locals())
        else:
            logger.error('%(context)r, %(cls)r: no view names!',
                         locals())
        return None

    # ------------------------------------- [ choose_view() ... [
    def choose_view(self, *args, **kwargs):
        """
        This method is called *after* performing the View permission check;
        see as well the please_login_viewname and insufficient_rights_viewname
        methods which are used alternatively.

        There shouldn't be normally the need to override this method;
        instead, override --> views_to_try.
        """
        # we used to expect `context` as a mandatory argument,
        # which was a bad idea ...
        if 'context' in kwargs:
            context = kwargs.pop('context')
        elif args:
            context = args.pop(0)
        else:
            context = self.context
        if args:
            raise TypeError('no (further) positional arguments allowed!')
        return self._choose_view(context, **kwargs)

    # ------------------------------- [ _choose_view() ... [
    def _choose_view(self, context, **kwargs):
        """
        Working horse for choose_view ...

        Keyword arguments:

        - can_view -- if False, we simply return None.
                      Note: This methoed doesn't perform permission checks!
        """
        if not kwargs.get('can_view', 1):
            return None
        the_view = self._iterate_viewnames(context, **kwargs)
        if the_view is not None:
            return the_view
        return None
    # ------------------------------- ] ... _choose_view() ]
    # ------------------------------------- ] ... choose_view() ]
    # ------------- ] ... choose the view for the 'context' JSON key ]

    # ---------------------------------- [ construct JSON object ... [
    def get_replacement_content(self, context, request, title=None):
        """
        Return a dict which is used by the __call__ method (below)
        in case the context can't be accessed
        """
        pm = getToolByName(context, 'portal_membership')
        if pm.isAnonymousUser():
            view_name = self.please_login_viewname()
            title =     self.please_login_title(title)
        else:
            view_name = self.insufficient_rights_viewname()
            title =     self.insufficient_rights_title(title)
        self._interesting_request_vars(context, request)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        the_view = queryMultiAdapter((portal, request),
                                     name=view_name)
        if the_view is None:
            logger.error('%(portal)r: view %(view_name)r not found!', locals())
            return {
                '@noajax': True,
                'content': None,
                }
        try:
            request.set(CALLING_CONTEXT_KEY, context)
            content = the_view()
            return {
                '@noajax': False,
                '@title': title,
                'content': content,
                }
        except Exception as e:
            logger.error('Calling %(view_name)r on %(portal)r --> exception %(e)r', locals())
            self._interesting_request_vars(context, request)
            if DevelopmentMode and 0:
                print('*** NOCHMAL, MIT DEBUGGER:')
                set_trace()
                content = the_view(portal, request)
                print('*** WIEDER ZURUECK; content:')
                print(content)
            print('*** ES HATTE GEKNALLT! ALSO:')
            raise

    # ------------------------------ ] ... construct JSON object ... [
    def shortcircuit_noajax(self, context, request):
        """
        Detect situations which are not yet handled nicely

        ... but try to handle them first!
        """
        form = request.form
        pp(form=form)
        changes = 0
        ok = True
        for key, val in form.items():
            if isinstance(val, list):
                if key.startswith('b_'):
                    logger.warn('%(context)r: key %(key)r has value %(val)r',
                                locals())
                    newval = val[-1]
                    form[key] = newval
                    changes += 1
                    logger.warn('%(context)r: key %(key)r set to    %(newval)r',
                                locals())
                elif key == 'uid':
                    same_set = set(val)
                    if len(same_set) == 1:
                        form[key] = val[0]
                        changes += 1
                    else:
                        ok = False
        if changes:
            pp('%(changes)d changes:' % locals(),
               form=form)
        return not ok

    # ------------------------------ ] ... construct JSON object ... [
    def update_response(self, thedict):
        """
        Apply the changes provided by .response_additions.

        Options:

        - update (default: False)
          If true, simply use the .update method and silently override
          existing keys

        This method collects the .response_additions of all inherited classes,
        after the following strategy:

        - the "most far away" classes are tried first, since their results may
          be overridden (dict.update())
        - keys already present in the given result dictionary are only updated
          if the result is a 2-tuple,
          and the 2nd value is a dict {'update': True}.
        """
        classes = list(type(self).mro())
        classes.reverse()
        collected_changes = {}
        keys_in = set(thedict.keys())
        keys_updated = set()

        for cls in classes:
            mod = cls.__module__
            response_additions = getattr(cls, 'response_additions', None)
            if response_additions is None:
                continue
            changes = response_additions(self)
            if changes is None:
                continue
            if isinstance(changes, dict):
                kwargs = {}
            else:  # can be a 2-tuple
                changes, kwargs = changes
            pop = kwargs.pop
            update = pop('update', False)
            if kwargs:  # error!
                invalid = tuple(kwargs.keys())
                mod = cls.__module__
                context = self.context
                raise TypeError('Unknown keyword arguments '
                                'in result of %(cls)r.response_additions'
                                ' (%(mod)r; context: %(context)r)'
                                '! %(invalid)s'
                                % locals())
            collected_changes.update(changes)
            if update:
                keys_updated.update(changes.keys())  # noqa

        for key, val in collected_changes.items():
            if key in keys_in and key not in keys_updated:
                logger.warn('%(context)r.update_response: '
                            'Changes for key %(key)r ignored '
                            ' (%(val)r)',
                            locals())
                continue
            thedict[key] = val

    # ------------------------------ ] ... construct JSON object ... [

    # ------------------------------------- [ _usual_data() ... [
    def _usual_data(self):
        """
        Return the data (still a Python dictionary)
        usually returned by the __call__ method
        """
        # context = aq_inner(self.context)
        context = self.context
        request = self.request
        MYNAME = 'ajax-nav'
        assert MYNAME == self.__name__
        if self.shortcircuit_noajax(context, request):
            return {
                '@noajax': True,
                }

        state = getMultiAdapter((context, request),
                                name='plone_context_state')
        visible_url = self.get_visible_url(context, request)
        res = {
            '@title': state.object_title(),
            # for history (like for incoming external links):
            '@url': visible_url,
            }
        self._res = res
        if DevelopmentMode:
            res['@devel-info'] = {
                'tried-views': self._view_names_tried,
                }
        pm = getToolByName(context, 'portal_membership')
        can_view = pm.checkPermission(view_permission, context)
        the_view = self.choose_view(can_view=can_view)
        if the_view is not None:
            view_name = None
        else:
            res.update(self.get_replacement_content(context, request))
            return res

        if view_name == MYNAME:
            res.update({
                '@noajax': True,
                })
            return res

        if (the_view is None
            and view_name is not None
            and view_name != MYNAME):
          try:
            the_view = queryMultiAdapter((context, request),
                                         name=view_name)
          except ComponentLookupError as e:
            logger.error('%(e)r looking for %(view_name)r (%(context)r)',
                         locals())
            logger.exception(e)
            raise

        if the_view is None:
            logger.error('%(context)r: view %(view_name)r not found!',
                         locals())
            res.update({
                '@noajax': True,
                'content': None,
                })
            return res
        else:
            content = None
            try:
                pp((('context', context),
                    ('view_name:', view_name),
                    ('the_view:', the_view),
                    ('zcml_name:', self.__name__),
                    ('res (so far):', res),
                    ))
                content = the_view()
            except Unauthorized as e:
                res.update(self.get_replacement_content(context, request))
                self.update_response(res)
                return res
            except UnicodeDecodeError as e:
                logger.error(e)
                if DevelopmentMode and 0:
                    logger.info('NOCHMAL MIT DEBUGGER!')
                    set_trace()
                    try:
                        content = the_view()
                    except Exception as e:
                        logger.error(e)
                        logger.exception(e)
                        res.update({
                            '@noajax': True,
                            })
                    finally:
                        logger.info('... NOCHMAL MIT DEBUGGER!')
                else:
                    res.update({
                        '@noajax': True,
                        })
            except Exception as e:
                logger.error(e)
                logger.exception(e)
                if DevelopmentMode:
                    if 0:  # don't reactivate UNLESS FOCUSING on this problem!
                        pp(e=e)
                        logger.info('NOCHMAL MIT DEBUGGER!')
                        set_trace()
                        content = the_view()
                        logger.info('... NOCHMAL MIT DEBUGGER!')
                    else:
                        logger.info('NOCHMAL MIT DEBUGGER: DISABLED!')
                else:
                    res.update({
                        '@noajax': True,
                        })
            res.update({
                'content': content,
                })
            self.update_response(res)
        return res
    # ------------------------------------- ] ... _usual_data() ]

    @returns_json
    def __call__(self):
        """
        Return JSON data for AJAX navigation.

        Return "nothing" if no appropriate (normally: @@embed) view is available.
        Return False if no URL is given.
        """
        return self._usual_data()

    @classmethod
    def _data_complete(cls, res):
        """
        Override helper:
        By default, the __call__ method simply returns the result provided by
        the _usual_data method.

        You might want to extend this; in rare cases
        beyond the possibilities of the update_response method
        (which collects and executes response_additions).

        This method allows you to decide whether the so-far calculated result
        is complete, and to do some more processing otherwise.
        """
        return 1 if (res.get('@noajax') or
                     res.get('content')
                     ) else 0
    # ---------------------------------- ] ... construct JSON object ]

    def please_login_viewname(self):
        return 'please_login'

    def please_login_title(self, title):
        if title is None:
            return _('Please login')
        return _('Please login: ${title}',
                 mapping=locals())

    def insufficient_rights_viewname(self):
        return 'insufficient_rights'

    def insufficient_rights_title(self, title):
        if title is None:
            return _('Access denied')
        return _('Access denied: ${title}',
                 mapping=locals())
    # ------------------------------------ ] ... class AjaxnavBrowserView ]
