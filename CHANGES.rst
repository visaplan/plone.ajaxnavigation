Changelog
=========


1.2.3 (2021-12-20)
------------------

Bugfixes:

- Javascript code:

  - Declare ``reply_ok`` in ``AjaxNav.process_data`` as well

Temporary changes:

- Added to ``blacklist_view_ids``:

  - ``structure-edit`` (visaplan.plone.structures)

[tobiasherp]


1.2.2 (2021-08-25)
------------------

Bugfixes:

- Corrected an import in the ``.helpers`` module

[tobiasherp]


1.2.1 (2021-07-09)
------------------

Bugfixes:

- Missing import in .views._load module

Improvements:

- _get_tool_1 catches TypeError exceptions for getToolByName

[tobiasherp]


1.2.0 (2021-06-30)
------------------

Bugfixes:

- NameError fixed for NoAjaxBrowserView.__call__
- NoAjaxBrowserView didn't return the JSON data in some cases

New Features:

- New ``helper`` module:

  - Method `getAjaxSettingsProxy` to get the settings
  - Method `updateAjaxSettings` to simplify changes
    (including a call to the former)

Improvements:

- AjaxnavBrowserView can be extended more easily by providing the `._usual_data`
  and `._data_complete` methods

Requirements:

- visaplan.tools v1.3.1+ because of the `ChangesCollector` utility class

- If zope.deprecations is installed, imports from old locations are still
  possible (see below)

Miscellaneous:

- Moved the exception classes to a dedicated ``.exceptions`` module

  - The `Error` root exception was renamed to `AjaxnavError`

- Renamed the `AjaxnavBaseBrowserView` to `AjaxnavBrowserView`. We have two
  classes of this name now

- Renamed the .views.ajaxnav_options module to .views.options

- Since the menu support can be done in a generic way now
  (see the `AjaxnavBrowserView` classes in visaplan.plone.menu),
  the special Javascript code was removed;
  the only exception:

  - Temporarily injected the selector for ``mainmenu`` into the Javascript code
    ([main-menu]@38061)

[tobiasherp]


1.1.0.5 (2020-07-02)
--------------------

Improvements:

- Tolerate ``getLayout`` AttributeErrors and log an error in such cases.
  These probably indicate wrong usage, but we don't want the whole thing to crash.

[tobiasherp]


1.1.0.4 (2020-05-13)
--------------------

Breaking changes:

- The helper function `_get_tool_1` now *always* expects the request
  to be specified as the 3rd argument.
  This has been optional which seems to have been a bad idea.
- Same for the method ``.views.AjaxLoadBrowserView.get_visible_url``

Bugfixes:

- Typo corrected (``urlSplit``)

[tobiasherp]


1.1.0.3 (2020-04-07)
--------------------

- Blacklisted some more ``a`` element classes to make
  the course editor work again (visaplan.plone.elearning_)

[tobiasherp]


1.1.0.2 (2020-04-03)
--------------------

Bugfixes:

- ``ToolNotFound`` exceptions are now caught
  by the ``AjaxnavBaseBrowserView.choose_view`` method.

Profile changes:

- There are no blacklisted view id prefixes now anymore by default
  (``blacklist_view_prefixes``); those views can in fact work quite well now.
- Profile version increased to 3.

[tobiasherp]


1.1.0.1 (2020-03-31)
--------------------

New features:

- New settings (client-side only, so far):

  - ``replace_view_ids``
  - ``replaced_view_ids``
  - ``dropped_view_ids``

- All other changes of release 1.1.0

- Hardcoded configuration changes
  (for internal use).

[tobiasherp]


1.1.0 (unreleased)
------------------

New Features:

- New setting ``replace_view_ids`` (default: `false`)
- New setting ``replaced_view_ids``;
  by default, and if ``replace_view_ids`` is `true`,
  replace

  - ``replaceUid`` by ``@@replaceuid``
  - ``replacei18n`` by ``@@replaceuid``

- New setting ``dropped_view_ids`` (default: ``['view']``;
  generalization of the special treatment of ``.../view`` URLs
  from release 1.0.2)
- New wrapper ``AjaxNav.urlSplit``

  - to fix issues with ``urlSplit``:

    - fragments are detected but remain in the `fileName`
    - relative URLs not treated correctly,
      including "invention" of a ``.`` `domain`

  - to perform view ids replacement if configured (see above)

- New server-side methods:

  - ``AjaxLoadBrowserView.get_given_viewname``

Bugfixes:

- Consider fragments when constructing ``.../@@ajax-nav`` URLs


1.0.2.1 (2020-03-27)
--------------------

- Includes all changes of version 1.0.2

- Hardcoded configuration changes
  (for internal use).

[tobiasherp]


1.0.2 (2020-03-27)
------------------

Bugfixes:

- Use of default pages (of folders) should work now
- If a visible ``.../@@ajax-nav`` url is found, we have the JSON url already
  and thus strip this trailing part; otherwise we'd display the JSON data
  rather than perform the intended page update.

  There are server-side measures to help prevent such urls as well,
  since we don't want people to see and use them.
- ``.../view`` URLs are treated specially as well - the ``/view``
  is considered a non-information (just use the standard view) in this regard.
  Thus, URLs ending with ``/view`` are treated the same
  as those ending with ``/``.

[tobiasherp]


1.0.1.1 (2020-03-24)
--------------------

- Includes all changes of version 1.0.1

- Hardcoded configuration changes
  (for internal use).

[tobiasherp]


1.0.1 (2020-03-24)
------------------

Improvements:

- in client-side code:

  - UIDs in paths are recognised (to be retained, and not mistaken as a possible view name)

- in server-side code:

  - AjaxNav-generated information (``viewname``, ``visible_url``) is available
    in every browser view based on ``AjaxLoadBrowserView`` (which includes
    ``AjaxnavBaseBrowserView`` and - new ``NoAjaxBrowserView``)

  - ``NoAjaxBrowserView`` performs permission checks to allow for fast login
    prompts or error information (the full page is needed only once)

  - Moved function ``NoneOrBool`` from ``utils`` to new ``minifuncs`` module,
    for easier testing (it is a variant of `visaplan.tools`_.minifuncs.NoneOrBool,
    anyway)

New Features:

  - New method ``AjaxLoadBrowserView.get_visible_url``
  - New module ``minifuncs``, mentioned above

[tobiasherp]


1.0.0.3 (2020-03-06)
--------------------

- Hotfixes due to customization problems.

[tobiasherp]


1.0.0 (2020-03-06)
------------------

- Initial release.
  [tobiasherp]

.. _visaplan.plone.elearning: https://pypi.org/project/visaplan.plone.elearning
.. _visaplan.tools: https://pypi.org/project/visaplan.tools

.. vim: shiftwidth=2 sts=2 expandtab ts=8 tw=79 cc=+1 si
