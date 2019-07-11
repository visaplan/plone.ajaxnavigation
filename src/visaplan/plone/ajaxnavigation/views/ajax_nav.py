# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

from visaplan.plone.ajaxnavigation.decorators import returns_json


class AjaxNav(BrowserView):

    def getContent(self, context, form):
        tmpl = context.restrictedTraverse('@@embed')
        if tmpl is None:
            return None
        return tmpl(**form)

    @returns_json
    def __call__(self):
        """
        Return JSON data for AJAX navigation.

        Return "nothing" if no @@embed view is available.
        Return False if no URL is given.
        """
        context = self.context
        request = context.REQUEST
        form = request.form

        # without a given URL, there probably won't be anything to do for us:
        given_url = form.pop('_given_url', None)
        if not given_url:
            return False

        content = self.getContent(context, form)
        if not content:
            return None

        title = context.title
        return {
            'content': content,
            '@title': title,
            '@url': url,
            }

class AjaxNav4Folder(AjaxNav):

    def getContent(self, context, form):
        """
        For folders: call getLayout, and replace the final _view by _embed
        """
        layout = context.getLayout()
        if layout and layout.endswith('_view'):
            liz = layout.split('_')
            layout = '_'.join(liz[:-1]+['embed'])
            tmpl = context.restrictedTraverse('@@'+layout)
            if tmpl:
                return tmpl(**form)

