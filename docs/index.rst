=============================
visaplan.plone.ajaxnavigation
=============================

This package adds AJAX navigation to a Plone site, using jQuery.


TL;DR:
======

There are two Javascript resources added to the registry:

- ``++resource++visaplan.plone.ajaxnavigation/ajaxnavigation.js``
- ``++resource++visaplan.plone.ajaxnavigation/init-default.js``

If those are loaded by a Plone page, AjaxNav is activated using a simple
standard configuration.


Overview
========

The general idea is:

- Catch the ``click`` event for every ``a`` element on the page.

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

  - ``content`` (and e.g. breadcrumbs, if configured)

  It will also set the page url and title accordingly
  (from the ``@url`` and ``@title`` keys of the JSON reply, respectively),
  allowing for the browser history.

- If the AJAX view was tried (up to two ``.../@@ajax-nav`` URLs) but failed,
  the default click handling will be performed.


Configuration
=============

Javascript configuration
------------------------

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
~~~~~~~~

Returns the data necessary to display the requested object via AJAX as a
JSON-encoded dictionary; see the `Data keys`_.

AjaxNav will send the following information to ``@@ajax-nav`` views:

- The non-AJAX ``href`` value, as ``_given_url``
- The raw ``class`` attribute (if any), as ``_class``
- The HTML5 ``data-*`` attributes (if any), with ``data-`` prefixes.

The default implementation of the ``@@ajax-nav`` view is ``Zope.public``;
it checks whether the object is viewable to the current user and uses
one of the following views to fill the ``content`` key of the JSON reply:

- ``@@embed``
- ``@@please_login``
- ``@@insufficient_rights``


embed
~~~~~

Returns the "contents" of the requested object as needed to embed it,
including the ``h[1-6]`` HTML headline element if desired,
but perhaps excluding e.g. breadcrumbs.


AJAX data
---------

Configuration keys
------------------

These are the keys understood by the ``AjaxNav.init`` function.

