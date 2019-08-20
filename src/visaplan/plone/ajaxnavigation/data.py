# -*- coding: utf-8 -*-
from Products.CMFCore.permissions import (
        ManagePortal,
        ModifyPortalContent,
        )
from Products.Sessions.SessionPermissions import (
        ACCESS_CONTENTS_PERM as Access_contents_information,
        )
from Products.PlonePAS.permissions import (ManageGroups,
        )
from AccessControl.Permissions import (
        manage_users,             # Manage users
        view as view_permission,  # View
        )

from visaplan.tools.classes import AliasDict

from visaplan.plone.ajaxnavigation.interfaces import IAjaxNavigationSettings

_prefix = IAjaxNavigationSettings.__identifier__ + '.'

clientside_map = {
        key: _prefix + key
        for key in (
                'whitelist',
                'blacklist',
                'nested_blacklist',
                'view_ids',
                'view_prefixes',
                'view_suffixes',
                'blacklist_view_ids',
                'blacklist_view_prefixes',
                'blacklist_view_suffixes',
                'selectors',
                )}

internal_map = {
        key: _prefix + key
        for key in (
                'layout4ajax',
                'view4ajax',
                )}

all_keys = clientside_map.keys() + \
        internal_map.keys()

PERMISSION_ALIASES = AliasDict({
        'view':          view_permission,
        'edit':          ModifyPortalContent,
        'info':          Access_contents_information,
        'manage':        ManagePortal,
        'manage_groups': ManageGroups,
        'manage_users':  manage_users,
        })
