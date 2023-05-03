# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import, print_function

from six import string_types as six_string_types
from six.moves.urllib.parse import urlsplit, urlunsplit

# Standard library:
from string import whitespace

WHITESPACE = frozenset(whitespace)

# Standard library:
from os import makedirs
from posixpath import join as path_join
from posixpath import normpath, sep
from time import strftime

# visaplan:
from visaplan.tools.minifuncs import check_kwargs
from visaplan.tools.sequences import inject_indexes

try:
    # visaplan:
    from visaplan.plone.tools.functions import is_uid_shaped
except ImportError:
    if __name__ == '__main__':
        def is_uid_shaped(s):
            return len(s) == 32 and set('0123456789abcdef').issuperset(s)
        print('Using simple is_uid_shaped replacement')
    else:
        raise

__all__ = [
        'embed_view_name',
        'view_choice_tuple',
        'dromedarCase',
        'pop_ajaxnav_vars',
        'strip_method_name',
        'strip_method_name_dammit',
        'parse_current_url',
        ]


def embed_view_name(viewname):
    """
    For a given view name <viewname>, construct a name of an "embed view"
    which is suitable to provide the "naked contents" of the object.

    A final 'view' "word" will be replaced by 'embed':

    >>> embed_view_name('view')
    'embed'
    >>> embed_view_name('folder_contents')
    'folder_contents_embed'

    This hypothetical view name ends with 'view', but this is not a word,
    so it is ignored:
    >>> embed_view_name('preview')
    'preview_embed'

    The divider ('_' preferred) will be preserved:

    >>> embed_view_name('folder_view')
    'folder_embed'
    >>> embed_view_name('folder-view')
    'folder-embed'

    If the argument is "false" (e.g. an empty string), None is returned:
    >>> embed_view_name('')

    If no 'view' suffix is found, we consider the divider(s) used.
    If only dashes are used, we use a dash:
    >>> embed_view_name('my-images')
    'my-images-embed'

    If none are found, or both, the underscore is used:
    >>> embed_view_name('my-cool_images')
    'my-cool_images_embed'
    >>> embed_view_name('dontknow')
    'dontknow_embed'
    """
    if viewname == 'view':  # shortcut; doesn't change the result
        return 'embed'
    elif not viewname:
        return None
    dividers = ('_', '-')
    used = []
    for divider in dividers:
        liz = viewname.split(divider)
        if liz[-1] == 'view':
            return divider.join(liz[:-1] + ['embed'])
        if liz[1:]:
            used.append(divider)
    if used:
        return used[0].join((viewname, 'embed'))
    return dividers[0].join((viewname, 'embed'))


def view_choice_tuple(val):
    """
    Take something which a views_to_try method might yield
    and return a (page_id, viewname) tuple.

    Folders might have a default page which should be used:
    >>> view_choice_tuple(('introduction', 'document_embed'))
    ('introduction', 'document_embed')

    In this case, the calling folder has an 'introduction' page which is
    considered its associated page, and we'll use the "layout" of this
    page (unless some other viewname was specified, of course).
    The choice (and transformation) of that view name is subject to the
    AjaxnavBrowserView.views_to_try method.

    For non-folders (which can't have a default_page mapped),
    we'll usually only get the name of a view;
    we'll inject None, representing the calling context, to get a 2-tuple:
    >>> view_choice_tuple('embed')
    (None, 'embed')
    """
    if isinstance(val, six_string_types):
        return (None, val)
    elif val[2:] or not val[1:]:
        raise ValueError('Please specify either a string '
                'or a (page_id, view_name) 2-tuple!'
                ' (%(val)r)' % locals())
    elif isinstance(val, tuple):
        return val
    else:
        return tuple(val)


