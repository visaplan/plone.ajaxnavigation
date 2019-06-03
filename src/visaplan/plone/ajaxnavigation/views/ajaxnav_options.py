# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

from visaplan.plone.ajaxnavigation.utils import options_dict
from visaplan.plone.ajaxnavigation.decorators import returns_json


class AjaxnavOptions(BrowserView):

    @returns_json
    def __call__(self):
        """
        Default options for AjaxNav

        (@@ajaxnav-options-default)
        """
        return options_dict()
