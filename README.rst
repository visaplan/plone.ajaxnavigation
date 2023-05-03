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
  - Anchor elements with certain attributes (``data-fullpage-only="true"``)
  - Views for contexts which don't have a suitable embedable view yet.

  For such link targets, this function will simply return *true*,
  and the page is loaded in the standard way.

- If that check function concludes, "let's load the target via AJAX",
  it will send a request to an ``.../@@ajax-nav`` address which will return
  all necessary JSON data; using the result,
  it will look for certain elements on the page and try to update them:

  - ``#content`` (the target for ``content`` as of the default configuration)

  and, optionally:

  - breadcrumbs
  - other page elements, like context specific search forms.

  It will also set the page url and title accordingly
  (from the ``@url`` and ``@title`` keys of the JSON reply, respectively),
  allowing for the browser history.

- If the tried URLs fail to return a usable JSON answer,
  or if the target URL is inappropriate for other reasons
  (e.g. page-local, or leaving the current site),
  the target page is loaded the normal, non-AJAX way
  (i.e., loading the whole page).

- All hyperlinks will *continue* to work with Javascript switched off;
  of course, pages will load faster when switched on.


Features
--------

- Tries up to two URLs for each ``a`` element (only one, if the target URL ends
  with "``/``", or if the final path element can be considered a view method
  name rather than an object id)
- Can be configured using the Plone registry:

  - ``target`` attributes of ``a`` elements are regarded *by default*,
    following the `Principle of Least Surprise`_.
    However, you are encouraged to disregard them, since the use of this
    attribute is not recommended.
  - By default, ``a[target]`` elements are secured by adding to them a ``rel``
    value of noopener_.


To do
-----

- Use a `web worker`_.
- Make this package RequireJS_-aware.
- Provide support for additional search configurations.
- Pick values from contents to be replaced, and re-insert them
  (e.g. search expressions in context specific search forms).


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


Questions
---------

"What about my view templates?"

If your view templates don't inject Javascript code in the HTML head element
(e.g. filling the ``head_slot`` or ``javascript_head_slot``) but rather add it
to the body, chances are good that they will just work fine.

If they don't, you have the following choices:

- Refactor your view templates and move the script code from the head to the
  body (which should be a good idea anyway);

- Provide special ``@@embed`` views which would be tried first by the
  ``@@ajax-nav`` view;

- Suppress AJAX navigation for the respective views and load it the standard
  way (full page).

"Why don't you simply inject that ``ajax_load`` variable
automatically per BrowserView code?"

Yes, we do so already.

There is a simple ``.views.AjaxLoadBrowserView`` class which takes care of
this, and a few subclasses.

"Why don't you drop that ``embed`` view name, and simply use ``view``,
with ``ajax_load=1`` injected?

We do so as a fallback option.
But some of our pages simply don't work this way
(e.g. because some necessary scripts are loaded in a METAL slot
which is dropped if ``ajax_load`` is found true),
so we need to be able to be explicit.

Thus, an ``..._embed`` view is used, if present, and then the standard view
jumps in as a fallback.

The visaplan.plone.ajaxnavigation package was developed as a drop-in solution
for sites which might not do everything right already.
If your site works fine with ``ajax_load`` injected, you'll need to do less
customization work to make it run.

Quite probably there are several things which could be done better.
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
.. _`Principle of Least Surprise`: https://en.wikipedia.org/wiki/Principle_of_least_astonishment
.. _noopener: https://mathiasbynens.github.io/rel-noopener/

.. vim: tw=79 cc=+1 sw=4 sts=4 si et
