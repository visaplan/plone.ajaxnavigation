# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from visaplan.plone.ajaxnavigation.interfaces import (
	IAjaxNavigationClientSettings, IAjaxNavigationInternalSettings,
	)
from plone.z3cform import layout
from z3c.form import form


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
