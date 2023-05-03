# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

from six import string_types as six_string_types

# visaplan:
from visaplan.tools.minifuncs import makeBool


def NoneOrBool(val):
    """
    A variant of visaplan.tools.minifuncs.NoneOrBool which translates 'auto' into None

    >>> NoneOrBool('')
    >>> NoneOrBool('auto')
    >>> NoneOrBool('auto') is None
    True
    >>> NoneOrBool('True')
    True
    >>> NoneOrBool('on')
    True
    >>> NoneOrBool('oFf')
    False

    Wrong values yield ValueErrors:

    >>> NoneOrBool('perhaps')
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'perhaps'

    A 'None' *string* is refused as well:
    >>> NoneOrBool('None')
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'none'
    """

    if val is None or val == '':
        return None
    elif isinstance(val, six_string_types):
        val = val.strip().lower()
        if val in ('', 'auto'):
            return None
        return bool(makeBool(val))
    else:
        return bool(val)