def dromedarCase(s, offset=0, strict=True):
    """
    Convert a dashed variable name (like common for HTML5 "data-" attributes)
    to its dromedar-cased form.

    >>> dromedarCase('dashed-name')
    'dashedName'

    For conversion of "@data-" names we specify an offset of 6:

    >>> dromedarCase('@data-other-name', offset=6)
    'otherName'

    Preconverted names are not changed:

    >>> dromedarCase('preConverted')
    'preConverted'
    """
    res = []
    first = 1
    val = s[offset:]
    if strict:
        forbidden = WHITESPACE.intersection(s)
        if forbidden:
            forbidden = tuple(forbidden)
            raise ValueError('%(s)r contains whitespace %(forbidden)r'
                             % locals())
    if not val:
        if offset:
            raise ValueError('%(s)r: empty values (%(val)r) are disallowed!'
                             % locals())
        else:
            raise ValueError('%(s)r: empty values are disallowed!'
                             % locals())
    for chunk in val.split('-'):
        if not s:
            if strict:
                raise ValueError('double / leading / trailing dashes '
                        'are disallowed! (%(val)r)'
                        % locals())
            # otherwise simply ignore:
            continue
        if first:
            first = 0
        else:
            chunk = chunk[0].upper() + chunk[1:]
        res.append(chunk)
    if not res:
        raise ValueError('%(s)r lacks any non-dash characters!'
                         % locals())
    return ''.join(res)


SPECIAL_QV_PREFIX = '@'
DATA_PREFIX = SPECIAL_QV_PREFIX+'data-'
DATA_OFFSET = len(DATA_PREFIX)
def pop_ajaxnav_vars(dic, **kwargs):
    """
    Remove all vars from the request form data which might disturb standard
    Zope/Plone behaviour.
    Return a 2-tuple (data, other) of dictionaries.

    dic -- a dictionary, usually request.form

    Supported keyword arguments, for now:

    nocache -- remove an "_" argument as added by jQuery for "uncached" $.ajax
               requests; default: True

    >>> def pav(*args, **kwargs):
    ...     d, o = pop_ajaxnav_vars(*args, **kwargs)
    ...     return (sorted(d.items()), sorted(o.items()))
    >>> def testdata(**kwargs):
    ...     res = {'_': '123', '@original_url': 'https://somewhere.org/'}
    ...     res.update(kwargs)
    ...     return res

    Simple example:

    >>> tst1 = testdata()
    >>> sorted(tst1.items())
    [('@original_url', 'https://somewhere.org/'), ('_', '123')]
    >>> pav(tst1)
    ([], [('original_url', 'https://somewhere.org/')])

    The extracted vars have been removed "in-place" from the given dict:
    >>> sorted(tst1.items())
    []

    To avoid the removal of an '_' option, use nocache=False:

    >>> tst2 = testdata()
    >>> pav(tst2, nocache=False)
    ([], [('original_url', 'https://somewhere.org/')])
    >>> sorted(tst2.items())
    [('_', '123')]

    Another example with "data" and something which will be left alone:

    >>> tst3 = testdata(**{'@data-for': '#gaga', 'b_start': 'int:25'})
    >>> sorted(tst3.items())
    [('@data-for', '#gaga'), ('@original_url', 'https://somewhere.org/'), ('_', '123'), ('b_start', 'int:25')]
    >>> pav(tst3)
    ([('for', '#gaga')], [('original_url', 'https://somewhere.org/')])
    >>> sorted(tst3.items())
    [('b_start', 'int:25')]

    The 'ajax_load' variable is used by standard Plone (or used to be, at least),
    and thus is preserved in the original request dictionary;
    in fact, it simply doesn't start with '@data-':

    >>> req4 = testdata(**{'@data-for': '#gaga', 'b_start': 'int:25',
    ...                    'ajax_load': 1})
    >>> sorted(req4.items())
    [('@data-for', '#gaga'), ('@original_url', 'https://somewhere.org/'), ('_', '123'), ('ajax_load', 1), ('b_start', 'int:25')]
    >>> dat4, oth4 = pav(req4)
    >>> dat4
    [('for', '#gaga')]
    >>> oth4
    [('original_url', 'https://somewhere.org/')]
    >>> sorted(req4.items())
    [('ajax_load', 1), ('b_start', 'int:25')]

    The "data-"-prefixed names of the first returned dict are converted to dromedarCase:

    >>> req5 = testdata(**{'@data-dromedar-case': 42})
    >>> pav(req5)
    ([('dromedarCase', 42)], [('original_url', 'https://somewhere.org/')])

    """
    data = {}
    other = {}
    nocache = kwargs.pop('nocache', True)
    check_kwargs(kwargs)  # raises TypeError if necessary
    for key in dic.keys():
        if key.startswith(DATA_PREFIX):
            try:
                tail = dromedarCase(key, DATA_OFFSET)
                # print key, '-->', tail
            except ValueError:
                other[key] = dic.pop(key)
            else:
                data[tail] = dic.pop(key)
            # ignore (i.e. neither pop nor store) invalid keys
        elif key == '_':
            # When sending "uncached" $.ajax requests, jQuery adds a "_"
            # variable which contains a numeric timestamp (seconds since epoch)
            val = dic[key]
            if nocache:
                try:
                    int(val)
                except ValueError:
                    # for now, we don't want errors to go unnoticed;
                    # we might want to do some logging instead later
                    raise
                else:
                    del dic[key]
        elif key.startswith(SPECIAL_QV_PREFIX):
            # for now, all such variables are considered AjaxNav-only.
            # We might add a keyword argument with some default value.
            tail = key[1:]
            other[tail] = dic.pop(key)
    return data, other


