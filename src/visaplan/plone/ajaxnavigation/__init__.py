"""\
visaplan.plone.ajaxnavigation: Add AJAX navigation to a Plone site.

Short description
"""
from __future__ import absolute_import

from zope.i18nmessageid import MessageFactory


_ = MessageFactory('visaplan.plone.ajaxnavigation')

class Error(Exception):
    """
    Root exception class for the visaplan.plone.ajaxnavigation package
    """

class AjaxnavTypeError(TypeError, Error):
    """
    Some visaplan.plone.ajaxnavigation component has been used wrongly
    """

class ToolNotFound(Error):
    pass

class TemplateNotFound(Error):
    pass
