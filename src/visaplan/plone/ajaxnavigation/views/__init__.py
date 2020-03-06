# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from six import string_types as six_string_types
from six.moves.urllib.parse import urlsplit, urlunsplit, urljoin

from Globals import DevelopmentMode
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.interfaces import ComponentLookupError
# from Acquisition import aq_inner
from AccessControl.Permissions import view as view_permission
from plone.uuid.interfaces import IUUID
from logging import getLogger

from visaplan.plone.tools.decorators import returns_json
from visaplan.plone.ajaxnavigation.data import PERMISSION_ALIASES
from visaplan.plone.ajaxnavigation.data import CALLING_CONTEXT_KEY
from visaplan.plone.ajaxnavigation.utils import view_choice_tuple
from visaplan.plone.ajaxnavigation.utils import embed_view_name
from visaplan.plone.ajaxnavigation.utils import pop_ajaxnav_vars

from visaplan.plone.ajaxnavigation.views.helpers import _get_tool_1
from visaplan.plone.ajaxnavigation import ToolNotFound, TemplateNotFound, _

from pdb import set_trace
logger = getLogger('visaplan.plone.ajaxnavigation:views')
from visaplan.tools.debug import pp

__all__ = [  # public interface:
        # for @@ajax-nav views (JSON):
        'AjaxnavBaseBrowserView',  # for @@ajax-nav views
        'NoAjaxBrowserView',       # ... not (yet) ready for AJAX
        # for @@embed and other content views (HTML):
        'AjaxLoadBrowserView',     # reuse full-page templates
        'SchemaAwareBrowserView',  # ... use schema data
        'PleaseLoginBrowserView',  # ... inject came_from and prompt for login
        'AccessDeniedBrowserView', # ... inject came_from and prompt for login
        'VoidBrowserView',         # ... empty result (None)
        # MarginInfoBaseBrowserView  (nothing interesting yet)
        ]


