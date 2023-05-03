# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six

from string import whitespace
WHITESPACE = frozenset(whitespace)


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
    >>> view_choice_tuple(('introduction', 'embed'))
    ('introduction', 'embed')

    In this case, the calling folder has an 'introduction' page which is
    considered its associated page, and will be rendered using its 'embed'
    method ('introduction/@@embed').

    Now that we have a page_id, it is on the choose_view method
    to look for that page and call the given view.

    For non-folders (which can't have a default_page mapped),
    we'll usually only get the name of a view:
    >>> view_choice_tuple('embed')
    (None, 'embed')
    """
    if isinstance(val, six.string_types):
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
    Convert a dashed variable name (like common for HTML5 "data-" attributes
    to its dromedar-cased form.

    >>> dromedarCase('dashed-name')
    'dashedName'

    For conversion of "data-" names we specify an offset of 5:

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
    if kwargs:
        bogus = list(kwargs.keys())
        raise TypeError('Undefined kwargs found! (%(bogus)s)'
                        % locals())
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
else:
    from .minifuncs import NoneOrBool
