# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from zope.component.interfaces import ComponentLookupError

from logging import getLogger
logger = getLogger('visaplan.plone.ajaxnavigation:_get_tool_1')
debug = logger.info

from visaplan.plone.ajaxnavigation import ToolNotFound


def _get_tool_1(name, context, request=None):
    r"""
    This a workaround to help get things running; it should not be used
    permanently.

    It tries the following methods to get the given "tool", in this order:

    - Products.CMFCore.utils.getToolByName
    - zope.component.queryMultiAdapter
    - <ontext>.restrictedTraverse

    In situations where you are confused about the right strategy to get the
    needed tool (because you tried several and still get errors),
    you might replace your code by one of the Vim commands in helpers.vim

    """
    # This is a workaround; it might go away!
    #
    # We don't fully understand currently why sometimes getToolByName fails,
    # and sometimes it seems to be necessary.
    # Thus, we put that nasty trial-and-error stuff in this function
    # and hope to understand that topic better later.
    debug('getting %(name)r for %(context)r ...', locals())
    if not isinstance(name, basestring):
        raise TypeError('Expected %(name)r (the 1st argument) '
                        'to be a string!'
                        % locals())
    try:
        val = getToolByName(context, name)
    except AttributeError as e:
        debug('getToolByName FAILED.')
    else:
        if val is not None:
            debug('getToolByName succeeded.')
            return val
        debug('getToolByName returned %(val)r.', locals())

    if request is None:
        request = context.REQUEST
    val = queryMultiAdapter((context, request), name=name)
    if val is not None:
        debug('queryMultiAdapter succeeded.')
        return val
    else:
        debug('queryMultiAdapter FAILED.')

    try:
        val = context.restrictedTraverse('@@'+name)
        if val is not None:
            debug('context.restrictedTraverse succeeded', locals())
            return val
    except AttributeError as e:
        debug('context.restrictedTraverse FAILED (%(e)r)', locals())
    else:
        debug('context.restrictedTraverse FAILED (not found)', locals())
    raise ToolNotFound(name)
