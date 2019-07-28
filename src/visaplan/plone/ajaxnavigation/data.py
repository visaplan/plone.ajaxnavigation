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
