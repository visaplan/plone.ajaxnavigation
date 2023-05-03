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
from Globals import DevelopmentMode
from Products.CMFCore.utils import getToolByName

# Plone:
from plone.uuid.interfaces import IUUID

# Local imports:
from visaplan.plone.ajaxnavigation.data import PERMISSION_ALIASES

# Logging / Debugging:
from logging import getLogger

logger = getLogger('visaplan.plone.ajaxnavigation:views')
# Local imports:
from ._load import AjaxLoadBrowserView

# Logging / Debugging:
from pdb import set_trace
from visaplan.tools.debug import pp


class SchemaAwareBrowserView(AjaxLoadBrowserView):
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
                try:
                    val = field.get(context)
                except AttributeError as e:
                    logger.warn('Error %(e)s getting %(key)r value'
                                ' for %(context)r', locals())
                    if key in ('constrainTypesMode',
                               ):  # Known (but not yet understood ...)
                        res[key] = None
                        continue
                    elif DevelopmentMode and 0:
                        logger.error('context=%(context)r, field=%(field)r',
                                     locals())
                        pp(context=context, key=key, e=e, text='Nochmal mit Debugger!')
                        set_trace()
                        val = field.get(context)
                    else:
                        raise
                res[key] = val
            else:  # DEBUG
                logger.warn('%(context)r: field %(key)r is None', locals())

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
