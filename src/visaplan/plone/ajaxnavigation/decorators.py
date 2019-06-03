# -*- coding: utf-8 -*-
from functools import wraps

from simplejson import dumps


def returns_json(raw):
    """
    Decorate the given function to ...
    - convert the result to JSON, and
    - add the appropriate HTTP headers
    """
    @wraps(raw)
    def wrapped(self, **kwargs):
        dic = raw(self, **kwargs)
        txt = dumps(dic)
        context = self.context
        setHeader = context.REQUEST.RESPONSE.setHeader
        setHeader('Content-Type', 'application/json; charset=utf-8')
        setHeader('Content-Length', len(txt))
        return txt
    return wrapped