def strip_method_name(url):
    """
    We sometimes see @@ajax-nav URLs where we don't want them:
    >>> url = 'https://dev-de.unitracc.de/aktuelles/news-und-artikel/@@ajax-nav?b_start:int=25'

    When those cause problems, we need to strip the '@@ajax-nav' part
    but like to keep the '/':
    >>> strip_method_name(url)
    'https://dev-de.unitracc.de/aktuelles/news-und-artikel/?b_start:int=25'
    """
    parsed = urlsplit(url)
    url_list = list(parsed)
    pa = url_list[2]
    if pa.endswith('/@@ajax-nav'):
        url_list[2] = pa[:-10]
    elif 'ajax-nav' in pa:
        raise ValueError('URL %(url)r looks broken (misplaced "ajax-nav")!'
                         % locals())
    return urlunsplit(url_list)


def strip_method_name_dammit(url):
    """
    We might see '@@ajax-nav' in places where it can't possibly work,
    and thus the strip_method_name function (above) won't fix it.

    We certainly want to fix the error.
    But we want our instance to run.
    Thus, this function will help us in cases of such broken URLs:
    >>> url = 'https://dev-de.unitracc.de/aktuelles@@ajax-nav?b_start:int=25'

    This url will make strip_method_name choke; but:
    >>> strip_method_name_dammit(url)
    'https://dev-de.unitracc.de/aktuelles/?b_start:int=25'
    """
    parsed = urlsplit(url)
    url_list = list(parsed)
    pa = url_list[2]
    pa_list = pa.split('/')
    changed = []
    for seg in pa_list:
        if seg.endswith('@@ajax-nav'):
            changed.append(seg[:-10])
        else:
            changed.append(seg)
    url_list[2] = '/'.join([seg for seg in changed
                            if seg]
                            + [''])
    return urlunsplit(url_list)