class AjaxLoadBrowserView(BrowserView):
    """
    An ordinary BrowserView which simply injects ajax_load=1 into the request.

    Allows to re-use normal full-page templates for AJAX requests;
    you simply need to adjust your main_template.pt (or whatever)
    and decide which page parts you want to let go through.
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        request.set('ajax_load', 1)

    def _interesting_request_vars(self, context, request):
        print(('URL0:                 %s' % (request['URL0'],)))
        print(('BASE0:                %s' % (request['BASE0'],)))
        print(('ACTUAL_URL:           %s' % (request['ACTUAL_URL'],)))
        print(('VIRTUAL_URL_PARTS[1]: %s' % (request['VIRTUAL_URL_PARTS'][1],)))


class AjaxnavBaseBrowserView(AjaxLoadBrowserView):  # [ AjaxnavBaseBV ... [
    """
    BrowserView for @@ajax-nav views:
    these override the __call__ method to return a JSON "object"
    """

    def __init__(self, context, request):
        AjaxLoadBrowserView.__init__(self, context, request)
        # XXX: This might not be early enough,
        #      e.g. for views including batch navigation:
        self._data, self._other = pop_ajaxnav_vars(request.form)
        # for developer information:
        self._view_names_tried = []

    # ------------- [ choose the view for the 'context' JSON key ... [
    def views_to_try(self, context):
        """
        Override this method to inject special views.

        The yielded values can be simply strings representing view names
        (like 'embed'), or 2-tuples (page_id, view_name), where page_id
        may be None; see ..utils.view_choice_tuple().
        """
        request = self.request
        given_viewname = request.get('_viewname') or None
        # if a viewname was extracted from clientside code, we try this first:
        if given_viewname:
            yield embed_view_name(given_viewname)
            yield given_viewname

        layout = context.getLayout()
        if layout:
            view = embed_view_name(layout)
            if view:
                yield view
            yield layout
        yield 'embed'
        yield 'view'

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
        for val in self.views_to_try(context):
            tup = view_choice_tuple(val)
            self._view_names_tried.append(tup)
            if tup in tried:
                continue
            tried.append(tup)
            page_id, view_name = tup
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
                the_view = _get_tool_1(view_name, context)
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

    # ---------------------------------- [ construct JSON object ... [
    def get_replacement_content(self, context, request, title=None):
        """
        Return a dict which is used of the __call__ method (below)
        in case the context can't be accessed
        """
        # pm = getToolByName(context, 'portal_membership')
        pm = _get_tool_1('portal_membership', context)
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
    def response_additions(self):
        """
        For subclassing: e.g. inject a '@prefered-selectors' dict into the AJAX
        response (see .update_response below)
        """
        return None

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
                keys_updated.update(list(changes.keys()))

        for key, val in collected_changes.items():
            if key in keys_in and key not in keys_updated:
                logger.warn('%(context)r.update_response: '
                            'Changes for key %(key)r ignored '
                            ' (%(val)r)',
                            locals())
                continue
            thedict[key] = val

    # ------------------------------ ] ... construct JSON object ... [
    @returns_json
    def __call__(self):
        """
        Return JSON data for AJAX navigation.

        Return "nothing" if no appropriate (normally: @@embed) view is available.
        Return False if no URL is given.
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

        # state = context.restrictedTraverse('@@plone_context_state')
        # state = getToolByName(context, 'plone_context_state')
        state = _get_tool_1('plone_context_state', context)
        visible_url = request.get('_original_url') or None
        if visible_url is None:
            logger.warn('No _original_url; using context!')
            visible_url = context.absolute_url() + '/',
        elif isinstance(visible_url, six_string_types):
            logger.info('visible_url (from Request) is %(visible_url)r', locals())
        else:
            logger.error('visible_url (from Request) is %(visible_url)r (STRING expected!)',
                         locals())
            if isinstance(visible_url, (list, tuple)):
                tmp = set([url for url in set(visible_url) if url])
                if len(tmp) == 1:
                    visible_url = list(tmp)[0]
            else:
                visible_url = 0
            if not visible_url:
                visible_url = context.absolute_url() + '/',
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
        # pm = getToolByName(context, 'portal_membership')
        pm = _get_tool_1('portal_membership', context)
        can_view = pm.checkPermission(view_permission, context)
        the_view = None
        if can_view:
            the_view = self.choose_view(context)
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
            try:
                pp((('context', context),
                    ('view_name:', view_name),
                    ('zcml_name:', self.__name__),
                    ('res (so far):', res),
                    'POSSIBLE RECURSION?!',
                    ))
                # set_trace()
                content = the_view()
            except UnicodeDecodeError as e:
                logger.error(e)
                logger.info('NOCHMAL MIT DEBUGGER!')
                # set_trace()
                try:
                    content = the_view()
                except Exception as e:
                    logger.error(e)
                    logger.exception(e)
                    logger.info('... NOCHMAL MIT DEBUGGER!')
                    res.update({
                        '@noajax': True,
                        'content': None,
                        })
                else:
                    res.update({
                        'content': content,
                        })
                    self.update_response(res)
            except Exception as e:
                logger.error(e)
                logger.exception(e)
                pp(e=e)
                # set_trace()
                res.update({
                    '@noajax': True,
                    'content': None,
                    })
            else:
                res.update({
                    'content': content,
                    })
                self.update_response(res)
        return res
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
    # -------------------------------- ] ... class AjaxnavBaseBrowserView ]


class NoAjaxBrowserView(BrowserView):
    """
    Use this BrowserView class for cases where AJAX loading won't work (currently, at least),
    and you'd rather deliver a (slower) full-page view than a faulty AJAX version
    """
    @returns_json
    def __call__(self, *args, **kwargs):
        return {
            '@noajax': True,
            'content': None,
            }

