# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class EmbedTextual(BrowserView):
    template = ViewPageTemplateFile('embed_at_textual.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _texts(self, context):
	lst = self.content_values = []

	try:
	    val = context.description
	except AttributeError:
	    pass
	else:
	    lst.append({
		'cls': 'description',
		'content': val.strip() or None,
		})

	try:
	    val = context.text
	except AttributeError:
	    pass
	else:
	    lst.append({
		'cls': 'text',
		'content': val.strip() or None,
		})

    def __call__(self):
	context = self.context
	self._texts(context)

        return self.template()
