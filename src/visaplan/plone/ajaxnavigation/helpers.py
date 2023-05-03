"""\
visaplan.plone.ajaxnavigation: Add AJAX navigation to a Plone site.

Short description
"""
# Python compatibility:
from __future__ import absolute_import

# Zope:
from zope.component import getUtility

# Plone:
from plone.registry.interfaces import IRegistry

# visaplan:
from visaplan.tools.dicts import ChangesCollector
from visaplan.tools.minifuncs import check_kwargs

# Local imports:
from .interfaces import IAjaxNavigationSettings

__all__ = [
    'getAjaxSettingsProxy',
    'updateAjaxSettings',
    ]


def getAjaxSettingsProxy(**kwargs):
    """
    Return a registry  proxy which contains a complete set of AjaxNavigation
    configuration variables.

    The default set is returned to the client via @@ajaxnav-options-default,
    but no prefix is used in this case; thus, we normalize "default" to None
    here, and any other value must be a trueish string
    (which should contain ASCII lower-case letters only).

    Keyword-only options:

    key -- By default None (or 'default'), which means, the interface itself is
           used without a prefix (IAjaxNavigationSettings.__identifier__ is
           used)

    register -- register the interface, initializing (or validating) the values
    """
    registry = getUtility(IRegistry)
    pop = kwargs.pop
    key = pop('key', None)
    register = pop('register', 0)
    check_kwargs(kwargs)
    if key is None:
        prefix = None
    elif key == 'default':
        key = None
        prefix = None
    else:
        key = key.strip().lower()
        if key == 'default':
            prefix = None
            return registry.forInterface(IAjaxNavigationSettings)
        elif not key:
            raise ValueError('Non-empty lowercase key expected; got %(key)r!'
                             % locals())
        prefix = 'visaplan.plone.ajaxnavigation.layout.' + key

    if register:
        # tries to retain existing values;
        # no checking before should be necessary:
        registry.registerInterface(IAjaxNavigationSettings,
                                   prefix=prefix)

    return registry.forInterface(IAjaxNavigationSettings,
                                 prefix=prefix)


def updateAjaxSettings(*args, **kwargs):
    """
    Update the AJAX settings with the given key (like for getAjaxSettingsProxy,
    above) with a sequence of dictionaries (last-seen wins).

    For fields which contain lists, a dictionary is expected which may contain
    one or more lists of the following:

    - 'add' - contains values to be added
    - 'remove' - contains values to be removed

    Not implemented (yet?):
    - 'set' - contains the complete set of new values
              (not combinable with other keys)
    - 'change' - a sequence of (old, new) tuples:
                 if `old` is found, replace it by `new`

    Arguments:

    *args - the sequence of dicts, like described above
    **kwargs - specifies which set of settings to update
               (forwarded to getAjaxSettingsProxy, above)
    """
    proxy = getAjaxSettingsProxy(**kwargs)
    changes = ChangesCollector(args[0])
    for chg in args[1:]:
        changes.update(chg)
    proxy.update(changes.frozen(proxy))
