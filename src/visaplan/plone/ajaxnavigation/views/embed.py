# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Embed(BrowserView):
    template = ViewPageTemplateFile('embed.pt')

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


class EmbedFolderish(Embed):
    template = ViewPageTemplateFile('embed_folderish.pt')

    def __call__(self):
	context = self.context
	# get the accessible child elements:
	self._children(context)
	# There might be texts as well:
	self._texts(context)
        return self.template()

    def _children(self, context):
	root = context.absolute_url() + '/'
	children = self.children = []
	# no contentFilter for now:
	for o in context.listFolderContents():
	    o_id = o.id
	    children.append({
		'href': root + o_id,
		'title': o.title or o_id,
		})
