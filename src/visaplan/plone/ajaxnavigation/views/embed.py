# -*- coding: utf-8 -*-

from visaplan.plone.ajaxnavigation import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Embed(BrowserView):
    template = ViewPageTemplateFile('embed.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
	context = self.context
	lst = self.content_values = []

	try:
	    val = context.description
	except AttributeError:
	    pass
	else:
	    lst.append({
		'cls': 'description',
		'content': val.strip() or None,
		}

	try:
	    val = context.text
	except AttributeError:
	    pass
	else:
	    lst.append({
		'cls': 'text',
		'content': val.strip() or None,
		}

        return self.template()
