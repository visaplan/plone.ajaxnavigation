# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from __future__ import absolute_import

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from plone.supermodel import model
from zope import schema

from visaplan.plone.ajaxnavigation import _


class IVisaplanPloneAjaxnavigationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAjaxNavigationSettings(model.Schema):
    """ Schema fields for view "@@ajaxnav-options-default"
    """
    model.fieldset(
            'clientside',
            label=_(u'Clientside processing'),
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
        value_type=schema.BytesLine(title=_(u'CSS selector')),
        default=['body',
                 ],
        description=_(
            u'help_whitelist',
            default=u"CSS selectors which activate delegation"
            u" for their a-element descendants"
            ))

    blacklist = schema.List(
        title=_(u"Blacklist"),
        value_type=schema.BytesLine(title=_(u'CSS selector')),
        default=[],
        description=_(
            u'help_blacklist',
            default=u"CSS selectors which deactivate delegation"
            u" for their a-element descendants"
            ))

    nested_blacklist = schema.Bool(
        title=_(u"Nested blacklist"),
        default=False,
        description=_(
            u'help_nested_blacklist',
            default=u"If this is set to True, and if there is a non-empty"
            u" Blacklist, the Blacklist un-delegation will be applied during the"
            u" whitelist processing."
            ))

    view_ids = schema.List(
        title=_(u"View IDs"),
        value_type=schema.BytesLine(title=_(u'view id')),
        default=['view',
                 'edit',
                 'base_edit',
                 ],
        description=_(
            u'help_view_ids',
            default=u"When computing the URLs to try,"
            u" the values given here "
            u' (when following the last slash in the path, of course) '
            u"are considered view ids."
            ))

    view_prefixes = schema.List(
        title=_(u"View prefixes"),
        value_type=schema.BytesLine(title=_(u'view prefix')),
        default=['manage_',
                 ],
        description=_(
            u'help_view_prefixes',
            default=u"If the last path segment of a URL starts with one of"
            " the values given here, it is considered a view name."
            ))

    view_suffixes = schema.List(
        title=_(u"View suffixes"),
        value_type=schema.BytesLine(title=_(u'view suffix')),
        default=['_view',
                 ],
        description=_(
            u'help_view_suffixes',
            default=u"If the last path segment of a URL ends with one of the"
            u" values given here, it is considered a view name."
            ))

    blacklist_view_ids = schema.List(
        title=_(u"Blacklist view IDs"),
        value_type=schema.BytesLine(title=_(u'view id')),
        default=['manage',
                 'edit',
                 'base_edit',
                 ],
        description=_(
            u'help_blacklist_view_ids',
            default=u"When computing the URLs to try, the values given here "
            u'(when following the last slash in the path, of course) '
            u"are considered view ids "
            u"for which an AJAX load won't be tried."
            ))

    blacklist_view_prefixes = schema.List(
        title=_(u"Blacklist view prefixes"),
        value_type=schema.BytesLine(title=_(u'view prefix')),
        default=['manage_',
                 ],
        description=_(
            u'help_blacklist_view_prefixes',
            default=u"If the last path segment of a URL starts with one of the"
            u" values given here, it is considered a view name"
            u" for which an AJAX load won't be tried."
            ))

    blacklist_view_suffixes = schema.List(
        title=_(u"Blacklist view suffixes"),
        value_type=schema.BytesLine(title=_(u'view suffix')),
        default=['_edit',
                 ],
        description=_(
            u'help_blacklist_view_suffixes',
            default=u"If the last path segment of a URL ends with one of the"
            u" values given here, it is considered a view name"
            u" for which an AJAX load won't be tried."
            ))

    selectors = schema.Dict(
        title=_(u"Selectors for data keys"),
        default={'content': "#content",
                 },
        key_type=schema.BytesLine(title=_(u'AJAX response key')),
        value_type=schema.BytesLine(title=_(u'CSS selector[,...]')),
        description=_(
            u'help_selectors',
            default=u'For each “normalˮ key from an AJAX response, '
                u'configure a CSS selector which tells where to put the value. '
                u'You can give more than one value, separated by comma, '
                u'which will be tried in order.'
                ))

    model.fieldset(
            'internal',
            label=_(u'Internal processing'),
            fields=[
                'layout4ajax',
                'view4ajax',
                ])

    layout4ajax = schema.Dict(
        title=_(u"Layouts for AJAX"),
        default={},
        key_type=schema.BytesLine(title=_(u'full-page layout')),
        value_type=schema.BytesLine(title=_(u'AJAX view')),
        description=_(
            u'help_layout4ajax',
            default=u'Having detected the layout of the current target '
                u'object, we may map an AJAX version '
                u'to each “full-pageˮ layout.'
                ))

    view4ajax = schema.Dict(
        title=_(u"Views for AJAX"),
        default={},
        key_type=schema.BytesLine(title=_(u'portal_type')),
        value_type=schema.BytesLine(title=_(u'AJAX view')),
        description=_(
            u'help_view4ajax',
            default=u'For each “portal_typeˮ, '
                u'we may map an AJAX version '
                u'corresponding to the standard full-page view.'
                ))

    scrollto_default_selector = schema.BytesLine(
        title=_(u"Default selector for the @scrollto feature"),
        default=None,
        description=_(
            u'help_scrollto_default_selector',
            default=u'When loading new content '
                u'by clicking on a hyperlink somewhere down the page, '
                u'the contents could be loaded unnoticed. '
                u'To prevent this, we scroll up; '
                u'globally, or to the element found by the CSS selector given here. '
                u'You might use the special value "@auto".'
                ))

    scrollto_default_deltay = schema.Int(
        title=_(u"Default vertical offset for the @scrollto feature"),
        default=0)

    scrollto_auto_key = schema.BytesLine(
        title=_(u"Default key for the @scrollto @auto value"),
        default='content',
        description=_(
            u'help_scrollto_auto_key',
            default=u'For a @scrollto value of "@auto", '
                u'use the selector given for the key given here; '
                u'default: "content". '
                u'E.g., if the value is "content", '
                u'and the selector for the "content" key is "#content", '
                u'the "#content" selector is used to call the jQuery "scrollTop" method. '
                ))
