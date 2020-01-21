# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Acquisition import aq_inner
from AccessControl.Permissions import view as view_permission
from plone.uuid.interfaces import IUUID
from plone.outputfilters.browser.resolveuid import uuidToObject
from logging import getLogger

from visaplan.plone.tools.decorators import returns_json
from visaplan.plone.ajaxnavigation.data import PERMISSION_ALIASES
from visaplan.plone.ajaxnavigation.utils import view_choice_tuple
from visaplan.plone.ajaxnavigation.utils import embed_view_name
from visaplan.plone.ajaxnavigation.utils import pop_ajaxnav_vars
from visaplan.tools.sequences import sequence_slide
from visaplan.tools.sequences import inject_indexes
from visaplan.tools.debug import pp

try:
    from simplejson import dumps
except ImportError:
    from json import dumps

from pdb import set_trace
logger = getLogger('visaplan.plone.ajaxnavigation:views')

__all__ = [  # public interface:
        'AjaxnavBaseBrowserView',  # for @@ajax-nav views
        'SchemaAwareBrowserView',  # for @@embed views
        # MarginInfoBaseBrowserView  (nothing interesting yet)
        'PleaseLoginBrowserView',
        ]

# ------------------------------------------------------------ [ data ... [
UID_INDICATORS = set(['@@resolveuid', 'resolveuid',
                      '@@resolveUid', 'resolveUid',
                      ])
# ------------------------------------------------------------ ] ... data ]


