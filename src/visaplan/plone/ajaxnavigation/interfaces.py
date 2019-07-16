# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from plone.supermodel import model
from plone.registry import field

from visaplan.plone.ajaxnavigation import _


class IAjaxNavigationClientSettings(Interface):
    """ Schema fields for view "@@ajaxnav-options-default"
    """
    whitelist = field.List(
        title=_(u"Whitelist"),
        value_type=field.BytesLine,
        default=['body',
                 ],
        description=_(u"CSS selectors which activate delegation"
        " for their <a> descendants"
        ))

    blacklist = field.List(
        title=_(u"Blacklist"),
        value_type=field.BytesLine,
        default=[],
        description=_(u"CSS selectors which deactivate delegation"
        " for their <a> descendants"
        ))

    nested_blacklist = field.Bool(
        title=_(u"Nested blacklist"),
        value_type=field.BytesLine,
        default=False,
        description=_(u"If this is set to True, and if there is a non-empty"
        " Blacklist, the Blacklist un-delegation will be applied during the"
        " whitelist processing."
        ))

    view_ids = field.List(
        title=_(u"View_ids"),
        value_type=field.BytesLine,
        default=['view',
                 'edit',
                 'base_edit'],
        description=_(u"When computing the URLs to try,"
        " the values given here are considered view ids"
        ))

    view_prefixes = field.List(
        title=_(u"View prefixes"),
        value_type=field.BytesLine,
        default=['manage_',
                 ],
        description=_(u"If the last path segment of a URL starts with one of"
        " the values given here, it is considered a view name."
        ))

    view_suffixes = field.List(
        title=_(u"View suffixes"),
        value_type=field.BytesLine,
        default=['_view',
                 ],
        description=_(u"If the last path segment of a URL ends with one of the"
        " values given here, it is considered a view name."
        ))

    blacklist_view_ids = field.List(
        title=_(u"Blacklist_view_ids"),
        value_type=field.BytesLine,
        default=['manage',
                 'edit',
                 'base_edit'],
        description=_(u"When computing the URLs to try, the values given here "
        "are considered view ids "
        "for which an AJAX load won't be tried."
        ))

    blacklist_view_prefixes = field.List(
        title=_(u"Blacklist_view_prefixes"),
        value_type=field.BytesLine,
        default=['manage_',
                 ])

    blacklist_view_suffixes = field.List(
        title=_(u"Blacklist_view_suffixes"),
        value_type=field.BytesLine,
        default=['_edit',
                 ])

    selectors = field.Dict(
        title=_(u"Selectors for data keys"),
        default={'content': ["#region-content,#content"],
                 },
        key_type=field.BytesLine,
        value_type=field.BytesLine,
        description=_(u'For each "normal" key from an AJAX response, '
        'configure a CSS selector which tells where to put the value. '
        'You can give more than one value, separated by comma.'
        ))


class IAjaxNavigationInternalSettings(model.Schema):
    """ Schema fields for internal processing
    """
    layout4ajax = field.Dict(
        title=_(u"Layouts for AJAX"),
        default={},
        key_type=field.BytesLine,
        value_type=field.BytesLine,
        description=_(u'Having detected the layout of the current target '
        'object, we may map an AJAX version '
        'to each "full-page" layout.'
        ))

    view4ajax = field.Dict(
        title=_(u"Views for AJAX"),
        default={},
        key_type=field.BytesLine,
        value_type=field.BytesLine,
        description=_(u'For each "portal_type", '
        'we may map an AJAX version '
        'corresponding to the standard full-page view.'
        ))

clientside_map = {
        key: 'visaplan.plone.ajaxnavigation.'+key
        for key in (
                'view_ids',
                'view_prefixes',
                'view_suffixes',
                'blacklist_view_ids',
                'blacklist_view_prefixes',
                'blacklist_view_suffixes',
                'selectors',
                )}

internal_map = {
        key: 'visaplan.plone.ajaxnavigation.'+key
        for key in (
                'layout4ajax',
                'view4ajax',
                )}


class IVisaplanPloneAjaxnavigationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
