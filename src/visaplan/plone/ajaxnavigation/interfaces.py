# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface

from visaplan.plone.ajaxnavigation import _


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