+---------------------------+--------+-------------------------------+----------------------------------------+
| Key                       | Type   | Default                       |   Description                          |
+===========================+========+===============================+========================================+
| whitelist                 | list   | [``body``]                    |   CSS selectors of elements            |
|                           |        |                               |   which contain ``a`` elements         |
|                           |        |                               |   for the event delegation to be       |
|                           |        |                               |   applied                              |
+---------------------------+--------+-------------------------------+----------------------------------------+
| blacklist                 | list   | *(empty)*                     |   CSS selectors for elements           |
|                           |        |                               |   from which the event delegation      |
|                           |        |                               |   be removed                           |
+---------------------------+--------+-------------------------------+----------------------------------------+
| nested_blacklist          | boolean| *false*                       | Regard the blacklist selectors         |
|                           |        |                               | "below" the whitelist selectors        |
|                           |        |                               | and undelegate immediately             |
|                           |        |                               | (experimental)                         |
+---------------------------+--------+-------------------------------+----------------------------------------+
| view_ids                  | list   | [``view``,                    |   For target url parsing:              |
|                           |        | ``edit``,                     |   recognized as view names even        |
|                           |        | ``base_edit``]                |   when not prefixed by ``@@``          |
+---------------------------+--------+-------------------------------+----------------------------------------+
| view_prefixes             | list   | [``manage_``]                 |   For target url parsing:              |
|                           |        |                               |   e.g. ``manage_`` does very likely    |
|                           |        |                               |   start a view name                    |
|                           |        |                               |   rather than an object.               |
+---------------------------+--------+-------------------------------+----------------------------------------+
| view_suffixes             | list   | [``_view``]                   |   For target url parsing:              |
|                           |        |                               |   e.g. ``_view`` does very likely      |
|                           |        |                               |   end a view name                      |
|                           |        |                               |   rather than an object.               |
+---------------------------+--------+-------------------------------+----------------------------------------+
| blacklist_view_ids        | list   | [``edit``, ``base_edit``]     |   View ids to suppress AJAX loading    |
+---------------------------+--------+-------------------------------+----------------------------------------+
| blacklist_view_prefixes   | list   |  [``manage_``]                |                                        |
+---------------------------+--------+-------------------------------+----------------------------------------+
| blacklist_view_suffixes   | list   |  [``_edit``]                  |                                        |
+---------------------------+--------+-------------------------------+----------------------------------------+
| selectors                 | object | {``content``:                 | Maps `Data keys`_ to CSS               |
|                           |        | ``#region-content,#content``} | selectors.  This value doesn't         |
|                           |        |                               | contain any specifications for         |
|                           |        |                               | ``@``-prefixed keys                    |
|                           |        |                               | (``@url``, ``@title``, ``@ok``)        |
|                           |        |                               | since those don't apply to             |
|                           |        |                               | the page text but have                 |
|                           |        |                               | special hard-coded meanings.           |
|                           |        |                               |                                        |
|                           |        |                               | The values are strings; however,       |
|                           |        |                               | since jQuery allows multiple           |
|                           |        |                               | selectors in the string, separated by  |
|                           |        |                               | comma, we do so as well and process    |
|                           |        |                               | them in order (e.g., fill              |
|                           |        |                               | ``#region-content``, if present, and   |
|                           |        |                               | otherwise ``#region``).                |
+---------------------------+--------+-------------------------------+----------------------------------------+
| scrollto_default_selector | string | *null*                        | Default for the ``@scrollto`` key      |
+---------------------------+--------+-------------------------------+----------------------------------------+
| scrollto_default_deltay   | int    | 0                             | Default vertical offset for            |
|                           |        |                               | ``@scrollto``                          |
+---------------------------+--------+-------------------------------+----------------------------------------+
| scrollto_auto_key         | string | ``content``                   | Default key for ``@auto``:             |
|                           |        |                               | if ``@scrollto`` is ``@auto``, use     |
|                           |        |                               | the ``selectors`` mapped to            |
|                           |        |                               | the ``content`` AJAX data              |
|                           |        |                               | key by default                         |
|                           |        |                               |                                        |
+---------------------------+--------+-------------------------------+----------------------------------------+



Data keys
---------

These are the keys which are expected in the JSON reply from requests to
``@@ajaxnav``.

+--------------------+-------------+-------------------------------------------------------------+
| Key                | Type        | Description, remarks                                        |
+====================+=============+=============================================================+
| content            | HTML text   | The "meat".                                                 |
|                    |             | This key is "special" only in one regard:                   |
|                    |             | It is expected to exist.                                    |
|                    |             | What happens for replies lacking this key                   |
|                    |             | is currently undefined.                                     |
+--------------------+-------------+-------------------------------------------------------------+
| @title             | string      | Used to set the title after filling in the ``content``.     |
+--------------------+-------------+-------------------------------------------------------------+
| @url               | absolute URL| Used for history support; usually the URL of the            |
|                    |             | AJAX-loaded page as it would be needed to be given          |
|                    |             | when approaching the page from outside.                     |
+--------------------+-------------+-------------------------------------------------------------+
| @ok                | boolean     | Specify *False* to suppress the ``@url`` and ``@title``     |
|                    |             | processing even after successfully inserting HTML text.     |
+--------------------+-------------+-------------------------------------------------------------+
|                    |             | Might be used e.g. for restricted objects the current       |
|                    |             | user is not allowed to view; in such cases you might want   |
|                    |             | to show a login form instead.                               |
+--------------------+-------------+-------------------------------------------------------------+
| @scrollto          | string      | A CSS selector as a scroll target for the                   |
|                    |             | `jQuery scrollTop function`_; default: *none*.              |
|                    |             |                                                             |
|                    |             | When loading new content by clicking on a hyperlink         |
|                    |             | somewhere down the page, the contents could be loaded       |
|                    |             | unnoticed. To prevent this, we scroll up or, if a           |
|                    |             | ``@scrollto`` value is given, to that element.              |
|                    |             |                                                             |
|                    |             | If ``@auto``, the ``selector`` mapped to                    |
|                    |             | the ``scrollto_auto_key`` is used (see above).              |
|                    |             |                                                             |
|                    |             | Use with care; it might not work as expected                |
|                    |             | for multiple CSS selectors (separated by comma).            |
|                    |             |                                                             |
|                    |             | If *none*, the plain-Javascript method ``window.scrollTo``  |
|                    |             | is used.                                                    |
+--------------------+-------------+-------------------------------------------------------------+
| @prefered-selectors| dict of     | Used to redirect the ``content`` (and other data keys)      |
|                    | lists       | to other, prefered selectors, if they are available.        |
|                    |             |                                                             |
|                    |             | Can be used to test new selectors.                          |
+--------------------+-------------+-------------------------------------------------------------+

Other keys can be used if they are configured in the ``selectors``
configuration value;
e.g., if your ``@@embed`` views don't provide breadcrumbs,
you might configure the ``breadcrumbs`` value
to fill the ``#breadcrumbs`` element.

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

The original `href` URL of the clicked `a` element is forwarded to the
``@@ajax-nav`` view  in the `_given_url` request variable.


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
are expected to be necessary; e.g., to establish RequireJS_ support.
Help with this is appreciated.

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

The jQuery functions on_ and off_ are used
to delegate resp. undelegate the ``click`` event.
These have been added to jQuery in version 1.7 and are meant to replace
bind_ / unbind_, delegate_ / undelegate_ as well as the live_ / die_ methods.
Plone 4.3.* specifies 1.7.2*, so this looks like a safe choice.

The live_ / die_ methods are deprecated since jQuery 1.7
but still exist in version 1.8.
With ``live`` event handling in place,
it is possible that the delegated events simply won't fire.

You'll want to get rid of ``.live(...)`` method calls anyway if you still have
any.

The `jQuery scrollTop function`_ was added in version 1.2.6.


Web Workers
~~~~~~~~~~~

We intend to use HTML5 "`web workers`_" to optimize performance.
These should be safe to use at the time of this writing;
see `Can I use web workers?`_.


.. _on: https://api.jquery.com/on/
.. _off: https://api.jquery.com/off/
.. _delegate: https://api.jquery.com/delegate/
.. _undelegate: https://api.jquery.com/undelegate/
.. _bind: https://api.jquery.com/bind/
.. _unbind: https://api.jquery.com/unbind/
.. _live: https://api.jquery.com/live/
.. _die: https://api.jquery.com/die/
.. _`jQuery scrollTop function`: https://api.jquery.com/scrollTop/#scrollTop2
.. _`plone.app.jquery`: https://pypi.org
.. _`Volto`: https://volto.kitconcept.com/
.. _`React.js`: https://reactjs.org/
.. _`URL()`: https://developer.mozilla.org/en-US/docs/Web/API/URL/URL
.. _`currently supported`: https://caniuse.com/#search=URL
.. _`web workers`: https://html.spec.whatwg.org/multipage/workers.html#workers
.. _`Can I use web workers?` : https://caniuse.com/#search=web%20workers
.. _RequireJS: https://requirejs.org/
