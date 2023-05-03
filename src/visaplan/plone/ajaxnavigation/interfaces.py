# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
# Python compatibility:
from __future__ import absolute_import

# Zope:
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

# Plone:
from plone.supermodel import model

# Local imports:
from .defaults import default
from visaplan.plone.ajaxnavigation import _

__all__ = [
        'IVisaplanPloneAjaxnavigationLayer',
        'IAjaxNavigationSettings',
        ]


class IVisaplanPloneAjaxnavigationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAjaxNavigationSettings(model.Schema):
    """ Schema fields for view "@@ajaxnav-options-default"
    """
    # ------------------- [ selectors: Where to put the contents ... [
    model.fieldset(
            'selectors',
            label=_(u'Selectors'),
            fields=[
                'selectors',
                ])

    selectors = schema.Dict(
        title=_(u"Selectors for data keys"),
        default=default['selectors'],
        missing_value=default['selectors'],
        key_type=schema.BytesLine(title=_(u'AJAX response key')),
        value_type=schema.BytesLine(title=_(u'CSS selector[,...]')),
        description=_(
            u'help_selectors',
            default=u'For each “normalˮ key from an AJAX response, '
                u'configure a CSS selector which tells where to put the value. '
                u'You can give more than one value, separated by comma, '
                u'which will be tried in order.'
                ))
    # ------------------- ] ... selectors: Where to put the contents ]

    # ------------------ [ areas: Where to delegate / undelegate ... [
    model.fieldset(
            'areas',
            label=_(u'Active areas'),
            fields=[
                'whitelist',
                'blacklist',
                'nested_blacklist',
                ])

    whitelist = schema.List(
        title=_(u"Whitelist"),
        value_type=schema.BytesLine(title=_(u'CSS selector')),
        default=default['whitelist'],
        missing_value=default['whitelist'],
        description=_(
            u'help_whitelist',
            default=u"CSS selectors which activate delegation"
            u" for their a-element descendants"
            ))

    blacklist = schema.List(
        title=_(u"Blacklist"),
        value_type=schema.BytesLine(title=_(u'CSS selector')),
        default=default['blacklist'],
        missing_value=default['blacklist'],
        description=_(
            u'help_blacklist',
            default=u"CSS selectors which deactivate delegation"
            u" for their a-element descendants"
            ))

    nested_blacklist = schema.Bool(
        title=_(u"Nested blacklist"),
        default=default['nested_blacklist'],
        missing_value=default['nested_blacklist'],
        description=_(
            u'help_nested_blacklist',
            default=u"If this is set to True, and if there is a non-empty"
            u" Blacklist, the Blacklist un-delegation will be applied during the"
            u" whitelist processing."
            ))
    # ------------------ ] ... areas: Where to delegate / undelegate ]

    # ----------------------------- [ views: View id recognition ... [
    model.fieldset(
            'views',
            label=_(u'View id recognition'),
            fields=[
                'view_ids',
                'view_prefixes',
                'view_suffixes',
                'blacklist_view_ids',
                'blacklist_view_prefixes',
                'blacklist_view_suffixes',
                ])
    view_ids = schema.List(
        title=_(u"View IDs"),
        value_type=schema.BytesLine(title=_(u'view id')),
        default=default['view_ids'],
        missing_value=default['view_ids'],
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
        default=default['view_prefixes'],  # see as well --> blacklist_view_prefixes
        missing_value=default['view_prefixes'],
        description=_(
            u'help_view_prefixes',
            default=u"If the last path segment of a URL starts with one of"
            " the values given here, it is considered a view name."
            ))

    view_suffixes = schema.List(
        title=_(u"View suffixes"),
        value_type=schema.BytesLine(title=_(u'view suffix')),
        default=default['view_suffixes'],
        missing_value=default['view_suffixes'],
        description=_(
            u'help_view_suffixes',
            default=u"If the last path segment of a URL ends with one of the"
            u" values given here, it is considered a view name."
            ))

    blacklist_view_ids = schema.List(
        title=_(u"Blacklist view IDs"),
        value_type=schema.BytesLine(title=_(u'view id')),
        default=default['blacklist_view_ids'],
        missing_value=default['blacklist_view_ids'],
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
        default=default['blacklist_view_prefixes'],
        missing_value=default['blacklist_view_prefixes'],
        description=_(
            u'help_blacklist_view_prefixes',
            default=u"If the last path segment of a URL starts with one of the"
            u" values given here, it is considered a view name"
            u" for which an AJAX load won't be tried."
            ))

    blacklist_view_suffixes = schema.List(
        title=_(u"Blacklist view suffixes"),
        value_type=schema.BytesLine(title=_(u'view suffix')),
        default=default['blacklist_view_suffixes'],
        missing_value=default['blacklist_view_suffixes'],
        description=_(
            u'help_blacklist_view_suffixes',
            default=u"If the last path segment of a URL ends with one of the"
            u" values given here, it is considered a view name"
            u" for which an AJAX load won't be tried."
            ))
    # ----------------------------- ] ... views: View id recognition ]

    # ----------------- [ other_exceptions: Other non-AJAX links ... [
    model.fieldset(
            'other_exceptions',
            label=_(u'Other exceptions'),
            fields=[
                'blacklist_class_ids',
                'blacklist_class_prefixes',
                'blacklist_class_suffixes',
                'regard_target_attribute'
                ])

    blacklist_class_ids = schema.List(
        title=_(u"Blacklist class IDs"),
        value_type=schema.BytesLine(title=_(u'class id')),
        default=default['blacklist_class_ids'],
        missing_value=default['blacklist_class_ids'],
        description=_(
            u'help_blacklist_class_ids',
            default=u'For some classes of "a" elements, other actions than '
            u'navigation are desired, e.g. opening of a lightbox.'
            ))

    blacklist_class_prefixes = schema.List(
        title=_(u"Blacklist class prefixes"),
        value_type=schema.BytesLine(title=_(u'class prefix')),
        default=default['blacklist_class_prefixes'],
        missing_value=default['blacklist_class_prefixes'],
        description=_(
            u'help_blacklist_class_prefixes',
            default=u'You might have a set of "a" classes '
            u"which share a common prefix and need to be excepted "
            u"from the AJAX navigation."
            ))

    blacklist_class_suffixes = schema.List(
        title=_(u"Blacklist class suffixes"),
        value_type=schema.BytesLine(title=_(u'class suffix')),
        default=default['blacklist_class_suffixes'],
        missing_value=default['blacklist_class_suffixes'],
        description=_(
            u'help_blacklist_class_suffixes',
            default=u'You might have a set of "a" classes '
            u"which share a common suffix and need to be excepted "
            u"from the AJAX navigation."
            ))

    regard_target_attribute = schema.Bool(
        title=_(u"Regard target attribute"),
        default=default['regard_target_attribute'],
        missing_value=default['regard_target_attribute'],
        description=_(
            u'help_regard_target_attribute',
            default=u"Following the Principle of Least Surprise, we regard "
            u'existing target attributes of "a" elements, causing pages to '
            u'continue to open in new windows (or, more likely with modern '
            u'browsers: tabs). '
            u'However, the use of target attributes is not recommended; '
            u'they don\'t allow users to choose otherwise. '
            u'Thus, we recommend you to set this value to False, '
            u'but this must be your own explicit decision.'
            ))
    # ----------------- ] ... other_exceptions: Other non-AJAX links ]

    # --------------------------------------[ security: Security ... [
    model.fieldset(
            'security',
            label=_(u'Security'),
            fields=[
                'target_rel_values',
                ])

    target_rel_values = schema.List(
        title=_(u"rel values for a[target] links"),
        value_type=schema.BytesLine(title=_(u'rel value')),
        default=default['target_rel_values'],
        missing_value=default['target_rel_values'],
        description=_(
            u'help_target_rel_values',
            default=u'A window which is opened automatically by clicking '
            u'an "a" element with a non-_self target attribute '
            u'has access to our Window element, even if located '
            u'in another site. For modern browsers, this can be prevented '
            u'by using a rel="noopener" attribute.'
            ))
    # --------------------------------------] ... security: Security ]

    # -------------------------------------- [ scroll: Scrolling ... [
    model.fieldset(
            'scroll',
            label=_(u'Scrolling'),
            fields=[
                'scrollto_default_selector',
                'scrollto_default_deltay',
                'scrollto_auto_key',
                ])

    scrollto_default_selector = schema.BytesLine(
        title=_(u"Default selector for the @scrollto feature"),
        default=default['scrollto_default_selector'],
        missing_value=default['scrollto_default_selector'],
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
        default=default['scrollto_default_deltay'])
        # no missing_value; this didn't start up!

    scrollto_auto_key = schema.BytesLine(
        title=_(u"Default key for the @scrollto @auto value"),
        default=default['scrollto_auto_key'],
        missing_value=default['scrollto_auto_key'],
        description=_(
            u'help_scrollto_auto_key',
            default=u'For a @scrollto value of "@auto", '
                u'use the selector given for the key given here; '
                u'default: "content". '
                u'E.g., if the value is "content", '
                u'and the selector for the "content" key is "#content", '
                u'the "#content" selector is used to call the jQuery "scrollTop" method. '
                ))
    # -------------------------------------- ] ... scroll: Scrolling ]

    # ---------------------------------- [ menu: menu processing ... [
    model.fieldset(
            'menu',
            label=_(u'Menu processing'),
            fields=[
                'menu_item_selector',
                'menu_item_switched_classname',
                ])

    menu_item_selector = schema.BytesLine(
        title=_(u"Selector menu items"),
        default=default['menu_item_selector'],
        missing_value=default['menu_item_selector'],
        description=_(
            u'help_menu_item_selector',
            default=u'When loading new content with AJAX, '
                u'the context indicated by a currently highlighted main menu '
                u'item might be left; '
                u'thus, the main menu must be updated to reflect the change, '
                u'based on the current URL.'
                ))

    menu_item_switched_classname = schema.BytesLine(
        title=_(u"Switched classname"),
        default=default['menu_item_switched_classname'],
        missing_value=default['menu_item_switched_classname'],
        description=_(
            u'help_menu_item_switched_classname',
            default=u'The name of a class which will be '
                u'added to the main menu item to be highlighted '
                u'and removed from all others, '
                u'matching the <main_item_selector>'
                ))
    # ---------------------------------- ] ... menu: menu processing ]

    # ----------------------- [ development: Development support ... [
    model.fieldset(
            'development',
            label=_(u'Development support'),
            fields=[
                'development_mode',
                ## removed; client-side 'mark_links' function triggered additional AJAX requests:
                # 'development_style_delegate',
                # 'development_style_undelegate',
                ])

    development_mode = schema.BytesLine(
        title=_(u"Development mode"),
        default=default['development_mode'],
        missing_value=default['development_mode'],
        description=_(
            u'help_development_mode',
            default=u'In development mode, h1 headlines are bordered '
                u'after loading contents via AJAX; '
                u'furthermore, the "a" elements are styled according to '
                u'the delegation / undelegation logic.\n'
                u'You may specify "on", "off" or "auto"; '
                u'With "auto", this key reflects Zope\'s DevelopmentMode.'
                ))
    # ----------------------- ] ... development: Development support ]

    # -------------------------- [ internal: Internal processing ... [
    model.fieldset(
            'internal',
            label=_(u'Internal processing'),
            fields=[
                'layout4ajax',
                'view4ajax',
                ])

    layout4ajax = schema.Dict(
        title=_(u"Layouts for AJAX"),
        default=default['layout4ajax'],
        missing_value=default['layout4ajax'],
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
        default=default['view4ajax'],
        missing_value=default['view4ajax'],
        key_type=schema.BytesLine(title=_(u'portal_type')),
        value_type=schema.BytesLine(title=_(u'AJAX view')),
        description=_(
            u'help_view4ajax',
            default=u'For each “portal_typeˮ, '
                u'we may map an AJAX version '
                u'corresponding to the standard full-page view.'
                ))
    # -------------------------- ] ... internal: Internal processing ]
