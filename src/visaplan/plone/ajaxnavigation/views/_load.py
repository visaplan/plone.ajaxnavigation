# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import, print_function

from six.moves.urllib.parse import urlsplit, urlunsplit

# Standard library:
from posixpath import sep

# Zope:
from Products.Five.browser import BrowserView

# Plone:
from plone.uuid.interfaces import IUUID

# Local imports:
from visaplan.plone.ajaxnavigation.utils import (
    parse_current_url,
    pop_ajaxnav_vars,
    )

# Logging / Debugging:
from logging import getLogger

logger = getLogger('visaplan.plone.ajaxnavigation:views')
# Logging / Debugging:
from visaplan.tools.debug import pp


class AjaxLoadBrowserView(BrowserView):
    """
    An ordinary BrowserView which simply injects ajax_load=1 into the request.

    Allows to re-use normal full-page templates for AJAX requests;
    you simply need to adjust your main_template.pt (or whatever)
    and decide which page parts you want to let go through.
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._data, self._other = pop_ajaxnav_vars(request.form)
        request.set('ajax_load', 1)

    # --------- [ information from ../resource/ajaxnavigation.js ... [
    def get_visible_url(self, context, request):
        """
        Return the (given and checked and/or calculated) visible URL

        *Always* use this method to get the value for the '@url' JSON key!
        """
        other = self._other
        url = other.get('original_url')
        if url:
            corrected_url = self.corrected_visible_url(url, context, request)
            if corrected_url is None:
                return url

            other['original_url'] = corrected_url
            return corrected_url
        return self._compute_visible_url(context, request)

    def corrected_visible_url(self, url, context=None, request=None):
        """
        Return a corrected URL, or None

        Fixes the following problems:

        - UUIDs (after [@@]resolve[uU]id, resolvei18n and the like)
          are resolved
        - UUID resolution methods which lack a following UID value
          are removed

        Errors are logged.
        """
        parsed, resinfo = parse_current_url(url)
        if not resinfo:  # everything is fine
            return None
        errors = resinfo.get('errors')
        if errors:
            logger.warn('corrected_visible_url(%r) found %d error(s):',
                        (url, len(errors),
                         ))
            for err in errors:
                logger.warn(err)

        uid = resinfo.pop('uid', None)
        if uid is not None:
            if context is None:
                context = self.context
            my_uid = IUUID(context, None)
            if my_uid != uid:
                logger.warn('corrected_visible_url(%(url)r): '
                            'found UID %(uid)r '
                            "doesn't match context UID %(my_uid)r"
                            ' %(context)r',
                            locals())
            my_url = context.absolute_url()
            my_path = urlsplit(my_url).path
            shortened_path = parsed[2]
            if shortened_path == sep:
                parsed[2] = my_path + shortened_path
            else:
                assert not shortened_path.startswith(sep), ('If a UID is '
                    'found (%(uid)r), the shortened path %(shortened_path)r '
                    'should *be* %(sep)r or not start with %(sep)r'
                    ) % locals()
                if sep not in shortened_path:
                    suspected_viewname = shortened_path
                    given_viewname = self.get_given_viewname()
                    if given_viewname is not None:
                        if given_viewname != suspected_viewname:
                            logger.warn('corrected_visible_url(%(url)r): '
                                        'URL suggests %(suspected_viewname)r '
                                        'but %(given_viewname)r was given!',
                                        locals())
                parsed[2] = sep.join((my_path, shortened_path))

        for key, val in resinfo.items():
            logger.warn('corrected_visible_url(%(url)r): %(key)s: %(val)r',
                        locals())

        # the path might e.g. have simply become normalized:
        new_url = urlunsplit(parsed)
        logger.info('corrected_visible_url(%(url)r) --> %(new_url)r',
                    locals())
        return new_url

    def get_given_viewname(self):
        """
        Return the given viewname or None
        """
        return self._other.get('viewname') or None

    def given_viewname(self, default=None):
        """
        Return the given viewname; if not yet present,
        and if a (trueish) default is given, set it.
        """
        other = self._other
        val = other.get('viewname')
        if val:
            return val
        elif default:
            other['viewname'] = default
            return default
        else:
            return default
    # --------- ] ... information from ../resource/ajaxnavigation.js ]

    def _compute_visible_url(self, context, request):
        """
        fallback method for cases of missing @original_url
        """
        if context is None:
            context = self.context
        url = context.absolute_url() + '/'
        view_name = self.get_given_viewname()
        if view_name:
            url += view_name
        # we don't do too much here; it's an emergency substitute after all!
        return url

    def _interesting_request_vars(self, context, request):
        pp('URL0:                 %s' % (request['URL0'],),
           'BASE0:                %s' % (request['BASE0'],),
           'ACTUAL_URL:           %s' % (request['ACTUAL_URL'],),
           'VIRTUAL_URL_PARTS[1]: %s' % (request['VIRTUAL_URL_PARTS'][1],),
           ('self._data: ', self._data),
           ('self._other:', self._other),
           )
