# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from plone.supermodel import model
from zope import schema

from visaplan.plone.ajaxnavigation import _


class IAjaxNavigationSettings(model.Schema):
    """ Schema fields for view "@@ajaxnav-options-default"
    """
    model.fieldset(
            'clientside',
            label=u'Clientside processing',
            fields=[
                'whitelist',
                'blacklist',
                'nested_blacklist',
                'view_ids',
                'view_prefixes',
                'view_suffixes',
                'blacklist_view_ids',
                'blacklist_view_prefixes',
                'blacklist_view_suffixes',
                'selectors',
                ])

    whitelist = schema.List(
        title=_(u"Whitelist"),
        value_type=schema.BytesLine,
        default=['body',
                 ],
        description=_(
            u'help_whitelist',
            default=u"CSS selectors which activate delegation"
            " for their <a> descendants"
            ))

    blacklist = schema.List(
        title=_(u"Blacklist"),
        value_type=schema.BytesLine,
        default=[],
        description=_(
            u'help_blacklist',
            default=u"CSS selectors which deactivate delegation"
            " for their <a> descendants"
            ))

    nested_blacklist = schema.Bool(
        title=_(u"Nested blacklist"),
        value_type=schema.BytesLine,
        default=False,
        description=_(
            u'help_nested_blacklist',
            default=u"If this is set to True, and if there is a non-empty"
            " Blacklist, the Blacklist un-delegation will be applied during the"
            " whitelist processing."
            ))

    view_ids = schema.List(
        title=_(u"View_ids"),
        value_type=schema.BytesLine,
        default=['view',
                 'edit',
                 'base_edit',
                 ],
        description=_(
            u'help_view_ids',
            default=u"When computing the URLs to try,"
            " the values given here are considered view ids"
            ))

    view_prefixes = schema.List(
        title=_(u"View prefixes"),
        value_type=schema.BytesLine,
        default=['manage_',
                 ],
        description=_(
            u'help_view_prefixes',
            default=u"If the last path segment of a URL starts with one of"
            " the values given here, it is considered a view name."
            ))

    view_suffixes = schema.List(
        title=_(u"View suffixes"),
        value_type=schema.BytesLine,
        default=['_view',
                 ],
        description=_(
            u'help_view_suffixes',
            default=u"If the last path segment of a URL ends with one of the"
            " values given here, it is considered a view name."
            ))

    blacklist_view_ids = schema.List(
        title=_(u"Blacklist_view_ids"),
        value_type=schema.BytesLine,
        default=['manage',
                 'edit',
                 'base_edit',
                 ],
        description=_(
            u'help_blacklist_view_ids',
            default=u"When computing the URLs to try, the values given here "
            "are considered view ids "
            "for which an AJAX load won't be tried."
            ))

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
        key_type=schema.BytesLine,
        value_type=schema.BytesLine,
        description=_(
            u'help_selectors',
            default=u'For each "normal" key from an AJAX response, '
                'configure a CSS selector which tells where to put the value. '
                'You can give more than one value, separated by comma.'
                ))

    model.fieldset(
            'internal',
            label=u'Internal processing',
            fields=[
                'layout4ajax',
                'view4ajax',
                ])

    layout4ajax = schema.Dict(
        title=_(u"Layouts for AJAX"),
        default={},
        key_type=schema.BytesLine,
        value_type=schema.BytesLine,
        description=_(
            u'help_layout4ajax',
            default=u'Having detected the layout of the current target '
                'object, we may map an AJAX version '
                'to each "full-page" layout.'
                ))

    view4ajax = schema.Dict(
        title=_(u"Views for AJAX"),
        default={},
        key_type=schema.BytesLine,
        value_type=schema.BytesLine,
        description=_(
            u'help_view4ajax',
            default=u'For each "portal_type", '
                'we may map an AJAX version '
                'corresponding to the standard full-page view.'
                ))

clientside_map = {
        key: 'visaplan.plone.ajaxnavigation.'+key
        for key in (
                'whitelist',
                'blacklist',
                'nested_blacklist',
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

all_keys = clientside_map.keys() + \
        internal_map.keys()


class IVisaplanPloneAjaxnavigationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
