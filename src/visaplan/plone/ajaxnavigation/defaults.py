# -*- coding: utf-8 -*-

default = {
    'selectors': {
        'content': "#content",
        },
    'whitelist': [
        'body',
        ],
    'blacklist': [],
    'nested_blacklist': False,
    'view_ids': [
        'view',
        'edit',
        'base_edit',
        'manage',
        ],
    'view_prefixes': [
        'manage_',  # see as well --> blacklist_view_prefixes
        ],
    'view_suffixes': [
        '_edit',
        '_view',
        ],
    'blacklist_view_ids': [
        'base_edit',
        'edit',
        'logout',  # logout might affect the top menu, so load whole page
        'manage',  # ZMI -- a beast of it's own
        ],
    'blacklist_view_prefixes': [
        'configure_',
        'configure-',
        'manage_',  # usually: ZMI pages
        'plone_',
        'portal_',
        'prefs_',
        ],
    'blacklist_view_suffixes': [
        '_management',
        ],
    'blacklist_class_ids': [
        'lightbox',
        ],
    'blacklist_class_prefixes': [
        '@novalue',
       ],
    'blacklist_class_suffixes': [
        '@novalue',
        ],
    'regard_target_attribute': True,
    'target_rel_values': [
        'noopener',
        ],
    'scrollto_default_selector': None,
    'scrollto_default_deltay': 0,
    'scrollto_auto_key': 'content',
    'menu_item_selector': '.mainmenu-item > a',
    'menu_item_switched_classname': 'selected',
    'development_mode': 'auto',
    'layout4ajax': {},
    'view4ajax': {},
    }