class AjaxnavBaseBrowserView(BrowserView):  # ------- [ AjaxnavBaseBV ... [
    """
    BrowserView for @@ajax-nav views:
    these override the __call__ method to return a JSON "object"
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # XXX: This might not be early enough,
        #      e.g. for views including batch navigation:
        self._data, self._other = pop_ajaxnav_vars(request.form)
        try:
            path = list(request['TraversalRequestNameStack'])
        except KeyError:
            path = None
        else:
            path.reverse()
        self._subpath = path
        logger.info('%(context)r @@ajax-nav: subpath = %(path)r', locals())

    # ------------- [ choose the view for the 'context' JSON key ... [
    def views_to_try(self, context):
        """
        Override this method to inject special views.

        The yielded values can be simply strings representing view names
        (like 'embed'), or 2-tuples (page_id, view_name), where page_id
        may be None; see ..utils.view_choice_tuple().
        """
        cls = self.__class__
        dp_view = queryMultiAdapter((context, self.request),
                                    name='default_page')
        if dp_view is not None:
            page_id = dp_view.getDefaultPage()
            if page_id:
                yield (page_id, 'embed')

        layout = context.getLayout()
        if layout:
            view = embed_view_name(layout)
            if view:
                yield view
        yield 'embed'

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

    # ------------------------------------ [ resolve the subpath ... [ 
    def _resolve_subpath(self, **kwargs):
        """
        Analysiere den Subpfad (der auf /@@ajax-nav/ folgt und keinen
        Query-String enthält)

        Options:

        - allow_subpaths: whether further method calls (beyond UID resolution)
            are allowed to take further subpaths. Default is False, i.e.
            the method name, if given, must be in the very last slash-separated
            path segment.
            Specifying True might have unexpected consequences and is not yet
            supported.
        - absolute_paths: whether to resolve UUIDs to absolute paths. Default
            is True, i.e.
            '/some/subpath/@@resolveuid/abc123' will be entirely replaced by
            the path to the object given by the UUID "abc123".
            When False is specified, the '/some/subpath/' part will be
            preserved.
        """
        pop = kwargs.pop
        allow_subpaths = pop('allow_subpaths', 0)
        absolute_paths = pop('absolute_paths', 1)
        if kwargs:
            keys = tuple(kwargs.keys())
            raise TypeError('Unsupported keyword argument(s)! (%(keys)s)'
                            % locals())
        global UID_INDICATORS
        subpath = self._subpath
        if not subpath:
            return (self.context,
                    None,
                    )
        changes = []
        method_name = None
        
        for chunk, prev_i, current_i, next_i in inject_indexes(subpath):
            if chunk in UID_INDICATORS:
                if next_i is None:
                    pa = '/'.join(subpath)
                    raise ValueError('Invalid subpath %(pa)r: '
                            '%(chunk)r must be followed by a UID!'
                            % locals())
                uid = subpath[next_i]
                if not is_uid_shaped(uid, onerror='return'):
                    pa = '/'.join(subpath)
                    raise ValueError('Invalid subpath %(pa)r: '
                            'Invalid UID %(uid)r following %(chunk)r!'
                            % locals())

                # CHECKME: Klappt das für zugriffsbeschränkte Objekte? 
                o = uuidToObject(uid)
                if o is None:
                    raise ValueError('UUID %(uid)r not found!'
                            % locals())
                vup = o.virtual_url_path()
                changes.append((
                        'REPLACE',
                        (0 if prev_i is None
                              or absolute_paths
                         else current_i,
                         next_i+1),
                        vup,
                        ))
            elif chunk.startswith('@@'):
                method_name = chunk[2:]
                if not method_name:
                    pa = '/'.join(subpath)
                    raise ValueError('Invalid method specification in %(pa)r'
                                     ' (%(chunk)r)'
                                     % locals())
                changes.append((
                        'DELETE',
                        (current_i,
                         current_i + 1),  # next_i might/should be None
                        ))
                if next_i is not None and not allow_subpaths:
                    pa = '/'.join(subpath)
                    raise ValueError('%(pa)r: subpath after method speci'
                            'fication %(chunk)r is not allowed!'
                            % locals())
                
        if changes:
            changes.reverse()
            for tup in changes:
                action, indexes = tup[:2]
                i1, i2 = indexes
                if action == 'REPLACE':
                    subpath[i1:i2] = tup[2]
                elif action == 'DELETE':
                    del subpath[i1:i2]
                else:
                    raise ValueError('Invalid action %(action)r! (%(tup)r)'
                                     % locals())

        pp(subpath=subpath)
        set_trace()
        if method_name is not None:  # explicitly given (after @@)
            return (context.restrictedTraverse('/'.join(subpath)),
                    method_name,
                    )
        elif not subpath[-1]:
            # last chunk is empty --> no method specified 
            return (context.restrictedTraverse('/'.join(subpath[:-1])),
                    None,
                    )

        p1 = '/'.join(subpath)
        try:
            o2 = context.restrictedTraverse(p1)
            # the subpath doesn't contain a method name: 
            return (o2,
                    None,
                    )
        except Exception as e:
            logger.error('%(p1)r is not an object', locals())
            logger.exception(e)
            if subpath[1:]:
                # we have a 2nd shot:
                pass
            else:
                raise

        p2 = '/'.join(subpath[:-1])
        # the last chunk of the subpath is the method name: 
        return (
            context.restrictedTraverse(p2),
            subpath[-1],
            )
    # ------------------------------------ ] ... resolve the subpath ]

    # ---------------------------------- [ construct JSON object ... [
    def __call__(self):
        """
        Return JSON data for AJAX navigation.

        Return "nothing" if no appropriate (normally: @@embed) view is available.
        Return False if no URL is given.
        """
        set_trace()
        if self._subpath is not None:
            context, view = self._resolve_subpath()
        else:
            context = aq_inner(self.context)
        pt = context.portal_type
        pp(context=context, portal_type=pt)

        request = self.request
        form = request.form
        # set_trace()

        state = context.restrictedTraverse('@@plone_context_state')
        res = {
            '@title': state.object_title(),
            # for history (like for incoming external links):
            '@url': context.absolute_url() + '/',
            }
        pm = getToolByName(context, 'portal_membership')
        ok = pm.checkPermission(view_permission, context)
        the_view = None
        if ok:
            the_view = self.choose_view(context)
            view_name = None
        elif pm.isAnonymousUser():
            view_name = self.please_login_viewname()
        else:
            view_name = self.insufficient_rights_viewname()

        if the_view is None and view_name is not None:
          try:
            the_view = queryMultiAdapter((context, request),
                                         name=view_name)
          except ComponentLookupError as e:
            logger.error('%(e)r looking for %(view_name)r (%(context)r)',
                         locals())

        if the_view is None:
            logger.error('%(context)r: view %(view_name)r not found!',
                         locals())
            res.update({
                '@noajax': True,
                'content': None,
                })
        else:
            try:
                content = the_view()
            except UnicodeDecodeError as e:
                logger.error(e)
                logger.info('NOCHMAL MIT DEBUGGER!')
                set_trace()
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
            except Exception as e:
                logger.error(e)
                logger.exception(e)
                res.update({
                    '@noajax': True,
                    'content': None,
                    })
            else:
                res.update({
                    'content': content,
                    })
        # since the response of sub-page @@ajax-nav methods is expected to be
        # in JSON format already, we don't decorate this method but perform the
        # operations of the @returns_json wrapper ourselves:
        txt = dumps(res)
        setHeader = request.RESPONSE.setHeader
        setHeader('Content-Type', 'application/json; charset=utf-8')
        setHeader('Content-Length', len(txt))
        return txt
    # ---------------------------------- ] ... construct JSON object ]

    def please_login_viewname(self):
        return 'please_login'

    def insufficient_rights_viewname(self):
        return 'insufficient_rights'
    # -------------------------------- ] ... class AjaxnavBaseBrowserView ]


class SchemaAwareBrowserView(BrowserView):  # - [ class SchemaAwareBV ... [
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
        context = aq_inner(self.context)
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
            if isinstance(fields, six.string_types):
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
            elif isinstance(omit_fields, six.string_types):
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
        context = aq_inner(self.context)
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
        context = aq_inner(self.context)
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
        context = aq_inner(self.context)
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


class PleaseLoginBrowserView(AjaxnavBaseBrowserView):
    pass


class MarginInfoBaseBrowserView(BrowserView):
    """
    A place to add common requirements for BrowserViews
    which are used to feed @@margin-info views
    """
