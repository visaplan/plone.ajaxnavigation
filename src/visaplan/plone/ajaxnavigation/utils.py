# -*- coding: utf-8 -*-

def options_dict(**kwargs):
    """
    Create a options dictionary for AjaxNav

    The keys of the dictionary are:

    'whitelist' -- a list of CSS-style selectors to select the objects which
                   will delegate the click handler to their child 'a' objects;
                   default is ['body'].

    'blacklist' -- after applying "delegate", it is possible to "undelegate"
                   certain parts of the DOM;
                   default is the empty list.

    This function returns a dictionary, and the keys of Python dictionaries
    are not guaranteed to follow a certain order.
    Thus, we'll create a little formatting wrapper for reproducibility:
    >>> def tst(**kwargs):
    ...     return sorted(options_dict(**kwargs).items())

    The default is a whitelist of ['body'] and an empty blacklist:
    >>> tst()
    [('blacklist', []), ('whitelist', ['body'])]

    Lists of selectors (currently whitelist and blacklist) can be given as
    strings which will be split whereever commas are found:

    >>> tst(whitelist='one, two')
    [('blacklist', []), ('whitelist', ['one', 'two'])]
    """
    # ./resource/ajaxnavigation.js
    pop = kwargs.pop
    whitelist = pop('whitelist', None) or 'body'
    if isinstance(whitelist, basestring):
        whitelist = [sel.strip() for sel in whitelist.split(',')]
    blacklist = pop('blacklist', [])
    if isinstance(blacklist, basestring):
        blacklist = [sel.strip() for sel in blacklist.split(',')]
    if kwargs:
        raise TypeError('Currently unsupported kwarg(s) %r'
                        % (kwargs.items()[0],
                           ))
    return {
        'whitelist': [sel for sel in whitelist if sel],
        'blacklist': [sel for sel in blacklist if sel],
        }


if __name__ == '__main__':
    import doctest
    doctest.testmod()
