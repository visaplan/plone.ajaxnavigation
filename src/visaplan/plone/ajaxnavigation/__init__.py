"""\
visaplan.plone.ajaxnavigation: Add AJAX navigation to a Plone site.

Short description
"""
# Python compatibility:
from __future__ import absolute_import

from importlib_metadata import PackageNotFoundError
from importlib_metadata import version as pkg_version

# Zope:
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('visaplan.plone.ajaxnavigation')
try:
    pkg_version('zope.deprecation')
except PackageNotFoundError:
    pass
else:
    # Zope:
    from zope.deprecation import deprecated

    # Local imports:
    from .exceptions import AjaxnavError as Error
    deprecated(Error, 'moved to .exceptions and renamed to AjaxnavError')
    # Local imports:
    from .exceptions import AjaxnavTypeError, TemplateNotFound, ToolNotFound

    # zope.deprecation.moved is for modules only, right? :-(
    deprecated(AjaxnavTypeError, 'moved to .exceptions')
    deprecated(ToolNotFound,     'moved to .exceptions')
    deprecated(TemplateNotFound, 'moved to .exceptions')
