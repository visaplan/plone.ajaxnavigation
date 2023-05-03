# -*- coding:utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

# Plone:
from plone.app.registry.browser import controlpanel

# Local imports:
from visaplan.plone.ajaxnavigation import _
from visaplan.plone.ajaxnavigation.interfaces import IAjaxNavigationSettings

__all__ = [
        'AjaxNavigationSettingsEditForm',
        'AjaxNavigationSettingsControlPanel',
        ]

class AjaxNavigationSettingsEditForm(controlpanel.RegistryEditForm):

    """Control panel edit form."""

    schema = IAjaxNavigationSettings
    label = _(u'AJAX navigation')
    description = _(u'Settings for the visaplan.plone.ajaxnavigation package')


class AjaxNavigationSettingsControlPanel(controlpanel.ControlPanelFormWrapper):

    """Control panel form wrapper."""

    form = AjaxNavigationSettingsEditForm
