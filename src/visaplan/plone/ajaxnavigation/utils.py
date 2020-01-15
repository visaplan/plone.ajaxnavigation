# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
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
    """
    if viewname == 'view':  # shortcut; doesn't change the result
        return 'embed'
    elif not viewname:
        return None
    dividers = ('_', '-')
    for divider in dividers:
        liz = viewname.split(divider)
        if liz[-1] == 'view':
            return divider.join(liz[:-1] + ['embed'])
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


def pop_ajaxnav_vars(dic, **kwargs):
    """
    Remove all vars from the request form data which might disturb standard
    Zope/Plone behaviour.

    dic -- a dictionary, usually request.form

    Supported keyword arguments, for now:

    nocache -- remove an "_" argument as added by jQuery for "uncached" $.ajax
               requests; default: True

    >>> def pav(*args, **kwargs):
    ...     d, o = pop_ajaxnav_vars(*args, **kwargs)
    ...     return (sorted(d.items()), sorted(o.items()))
    >>> def testdata(**kwargs):
    ...     res = {'_': '123', '_given_url': 'https://somewhere.org/'}
    ...     res.update(kwargs)
    ...     return res

    Simple example:

    >>> tst1 = testdata()
    >>> sorted(tst1.items())
    [('_', '123'), ('_given_url', 'https://somewhere.org/')]
    >>> pav(tst1)
    ([], [('given_url', 'https://somewhere.org/')])

    The extracted vars have been removed "in-place" from the given dict:
    >>> sorted(tst1.items())
    []

    To avoid the removal of an '_' option, use nocache=False:

    >>> tst2 = testdata()
    >>> pav(tst2, nocache=False)
    ([], [('given_url', 'https://somewhere.org/')])
    >>> sorted(tst2.items())
    [('_', '123')]

    Another example with "data" and a something which will be left alone:

    >>> tst3 = testdata(**{'data-for': '#gaga', 'b_start': 'int:25'})
    >>> pav(tst3)
    ([('for', '#gaga')], [('given_url', 'https://somewhere.org/')])
    >>> sorted(tst3.items())
    [('b_start', 'int:25')]
    
    """
    data = {}
    other = {}
    nocache = kwargs.pop('nocache', True)
    if kwargs:
        bogus = list(kwargs.keys())
        raise TypeError('Undefined kwargs found! (%(bogus)s)'
                        % locals())
    for key in dic.keys():
        if key.startswith('data-'):
            tail = key[5:]
            if tail:
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
        elif key.startswith('_'):
            # for now, all such variables are considered AjaxNav-only.
            # We might add a keyword argument with some default value.
            tail = key[1:]
            other[tail] = dic.pop(key)
    return data, other


if __name__ == '__main__':
    import doctest
    doctest.testmod()
