"""\
visaplan.plone.ajaxnavigation: Add AJAX navigation to a Plone site.

Short description
"""
# Python compatibility:
from __future__ import absolute_import

import pkg_resources

# Zope:
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('visaplan.plone.ajaxnavigation')
try:
    pkg_resources.get_distribution('zope.deprecation')
except pkg_resources.DistributionNotFound:
    pass
else:
    from zope.deprecation import deprecated
    from .exceptions import AjaxnavError as Error
    deprecated(Error, 'moved to .exceptions and renamed to AjaxnavError')
    from .exceptions import AjaxnavTypeError, ToolNotFound, TemplateNotFound
    # zope.deprecation.moved is vor modules only, right? :-( 
    deprecated(AjaxnavTypeError, 'moved to .exceptions')
    deprecated(ToolNotFound,     'moved to .exceptions')
    deprecated(TemplateNotFound, 'moved to .exceptions')
