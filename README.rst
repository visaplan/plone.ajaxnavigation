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

- Catch the onclick event for every ``a`` element on the page.
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

- If that check function says, "let's load the target via AJAX",
  it will look for certain elements on the page and try to update them:

  - content
  - breadcrumbs
  - title

  It will also set the page url accordingly, allowing for the browser history.



Features
--------

- Can be bullet points


Examples
--------

This add-on is currently under development and not yet used on public internet
sites.


Documentation
-------------

Full documentation for end users can be found in the "docs" folder.


Installation
------------

Install visaplan.plone.ajaxnavigation by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.plone.ajaxnavigation


and then running ``bin/buildout``


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

.. vim: tw=79 cc=+1 sw=4 sts=4 si et
