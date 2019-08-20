# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Acquisition import aq_inner

from visaplan.plone.ajaxnavigation.decorators import returns_json

from pdb import set_trace
from visaplan.tools.debug import pp

from visaplan.plone.ajaxnavigation.views import AjaxnavBaseBrowserView
from visaplan.plone.ajaxnavigation.views import EmbedBaseBrowserView


class AjaxnavBrowserView(AjaxnavBaseBrowserView):

    def views_to_try(self, context):
        """
        For folders: call getLayout, and replace the final _view by _embed
        """
        layout = context.getLayout()
        if layout and layout.endswith('_view'):
            liz = layout.split('_')
            yield '_'.join(liz[:-1]+['embed'])
        yield 'folder_content_embed'


class EmbedBrowserView(EmbedBaseBrowserView):

    def children(self):
        context = aq_inner(self.context)
        root = context.absolute_url() + '/'
        children = []
        # no contentFilter for now:
        for o in context.listFolderContents():
            o_id = o.id
            # if necessary: 
            # state = o.restrictedTraverse('@@plone_context_state')
            children.append({
                'href': root + o_id,
                # 'title': state.object_title(),
                'title': o.title,
                })
        return children
