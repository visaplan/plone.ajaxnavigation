# -*- coding: utf-8 -*- äöü vim: ts=8 sts=4 sw=4 si et tw=79 cc=+1
# Python compatibility:
from __future__ import absolute_import

# Logging / Debugging:
from logging import getLogger

logger = getLogger(__package__)
try:
    # visaplan:
    from visaplan.plone.breadcrumbs.base import NoCrumbs, register
except ImportError as e:
    logger.info(str(e))
else:
    register('ajax-nav', NoCrumbs)
    logger.info('Registered "ajax-nav" to have no breadcrumbs')
