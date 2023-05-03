Changelog
=========


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
    for easier testing (it is a variant of visaplan.tools.minifuncs.NoneOrBool,
    anyway)

New Features:

  - New method ``AjaxLoadBrowserView.get_visible_url``
  - New module ``minifuncs``, mentioned above

[tobiasherp]


1.0.0.3 (2020-03-06)
--------------------

- Hotfixes due to customization problems
  (for internal use).

[tobiasherp]


1.0.0 (2020-03-06)
------------------

- Initial release.
  [tobiasherp]

.. vim: shiftwidth=2 sts=2 expandtab ts=8 tw=79 cc=+1 si
