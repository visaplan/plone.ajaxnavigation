# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

# Zope:
from z3c.form import form

# Plone:
from plone.app.registry.browser.controlpanel import (
    ControlPanelFormWrapper,
    RegistryEditForm,
    )
from plone.z3cform import layout

# Local imports:
from visaplan.plone.ajaxnavigation.interfaces import (
    IAjaxNavigationClientSettings,
    IAjaxNavigationInternalSettings,
    )


class AjaxNavigationClientControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IAjaxNavigationClientSettings

AjaxNavigationClientControlPanelView = layout.wrap_form(
		AjaxNavigationClientControlPanelForm, ControlPanelFormWrapper)
AjaxNavigationClientControlPanelView.label = u"AjaxNavigation client settings"


class AjaxNavigationInternalControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = IAjaxNavigationInternalSettings

AjaxNavigationInternalControlPanelView = layout.wrap_form(
		AjaxNavigationInternalControlPanelForm, ControlPanelFormWrapper)
AjaxNavigationInternalControlPanelView.label = u"AjaxNavigation internal settings"
