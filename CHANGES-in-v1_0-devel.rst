.. Änderungen in Zweig v1_0-devel

1.0-devel (unreleased)
----------------------

Breaking changes:

- Removed the ``decorators`` module;
  it is imported from visaplan.plone.tools_ v1.1.6+ instead.

Bugfixes:

Improvements:

- Python 3 compatibility, using `six`_

New Features:

Profile changes:

- Explicitly enabled ``urlSplit.min.js`` (from visaplan.js.urlsplit_),
  since we currently still need it
- Set profile version to 1003

.. _visaplan.plone.tools: https://pypi.org/project/visaplan.js.urlsplit
.. _visaplan.js.urlsplit: https://pypi.org/project/visaplan.js.urlsplit
.. _six: https://pypi.org/project/six
