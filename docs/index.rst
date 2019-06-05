=============================
visaplan.plone.ajaxnavigation
=============================

This package adds AJAX navigation to a Plone site, using jQuery.


TL;DR:
~~~~~~

There are two Javascript resources added to the registry:

- ``++resource++visaplan.plone.ajaxnavigation/ajaxnavigation.js``
- ``++resource++visaplan.plone.ajaxnavigation/init-default.js``

If those are loaded by a Plone page, AjaxNav is activated using a simple
standard configuration.


Overview
========

The general idea is:

- Catch the onclick event for every ``a`` element on the page.

- Do some client-side calcuations to determine whether AJAX loading should be
  tried and which URL(s) to use.

  Don't use AJAX
  (and instead immediately return *true* to perform the standard click processing)
  in the following cases:

  - The link target is outside the current site (another hostname is given).
  - The anchor features special attributes
    (CSS classes or ``data-*`` attributes)
    which indicate special handling, e.g. opening a lightbox.
  - A view name is given which is blacklisted by id (e.g. ``edit``),
    prefix (e.g. ``manage_``) or suffix (e.g. ``_edit``).

- If that check concludes, "let's load the target via AJAX",
  it will look for certain elements on the page and try to update them:

  - contents (and e.g. breadcrumbs, if configured)
  - title

  It will also set the page url accordingly, allowing for the browser history.

- The AJAX view was tried (up to two URLs) but failed, the default click
  handling will be performed.


Configuration
=============

Javascript configuration
~~~~~~~~~~~~~~~~~~~~~~~~

The ``AjaxNav`` Javascript object has an ``init`` method which is called when
the document is ready.
It expects a ``key`` argument which is ``default`` by default;
if will then load the configuration from the server by calling the
``@@ajaxnav-options-default`` view.
This view returns a JSON-encoded dictionary; see `Configuration keys`_.

Thus, for customization you have two options:

1. Override the ``ajaxnav-options-default`` view to match your page layout for
   normal pages
2. Add special views, e.g. an ``ajaxnav-options-presentation`` view which
   returns the options to be used by "presentation mode" pages which omit the
   usual site navigation links and use ``AjaxNav.init('presentation')`` instead
   of ``AjaxNav.init('default')``.

The ``ajaxnav-options-*`` views are expected to be implemented for portal
objects and perhaps other navigation roots only.


Content types
-------------

Your content types can be customized by providing the following views:


ajax-nav
++++++++

Returns the data necessary to display the requested object via AJAX as a
JSON-encoded dictionary; see the `Data keys`_.

AjaxNav will send the following information to ``@@ajax-nav`` views:

- The non-AJAX ``href`` value, as ``_given_url``
- The raw ``class`` attribute (if any), as ``_class``
- The HTML5 ``data-*`` attributes (if any), with ``data-`` prefixes.

embed
+++++

Returns the "contents" of the requested object as needed to embed it,
including the ``h[1-6]`` HTML headline element if desired,
but usually excluding e.g. breadcrumbs.

This is a mere convention; you might use calls to ``context@@embed`` to
construct the ``contents`` value of your ``@@ajax-nav`` reply.



AJAX data
~~~~~~~~~

Configuration keys
------------------

These are the keys understood by the ``AjaxNav.init`` function.

======================= ====== =================== ===================
key                     type   default             description
======================= ====== =================== ===================

whitelist               list   [``body``]          CSS selectors of elements
                                                   which contain ``a`` elements
                                                   for the event delegation to be
                                                   applied

blacklist               list   *(empty)*           CSS selectors for elements
                                                   from which the event delegation
                                                   be removed

view_ids                list   [``view``,          For target url parsing:
                               ``edit``,           recognized as view names even
                               ``base_edit``]      when not prefixed by ``@@``

view_suffixes           list   [``_view``]         For target url parsing:
                                                   e.g. ``_view`` does very likely
                                                   end a view name
                                                   rather than an object.

blacklist_view_ids      list   [``edit``,          View ids to suppress AJAX loading
                               ``base_edit``]

blacklist_view_suffixes list   [``_edit``]         View ids to suppress AJAX loading