def parse_current_url(url):
    """
    Parse a URL which was given as the visible URL (usually by the request
    variable "@visible_url") and might contain unresolved UIDs and/or be
    faulty; return a 2-tuple:

        (<list>, <dict>)

    <dict> tells about errors and/or necessary transformations;
    <list> is created from the named tuple returned by urlparse.urlsplit,
    often with some changes applied to the .path component.

    Note that the given URL might be non-functional.
    Since it's meant for use in the browser's address line,
    and in such cases would be used when re-loading the page,
    we do our best to convert it in something reasonable.

    >>> pcu = parse_current_url

    First, we don't want to see UIDs in the address line.

    >>> url1 = './resolveUid/0123abcd0123abcd0123abcd0123abcd'
    >>> res1 = pcu(url1)

    The result looks quite empty:
    >>> res1[0]
    ['', '', '', '', '']

    However, the 2nd part of the returned tuple contains information about the
    extracted UID:

    >>> sorted(res1[1].items())
    [('uid', '0123abcd0123abcd0123abcd0123abcd')]

    (It will be the UID of the context anyway.)
    The caller can now inject the path to the context:

    >>> res1[0][2] = '/path/to/my/context'
    >>> urlunsplit(res1[0])
    '/path/to/my/context'

    See below for a more interesting example (including fragment and query
    string), or views.AjaxLoadBrowserView.corrected_visible_url.

    A trailing '/' is preserved; it implies the non-specification of a
    particular view:
    >>> url2 = './resolveUid/0123abcd0123abcd0123abcd0123abcd/'
    >>> res2 = pcu(url2)
    >>> res2[0]
    ['', '', '/', '', '']

    Normal URLs are not changed:
    >>> url8 = '/some/ordinary/path'
    >>> res8 = pcu(url8)
    >>> res8[0]
    ['', '', '/some/ordinary/path', '', '']

    ... but they are normalized:
    >>> url9 = '/some/./ordinary/path/'
    >>> res9 = pcu(url9)
    >>> res9[0]
    ['', '', '/some/ordinary/path/', '', '']

    Now for the foul values.

    A UID resolution method without a UID following is removed:
    >>> url10 = '/some/foul/resolveUid/path/'
    >>> res10 = pcu(url10)
    >>> res10[0]
    ['', '', '/some/foul/path/', '', '']

    The error is reported:
    >>> res10[1]
    {'methods_deleted': ['resolveUid']}

    Sometimes such methods cumulate:
    >>> url11 = '/some/foul/resolveUid/resolveUid/path/'
    >>> res11 = pcu(url11)
    >>> res11[0]
    ['', '', '/some/foul/path/', '', '']

    Such cases are reported as 'methods_deleted':
    >>> res11[1]
    {'methods_deleted': ['resolveUid', 'resolveUid']}

    UIDs are recognized only when following a suitable method:
    >>> url12 = '0123abcd0123abcd0123abcd0123abcd'
    >>> res12 = pcu(url12)
    >>> res12[0]
    ['', '', '0123abcd0123abcd0123abcd0123abcd', '', '']
    >>> sorted(res12[1].items())
    [('uids_ignored', ['0123abcd0123abcd0123abcd0123abcd'])]

    >>> url13 = '/resolveuid/' + url12 + '/4567cdef4567cdef4567cdef4567cdef'
    >>> res13 = pcu(url13)
    >>> res13[0]
    ['', '', '4567cdef4567cdef4567cdef4567cdef', '', '']
    >>> sorted(res13[1].items())
    [('uid', '0123abcd0123abcd0123abcd0123abcd'), ('uids_ignored', ['4567cdef4567cdef4567cdef4567cdef'])]

    Fragments are retained, of course:
    >>> url14 = '/resolveuid/' + url12 + '#4567cdef4567cdef4567cdef4567cdef'
    >>> res14 = pcu(url14)

    The complete path was removed (for replacement by the context path);
    the fragment is put in the usual place:
    >>> res14[0]
    ['', '', '', '', '4567cdef4567cdef4567cdef4567cdef']
    >>> sorted(res14[1].items())
    [('uid', '0123abcd0123abcd0123abcd0123abcd')]

    Inserting the path of the context (which is expected to feature the UID
    '0123abcd0123abcd0123abcd0123abcd'), you'd get:
    >>> res14[0][2] = '/path/to/context'
    >>> urlunsplit(res14[0])
    '/path/to/context#4567cdef4567cdef4567cdef4567cdef'

    As fragments are retained, so are query strings:
    >>> url15 = '/resolveuid/' + url12 + '?uid=4567cdef4567cdef4567cdef4567cdef'
    >>> res15 = pcu(url15)
    >>> res15[0]
    ['', '', '', 'uid=4567cdef4567cdef4567cdef4567cdef', '']
    >>> sorted(res15[1].items())
    [('uid', '0123abcd0123abcd0123abcd0123abcd')]
    >>> res15[0][2] = '/path/to/context'
    >>> urlunsplit(res15[0])
    '/path/to/context?uid=4567cdef4567cdef4567cdef4567cdef'

    Finally, a trailing @@ajax-nav is removed as well:
    >>> url20 = '/some/path/@@ajax-nav'
    >>> res20 = pcu(url20)
    >>> res20[0]
    ['', '', '/some/path/', '', '']

    Currently we don't report this simple case as an error (just the deletion):
    >>> sorted(res20[1].items())
    [('methods_deleted', ['@@ajax-nav'])]

    If this is not the final chunk, it is reported:
    >>> url21 = '/some/path/@@ajax-nav/'
    >>> res21 = pcu(url21)
    >>> res21[0]
    ['', '', '/some/path/', '', '']
    >>> sorted(res21[1].items())
    [('errors', ["misplaced '@@ajax-nav'"]), ('methods_deleted', ['@@ajax-nav'])]

    Even the non-functional case is fixed:
    >>> url22 = '/some/path@@ajax-nav'
    >>> res22 = pcu(url22)
    >>> res22[0]
    ['', '', '/some/path', '', '']
    >>> res22[1]['errors']
    ["severely misplaced '@@ajax-nav'!"]
    """  # ------------------------------- [ parse_current_url() ... [
    parsed = urlsplit(url)
    url_list = list(parsed)
    assert url_list[2] == parsed.path
    raw_path = url_list[2]
    trailing_slash = raw_path.endswith(sep)
    new_path = normpath(raw_path)
    if trailing_slash:
        new_path += sep
    path_changed = new_path != raw_path

    method_i = None
    path_list = new_path.split('/')
    resinfo = {}
    errors = []
    methods = []
    uids = []
    replacements = []
    # from pdb import set_trace; set_trace()
    for chunk, prev_i, i, next_i in inject_indexes(path_list):
        if chunk in (
            'resolveuid',
          '@@resolveuid',
            'resolveUid',
            'resolvei18n',
          '@@resolvei18n',
            ):
            methods.append((i, chunk, True))   # ... resolver?
            method_i = i
        elif is_uid_shaped(chunk):
            if method_i is None:
                pos_ok = False
            else:
                pos_ok = (method_i == prev_i)
            uids.append((pos_ok, i, chunk))
        elif chunk in (
            'ajax-nav',
          '@@ajax-nav',
            ):
            # from pdb import set_trace; set_trace()
            methods.append((i, chunk, False))  # other method
            if next_i is not None:
                errors.append('misplaced %(chunk)r' % locals())
            else:
                trailing_slash = True
        elif chunk.endswith('@@ajax-nav'):
            errors.append('severely misplaced %r!' % ('@@ajax-nav',))
            po = chunk.rfind('@@ajax-nav')
            replacements.append((i, chunk[:po]))

    for i, chunk in replacements:
        path_list[i] = chunk
        path_changed = True

    good_uid_i = None
    if uids:
        good_uids = [tup[2] for tup in uids if tup[0]]
        if good_uids:
            good_uid_i = max([tup[1] for tup in uids if tup[0]])
            resinfo['uid'] = good_uids[-1]
            del path_list[:good_uid_i+1]
            path_changed = True

        bad_uids_deleted = [tup[2] for tup in uids
                            if not tup[0] and tup[1] < good_uid_i]
        if bad_uids_deleted:
            resinfo['uids_deleted'] = bad_uids_deleted

        bad_uids_ignored = [tup[2] for tup in uids
                            if not tup[0] and tup[1] > good_uid_i]
        if bad_uids_ignored:
            resinfo['uids_ignored'] = bad_uids_ignored

    if methods:
        methods_deleted = [tup[1] for tup in methods
                           if tup[0] < good_uid_i]
        if methods_deleted[1:]:
            # the last one was the one which triggered good_uid_i:
            resinfo['methods_swallowed'] = methods_deleted[:-1]
        methods_remaining = [tup[1] for tup in methods
                             if tup[0] > good_uid_i]
        if methods_remaining:
            # methods without a following UID:
            resinfo['methods_deleted'] = methods_remaining
            delete_ids = reversed([tup[0] for tup in methods
                                   if tup[0] > good_uid_i])
            if good_uid_i is None:
                for i in delete_ids:
                    del path_list[i]
            else:
                for i in delete_ids:
                    del path_list[i-good_uid_i]
            path_changed = True

    if errors:
        resinfo['errors'] = errors

    if path_changed:
        # since we'll insert the context path,
        # we need to retain the trailing slash:
        leading_slash = path_list and not path_list[0]
        new_path = sep.join(path_list)
        if leading_slash and not new_path.startswith(sep):
            new_path = sep + new_path
        if trailing_slash and not new_path.endswith(sep):
            new_path += sep
        url_list[2] = new_path
    return url_list, resinfo  # ---------- ] ... parse_current_url() ]


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
else:
    # Local imports:
    from .minifuncs import NoneOrBool
