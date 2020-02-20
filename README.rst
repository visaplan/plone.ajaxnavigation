.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

=============================
visaplan.plone.ajaxnavigation
=============================

Add AJAX navigation to a Plone site.

This is probably not the most advanced or state-of-the-art way to add AJAX
navigation; for Plone 5, I was told about `plone.patternslib`_, based on
`patternslib`_.

For `Volto`_ sites, the whole jQuery-based handling might be obsolete because
of the use of `React.js`_.

At the time of this writing, those were no options for me since I was still on
Plone 4.3.  Thus, I needed a working solution.
Depending on the quality, I'll switch to some Plone-5-ish solution when doing
the leap, or I'll stick with my own.

The general idea is:

- Catch the ``click`` event for every ``a`` element on the page.

- For some links, a special check will tell to proceed with the standard
  behaviour, i.e. load the target the standard way; this includes:

  - Link targets outside of the current site (another hostname is given)
  - Management pages (e.g. starting with ``manage_``)
  - Other pages which don't load the navigation links etc. anyway,
    or wouldn't work when loaded via AJAX
  - Anchor elements with certain attributes
  - Views for contexts which don't have a suitable embedable view yet.

  For such link targets, this function will simply return *true*,
  and the page is loaded in the standard way.

- If that check function concludes, "let's load the target via AJAX",
  it will look for certain elements on the page and try to update them:

  - ``content``

    and, optionally:

  - breadcrumbs
  - other page elements

  It will also set the page url and title accordingly
  (from the ``@url`` and ``@title`` keys of the JSON reply, respectively),
  allowing for the browser history.

- If the tried URLs fail to return a usable JSON answer,
  or if the target URL is inappropriate for other reasons
  (e.g. page-local, or leaving the current site),
  the target page is loaded the normal, non-AJAX way
  (i.e., loading the whole page).


Features
--------

- Tries up to two URLs for each ``a`` element (only one, if the target URL ends
  with "``/``", or if the final path element can be considered a view method
  name rather than an object id)
- Can be configured using the Plone registry.


To do
-----

- Provide ``@@embed`` views for all standard objects.
- Provide ``@@please_login`` and ``@@insufficient_rights`` views.
- Use a `web worker`_.
- Find reliable CSS destination selectors for the ``content``.
- Make this package RequireJS_-aware.


Examples
--------

This add-on is currently under development and not yet used on public internet
sites.


Documentation
-------------

Full documentation for end users can be found in the "docs" folder.


Installation
------------

Install visaplan.plone.ajaxnavigation_ by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.plone.ajaxnavigation


and then running ``bin/buildout``.

Or, more likely:

Add it to the dependencies of your package, e.g. in your ``setup.py`` file.

You'll need to provide ``@@embed`` views for your content types;
ideally, you can use your already-existing ``BrowserView`` classes.
Usually it will be sufficient to make a copy of your ``view`` template
and inject an ``ajax_load=1`` request variable.


Questions
---------

"Why don't you simply inject that ``ajax_load`` variable automatically per BrowserView code?"

Perhaps we will.

"Why don't you drop that ``embed`` view name, and simply use ``view``, with ``ajax_load=1`` injected?

Perhaps we will do so as a fallback option.
But it might be a good idea to be able to do things differently on purpose.

Probably there are several things which could be done better.
Contributions are welcome.


Contribute
----------

- Issue Tracker: https://github.com/visaplan/plone.ajaxnavigation/issues
- Source Code: https://github.com/visaplan/plone.ajaxnavigation


Support
-------

If you are having issues, please let us know;
please use the `issue tracker`_ mentioned above.


License
-------

The project is licensed under the GPLv2 (or later).

.. _`Volto`: https://volto.kitconcept.com/
.. _`React.js`: https://reactjs.org/
.. _`patternslib`: https://patternslib.com/
.. _`plone.patternslib`: https://pypi.org/project/plone.patternslib/
.. _`issue tracker`: https://github.com/visaplan/plone.ajaxnavigation/issues
.. _`web worker`: https://html.spec.whatwg.org/multipage/workers.html#workers
.. _RequireJS: https://requirejs.org/
.. _visaplan.plone.ajaxnavigation: https://pypi.org/project/visaplan.plone.ajaxnavigation

.. vim: tw=79 cc=+1 sw=4 sts=4 si et
