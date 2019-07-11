# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from plone.supermodel import model
from zope import schema

from visaplan.plone.ajaxnavigation import _


class IAjaxNavigationClientSettings(model.Schema):
    """ Schema fields for view "@@ajaxnav-options-default"
    """
    whitelist = schema.List(
        title=_(u"Whitelist"),
        value_type=schema.BytesLine,
        default=['body',
                 ],
        description=_(u"CSS selectors which activate delegation"
        " for their <a> descendants"))

    blacklist = schema.List(
        title=_(u"Blacklist"),
        value_type=schema.BytesLine,
        default=[],
        description=_(u"CSS selectors which deactivate delegation"
        " for their <a> descendants"))

    nested_blacklist = schema.Bool(
        title=_(u"Nested blacklist"),
        value_type=schema.BytesLine,
        default=False,
        description=_(u"If this is set to True, and if there is a non-empty"
        " Blacklist, the Blacklist un-delegation will be applied during the"
        " whitelist processing"))

    view_ids = schema.List(
        title=_(u"View_ids"),
        value_type=schema.BytesLine,
        default=['view',
                 'edit',
                 'base_edit'],
        description=_(u"When computing the URLs to try, the values given here are considered view ids"))

    view_prefixes = schema.List(
        title=_(u"View prefixes"),
        value_type=schema.BytesLine,
        default=['manage_',
                 ],
        description=_(u"If the last path segment of a URL starts with one of"
        " the values given here, it is considered a view name"))

    view_suffixes = schema.List(
        title=_(u"View suffixes"),
        value_type=schema.BytesLine,
        default=['_view',
                 ],
        description=_(u"If the last path segment of a URL ends with one of the"
        " values given here, it is considered a view name"))

    blacklist_view_ids = schema.List(
        title=_(u"Blacklist_view_ids"),
        value_type=schema.BytesLine,
        default=['manage',
                 'edit',
                 'base_edit'],
        description=_(u"When computing the URLs to try, the values given here "
        "are considered view ids "
        "for which an AJAX load won't be tried."))

    blacklist_view_prefixes = schema.List(
        title=_(u"Blacklist_view_prefixes"),
        value_type=schema.BytesLine,
        default=['manage_',
                 ])

    blacklist_view_suffixes = schema.List(
        title=_(u"Blacklist_view_suffixes"),
        value_type=schema.BytesLine,
        default=['_edit',
                 ])

    selectors = schema.Dict(
        title=_(u"Selectors for data keys"),
        default={'content': ["#region-content,#content"],
                 },
        description=_(u'For each "normal" key from an AJAX response, '
        'configure a CSS selector which tells where to put the value. '
        'You can give more than one value, separated by comma.'),
        key_type=schema.BytesLine,
        value_type=schema.BytesLine)


class IAjaxNavigationInternalSettings(model.Schema):
    """ Schema fields for internal processing
    """
    layout4ajax = schema.Dict(
        title=_(u"Layouts for AJAX"),
        default={'content': ["#region-content,#content"],
                 },
        description=_(u'For each "normal" layout of a link target, '
        'you may configure an AJAX version which will provide the '
        '"meat" only'),
        key_type=schema.BytesLine,
        value_type=schema.BytesLine)


class IVisaplanPloneAjaxnavigationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