class SchemaAwareBrowserView(AjaxLoadBrowserView):  # [ SchemaAwareBV ... [
    """
    Multipurpose base class for @@embed views
    """
    # auszulesen von der perm-Methode:
    interesting_permissions = [
            'edit',  # e.g. to display a pencil
            ]

    def data(self, **kwargs):
        res = self.basedata()
        res.update(self.schemadata(**kwargs))
        return res

    # ----------------------------- [ Bausteine für data() ... [
    def basedata(self):
        context = self.context
        logger.info('basedata(%(context)r)', locals())
        return {
            'UUID': IUUID(context, None),
            'portal_type': context.portal_type,
            }

    # ------------------ [ SchemaAwareBrowserView.schemadata() ... [
    def schemadata_kwargs(self, accept_unused=False, **kwargs):
        """
        Resolve the keyword arguments to the schemadata method
        and return a dict.

        Keyword options:

        fields -- a whitelist of field names to use
        omit_fields -- a blacklist of field names.

        Of course, only one of both can be specified;
        if none is given, the default is an empty blacklist, i.e. return all.

        By default, unknown options are not accepted.
        To add more options in your own derived class, inject
        accept_unused=True in the kwargs, call this method, and then
        resolve the remaining options in your own method.
        """
        fields = kwargs.pop('fields', [])
        if fields:
            omit_fields = kwargs.pop('omit_fields', None)
            if omit_fields:
                raise TypeError('If fields are given, omit_fields must be empty!'
                                ' (fields=%(fields)r, omit_fields=%(omit_fields)r)'
                                % locals())
            if isinstance(fields, six_string_types):
                fields = set([fields])
            elif isinstance(fields, set):
                pass
            else:
                fields = set(fields)
        else:
            fields = set()
            omit_fields = kwargs.pop('omit_fields', None) or set()
            if omit_fields is None:
                pass
            elif isinstance(omit_fields, six_string_types):
                omit_fields = set([omit_fields])
            elif isinstance(omit_fields, set):
                pass
            else:
                omit_fields = set(omit_fields)

        accept_unused = kwargs.get('accept_unused', None)
        if not accept_unused:
            keys = set(kwargs.keys())
            keys.discard('accept_unused')
            if keys:
                keys = sorted(keys)
                raise TypeError('unknown kwarg(s): %(keys)s'
                                ', accept_unused: %(accept_unused)r'
                                % locals())

        return {
            'fields':      fields,
            'omit_fields': omit_fields,
            }

    def schemadata(self, **kwargs):
        """
        Returns the complete schema data, with possible adjustments.

        For the possible keyword options, see the schemadata_kwargs method.
        """
        context = self.context
        logger.info('schemadata(%(context)r)', locals())

        resolved_kw = self.schemadata_kwargs(**kwargs)

        # schemadata method is the final consumer of accept_unused:
        accept_unused = kwargs.pop('accept_unused', False)
        if kwargs and not accept_unused:
            raise TypeError('Unused kwarg(s)! (%s)'
                            % ', '.join(list(kwargs.keys())))

        fields =      resolved_kw.pop('fields')
        omit_fields = resolved_kw.pop('omit_fields')

        use_blacklist = bool(omit_fields)
        use_whitelist = not use_blacklist and bool(fields)

        assert not resolved_kw, (
                'Not all resolved arguments extracted (%(resolved_kw)r)'
                % locals())

        schema = context.Schema()
        keys = list(schema.keys())
        res = {}
        for key in keys:
            if use_blacklist and key in omit_fields:
                continue
            elif use_whitelist and key not in fields:
                continue
            field = context.getField(key)
            if field is not None:
                val = field.get(context)
                res[key] = val

        return res
    # ------------------ ] ... SchemaAwareBrowserView.schemadata() ]
    # ----------------------------- ] ... Bausteine für data() ]

    def perm(self):
        """
        Return
        Queries all "interesting" permissions, i.e.:
        permissions which are used *in* a view template.
        """
        res = {}
        context = self.context
        checkperm = getToolByName(context, 'portal_membership').checkPermission
        for alias in self.interesting_permissions:
            perm = PERMISSION_ALIASES[alias]
            if perm not in res:
                res[perm] = checkperm(perm, context)
            if alias != perm:
                res[alias] = res[perm]
        return res

    # ---------- [ "checking permission checker" ... [
    perm_checker_verbose = True
    def perm_checker(self, verbose=None):
        """
        Return a function which checks any permission for the calling context;
        be aware that you are responsible for the correct spelling yourself.

        Usage in template (Python expressions):

        view.perm_checker()('permission string')

        or to check more than one permission, create the checker first, and
        then call it:

        tal:define="check_perm python:view.perm_checker();
                    may_edit   python:check_perm('Modify portal content')"

        """
        context = self.context
        checkperm = getToolByName(context, 'portal_membership').checkPermission
        if verbose is None:
            verbose = self.perm_checker_verbose
        if verbose:
            known_perms = self.known_permission_strings()
            cls = self.__class__
            def check_verbose(perm):
                if perm not in known_perms:
                    logger.warn('%(cls)s:perm_checker():'
                                ' Unknown permission %(perm)r',
                                {'cls': cls,
                                 'perm': perm,
                                 })
                return checkperm(perm, context)
            return check_verbose
        else:
            def check_simple(perm):
                return checkperm(perm, context)
            return check_simple

    def known_permission_strings(self):
        return frozenset(list(PERMISSION_ALIASES.values()))
    # ---------- ] ... "checking permission checker" ]
    # ---------------------------------- ] ... class SchemaAwareBrowserView ]


TAIL = '@@ajax-nav'
TAIL_LEN = len(TAIL)
class PleaseLoginBrowserView(AjaxLoadBrowserView):

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
