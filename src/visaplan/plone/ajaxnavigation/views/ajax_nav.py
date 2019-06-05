# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

from visaplan.plone.ajaxnavigation.decorators import returns_json


class AjaxNav(BrowserView):

    @returns_json
    def __call__(self):
	"""
	Return JSON data for AJAX navigation.

	Return "nothing" if no @@embed view is available.
	Return False if no URL is given.
	"""
	context = self.context
	tmpl = context.restrictedTraverse('@@embed')
	if tmpl is None:
	    return None
	request = context.REQUEST
	form = request.form

	# without a given URL, there probably won't be anything to do for us:
	given_url = form.pop('_given_url', None)
	if not given_url:
	    return False

	content = tmpl(**form)
	title = context.title
	return {
	    'content': content,
	    '@title': title,
	    '@url': url,
	    }
