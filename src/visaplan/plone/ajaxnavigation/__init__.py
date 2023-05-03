"""\
visaplan.plone.ajaxnavigation: Add AJAX navigation to a Plone site.

Short description
"""
# Python compatibility:
from __future__ import absolute_import

# Setup tools:
import pkg_resources

# Zope:
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('visaplan.plone.ajaxnavigation')
try:
    pkg_resources.get_distribution('zope.deprecation')
except pkg_resources.DistributionNotFound:
    pass
else:
    # Zope:
    from zope.deprecation import deprecated

    # Local imports:
    from .exceptions import AjaxnavError as Error
    deprecated(Error, 'moved to .exceptions and renamed to AjaxnavError')
    # Local imports:
    from .exceptions import AjaxnavTypeError, TemplateNotFound, ToolNotFound

    # zope.deprecation.moved is vor modules only, right? :-(
    deprecated(AjaxnavTypeError, 'moved to .exceptions')
    deprecated(ToolNotFound,     'moved to .exceptions')
    deprecated(TemplateNotFound, 'moved to .exceptions')
