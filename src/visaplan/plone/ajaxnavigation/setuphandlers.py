# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

# Zope:
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer

# Plone:
from plone.app.upgrade.utils import loadMigrationProfile
from Products.CMFPlone.interfaces import INonInstallable

# visaplan:
from visaplan.plone.tools.setup import load_and_cook, step

# Local imports:
from .defaults import default
from visaplan.plone.ajaxnavigation.interfaces import IAjaxNavigationSettings

# Logging / Debugging:
import logging
from visaplan.tools.debug import pp

# ------------------------------------------------------ [ Daten ... [
__author__ = """Tobias Herp <tobias.herp@visaplan.com>"""
__docformat__ = 'plaintext'

# UNITRACC_PORTAL_TYPES_1000 = UNITRACC_PORTAL_TYPES[:17]

PROJECTNAME = 'visaplan.plone.ajaxnavigation'
PROFILE_ID = PROJECTNAME + ':default'
LOGGER_LABEL = PROJECTNAME + ': setuphandlers'
# ------------------------------------------------------ ] ... Daten ]

logger = logging.getLogger(LOGGER_LABEL)


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            PROJECTNAME + ':uninstall',
        ]


def post_install(context):
    """Post install script"""
    logger.info('Installation complete')

    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


@step
def register_settings_interface(context, logger=logger):
    """
    The interface must be registered explicitly;
    otherwise we'll get errors because of missing values!
    """
    registry = getToolByName(context, 'portal_registry')
    registry.registerInterface(IAjaxNavigationSettings)
    logger.info('Registered interface %r', IAjaxNavigationSettings)


# ------------------------ [ Migrationsschritte, ./profiles.zcml ... [
@step
def reload_gs_profile(context, logger=logger):
    loadMigrationProfile(
        context,
        'profile-visaplan.plone.ajaxnavigation:default',
        )

@step
def load_and_cook_javascript(context, logger):
    load_and_cook(context, logger,
                  profile='profile-visaplan.plone.ajaxnavigation:default',
                  tuples=[('jsregistry',  'portal_javascripts')])
# ------------------------ ] ... Migrationsschritte, ./profiles.zcml ]