reply_keys              object {``contents``:      Maps `Data keys`_ to CSS
                                ``#content``}      selectors.  This value
                                                   doesn't contain any
                                                   specifications for
                                                   ``@``-prefixed keys
                                                   (``@url``, ``@title``)
                                                   since those don't apply to
                                                   the page text but have
                                                   special hard-coded meanings.

======================= ====== =================== ===================


Data keys
---------

These are the keys which are expected in the JSON reply from requests to
``@@ajaxnav``.

======== ============ ================================================
Key      Type         Description, remarks
======== ============ ================================================

contents HTML text    The "meat".
                      This key is "special" only in one regard:
                      It is expected to exist.
                      What happens for replies lacking this key
                      is currently undefined.

@title   string       Used to set the title after filling in the contents.

@url     absolute URL Used for history support; usually the URL of the
                      AJAX-loaded page as it would be needed to be given
                      when approaching the page from outside.

======== ============ ================================================

Other keys can be used if they are configured in the ``reply_keys``
configuration value; e.g., you might configure the ``breadcrumbs`` value to
fill the ``#breadcrumbs`` element.

Please use "proper words" for now, avoiding punctuation, whitespace and the
like.  You never know whether those gain some meaning of a sort in the future.

Special keys start with ``@`` and are disallowed unless explicitly documented.


Strategies
==========

Keep low the number of requests
-------------------------------

AjaxNav tries to keep the number of requests to the necessary number, as low as
possible.

Thus, there is one request to load the configuration,
and preferably exactly one (but not more than two) TTW requests for each page.

All required data for the newly loaded pages is returned in a single JSON
reply.


View name detection
-------------------

AjaxNav tries to detect the view name components in the given target urls
to avoid sending invalid requests; it will try to replace it by ``@@ajax-nav``.
This is expected to return JSON data.

For ``.../name/`` urls, ``name`` is assumed to specify the object, and
``@@ajax-nav`` will simply be appended to form the url.

If ``@@`` is found (but not followed by a later ``/``), it will be considered
to be followed by the view name, which will be replaced by ``ajax-nav``.

For cases where the view name cannot be found by these simple rules,
the ``view_*`` keys from the `Configuration keys`_ are used;
if all else fails, the final slash-devided path chunk is first considered
the object name, and if this fails, the (replaced) view name.


Dependencies
============

Plone
-----

This package is written with Plone 4.3 in mind, as the writer of these lines is
currently still on Plone 4.3.

It is quite likely that it will work with earlier versions as well
(provided you use a supported JQuery version).
JQuery is usually integrated using `plone.app.jquery`_.

With Plone 5, the handling of Javascript resources changes, so some changes
are expected to be necessary.  Help with this is appreciated.

For `Volto`_ sites, the whole jQuery-based handling might be obsolete because
of the use of `React.js`_.


Javascript
----------

The `URL()`_ constructor is used for URL parsing.
It is `currently supported`_ by all major current browsers except IE 11 and
Opera Mini.

If an unsupported browser is used (or Javascript switched off), the standard
non-AJAX navigation is expected to work happily.


JQuery
~~~~~~

The jQuery functions on_ and off_ are used to delegate resp. undelegate the ``click`` event.
These have been added to jQuery in version 1.7 and are meant to replace
bind_ / unbind_, delegate_ / undelegate_ as well as the live_ method.
Plone 4.3.* specifies 1.7.2*, so this looks like a safe choice.

The live_ method is deprecated since jQuery 1.7 but still exists in version
1.8.  With ``live`` event handling in place, it is possible that the delegated
events simply won't fire.

You'll want to get rid of ``.live(...)`` method calls anyway if you still have
any.

.. _on: https://api.jquery.com/on/
.. _off: https://api.jquery.com/off/
.. _delegate: https://api.jquery.com/delegate/
.. _undelegate: https://api.jquery.com/undelegate/
.. _bind: https://api.jquery.com/bind/
.. _unbind: https://api.jquery.com/unbind/
.. _live: https://api.jquery.com/live/
.. _`plone.app.jquery`: https://pypi.org
.. _`Volto`: https://volto.kitconcept.com/
.. _`React.js`: https://reactjs.org/
.. _`URL()`: https://developer.mozilla.org/en-US/docs/Web/API/URL/URL
.. _`currently supported`: https://caniuse.com/#search=URL
