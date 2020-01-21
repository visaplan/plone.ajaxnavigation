/* visaplan.plone.ajaxnavigation: AJAX navigation for Plone sites
 * Copyright (C) 2019  visaplan GmbH, Bochum, Germany
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
urlSplit.prototype.toString = function urlSplitToString () {
	var result='', tmp=this.protocol;
	if (tmp)
		result += tmp + ':';
	tmp = this.authorization;
	if (tmp)
		result += tmp + '@';
	tmp = this.domain;
	if (tmp)
		result += tmp;
	tmp = this.port;
	if (tmp)
		result += ':'+tmp;
	tmp = this.path;
	if (tmp)
		result += tmp;
	tmp = this.query;
	if (tmp)
		result += '?'+tmp;
	tmp = this.fragment;
	if (tmp)
		result += '#'+tmp;
	return result;
}
var AjaxNav = (function () {
	var AjaxNav = {},
	    DEBUG_DOTTED = true,
	    log = function (txt) {
		if (typeof console !== 'undefined' &&
			    typeof console.log === 'function') {
				console.log(txt);
			}
		};
	log('AjaxNav loading ...')
	AjaxNav.log = log;
	if (typeof URL === 'undefined') {
		var URL = window.URL;
	}
	var origin;
	if (typeof location.origin === 'undefined') {
		origin = AjaxNav.origin = location.protocol + '//' +
	                              location.host;  // includes port, if any
	} else {
		origin = AjaxNav.origin = location.origin;
	}
	// hostname excludes the port:
	var myhostname = AjaxNav.myhostname = location.hostname;

	var id_match_logger = function (s, label) {
		if (typeof label !== 'undefined') {
			log(label + ' view id: "'+s+'"');
		}
	};
	/*
	 * Checks the given view id against the configured lists of
	 * complete ids, prefixes and suffixes
	 */
	var id_match = function (s, prefix, label) {
		var i, key, list, len, options=AjaxNav.options;

		// missing keys are amended in the AjaxNav.init method
		key = prefix+'_ids';
		list = options[key];
		for (i = 0, len = list.length; i < len; i++) {
			if (s == list[i]) {
				id_match_logger(s, label);
				return true;
			}
		}

		key = prefix+'_prefixes';
		list = options[key];
		for (i = 0, len = list.length; i < len; i++) {
			if (s.startsWith(list[i])) {
				id_match_logger(s, label);
				return true;
			}
		}

		key = prefix+'_suffixes';
		list = options[key];
		for (i = 0, len = list.length; i < len; i++) {
			if (s.endsWith(list[i])) {
				id_match_logger(s, label);
				return true;
			}
		}

		return false;
	};
	AjaxNav.id_match = id_match;

	/*
	 * split a path and return a list [prefix, div, view]:
	 * div -- '@@' or '/'
	 * prefix -- everything before <div>
	 * view -- a suspected view name (after <div>)
	 *
	 * A query string (starting with a question mark) is cropped from
	 * the view name and returned in the 4th part ([3]) of the list.
	 */
	var splitview = function (s) {
		var res = [],
		    posa = s.indexOf('@@'),
		    poslasl = s.lastIndexOf('/'),
		    qs = '',
		    posqm = s.indexOf('?');
		if (posqm === -1) {
			posqm = s.length;
		} else {
			qs = s.substring(posqm);
		}
		if (poslasl > -1) {  // position of last slash
			if (posa > poslasl) {
				return [s.substring(0, posa),
				        '@@',
				        s.substring(posa+2, posqm),
				        qs]
			} else {
				return [s.substring(0, poslasl),
				        '/',
				        s.substring(poslasl+1, posqm),
				        qs]
			}
		}
		if (posa > -1) {
			return [s.substring(0, posa),
			        '@@',
			        s.substring(posa+2, posqm),
			        qs]
		} else {
			return ['',
			        '',
			        s.substring(0, posqm),
			        qs]
		}
	};
	AjaxNav.splitview = splitview;

	var full_url = function (given) {
		var parsed = urlSplit(given),
		    offset = 0,
		    drop = 0,
		    path,
		    pathlist,
		    shortened,
		    suffix,
		    parsedloc;  // parsed current location

		if (parsed.protocol) {
			AjaxNav.log('full_url('+given+'): complete URL');
			return given;
		}

		if (given.startsWith('/')) {
			AjaxNav.log('full_url('+given+'): complete path');
			return AjaxNav.origin + given;
		}

		if (parsed.query) {
			suffix = '?'+parsed.query;
		} else {
			suffix = '';
		}
		if (parsed.fragment) {
			suffix += '#' + parsed.fragment;
		}
		shortened = given;
		AjaxNav.log('full_url('+given+'): assembling ...');
		parsedloc = urlSplit(location.href);
		pathlist = parsedloc.pathList;
		while (true) {
			if (shortened.startsWith('../')) {
				drop += 1;
				shortened = shortened.substring(3);
				continue;
			}
			if (shortened.startsWith('./')) {
				shortened = shortened.substring(2);
				continue;
			}
			break;
		}
		if (drop >> pathlist.length) {
			log('Zu viele Drops: '+ drop);
			return AjaxNav.origin
					+ '/'
					+ shortened
					+ suffix;
		} else {
			path = pathlist.slice(0, pathlist.length - drop).join('');
			if (path && ! path.startsWith('/'))
				path = '/' + path;
			if (shortened && ! shortened.startsWith('/'))
				shortened = '/' + shortened;
			return AjaxNav.origin
					+ path
					+ shortened
					+ suffix;
		}
	};
	AjaxNav.full_url = full_url;

	var _join_path = function (head, tail) {
		if (! head.endsWith('/')) {
			head += '/';
		}
		if (typeof tail === 'undefined') {
			tail = '';
		} else if (tail.startsWith('/')) {
			tail = tail.substring(1);
		}
		return head + tail;
	}

	/* The URLs to try: for .../full/path:
	 * - .../full/path/perhaps_a_view/@@ajax-nav
	 * - .../full/path/@@ajax-nav
	 *
	 * for .../any/path/@@any-view:
	 * - .../any/path/@@ajax-view
	 *
	 * TODO: check for the origin in the given URL,
	 *       and perhaps amend it
	 */
	var urls2try = function (fullpath) {
		var res = [],
		    suffix = '@@ajax-nav',
		    parsed = splitview(fullpath),
		    prefix = parsed[0],
		    divider = parsed[1],
		    viewname = parsed[2],
		    qs = parsed[3];
		if (id_match(viewname, 'blacklist_view', 'blacklisted')) {
			return null;
		} else {
			if (viewname) {
				if (divider == '@@') {
					log('followed @@, must be a view: "'+viewname+'"');
					return [_join_path(full_url(prefix), suffix+qs)];
				} else if (id_match(viewname, 'view', 'whitelisted')) {
					return [_join_path(full_url(prefix), suffix+qs)];
				} else {
					return [_join_path(full_url(fullpath), suffix+qs),
					        _join_path(full_url(prefix), suffix+qs)];
				}
			} else {
				return [_join_path(full_url(fullpath), suffix+qs)];
			}
		}
	};
	AjaxNav.urls2try = urls2try;

	var hostname_mismatch = function (s) {
		var parsed = urlSplit(s),
		    host_found = parsed.domain;
		if (! host_found)
			return false;
		return host_found !== AjaxNav.myhostname;
	};
	AjaxNav.hostname_mismatch = hostname_mismatch;

	// urlSplit will (reliably) parse complete URLs only
	var parsed_qs = function (s) {
		if (s.indexOf('?') === -1) {
			return {};
		}
		var parsed = urlSplit(s);
		if (parsed.protocol) {
			return parsed.queryObject;
		}
		return urlSplit(origin + '/' + s).queryObject;
	};

	/*
	 * It is possible to specify more than one CSS selector,
	 * separated by comma.
	 * This simple function considers those selectors in the given order
	 * to allow for their usage as a priority list.
	 */
	var fill_first = function (selectors, content) {
		var selector,
		    i, len,
		    done=false;
		selectors = selectors.split(',');
		for (i = 0, len=selectors.length; i < len; i++) {
			selector = selectors[i].trim();
			if (selector) {
				$(selector).each(function (idx) {
					$(this).html(content);
					done=true;
					return false;
				});
				if (done)
					return done;
			}
		}
		return done;
	};
	AjaxNav.fill_first = fill_first;

	/*
	 * The window history and title are special in not refering to
	 * DOM elements in the page text; thus, they are treated differently
	 */
	var history_and_title = function (url, title, data) {
		var has_title=title,
		    stateObj=null,
		    uid;
		if (typeof data.uid !== 'undefined') {
			stateObj = {uid: data.uid};
		} else if (url) {
			stateObj = {url: url};
		}
		if (title) {
			if (! url) {
				log('history_and_title: no URL for title ' +
				    title);
			} else {
				window.history.pushState(stateObj, title, url);
			}
			title = '(AJAX) ' + title;  // DEBUG / Development
			document.title = title;
		} else if (url) {
			window.history.pushState(stateObj, '', url);
		} else {
			log('history_and_title: no URL, no title');
		}
	};
	AjaxNav.history_and_title = history_and_title;

	/*
	 * The "working horse" of the clickfunc function
	 *
	 * This function will be called up to two times per click
	 * (ideally only once, of course); it will try the url with the given
	 * index and, in case of success, use the resulting JSON data to fill
	 * the appropriate URL elements and adjust the title and history
	 * (using the history_and_title function).
	 *
	 * If none of these requests succeeded, true will be returned
	 * to allow for the standard processing.
	 */
	var use_url = function (url, query) {
		var reply_ok = null,
		    newtitle = null,
		    newurl = null,
		    data_keys = [];
		$.ajax(url, {
			async: false,
			cache: false,  // development
			dataType: 'json',
			data: query, 
			error: function (jqXHR, textStatus, errorThrown) {
				log('AjaxNav failed ('+textStatus+') for URL '+url);
				reply_ok = false;
			},
			success: function (data, textStatus, jqXHR) {
				var key,
				    selector = null,
				    selectors=AjaxNav.options.selectors,
				    // null or a CSS selector:
				    scrollto = AjaxNav.options.scrollto_default_selector,
				    deltay = AjaxNav.options.scrollto_default_deltay,
				    auto_key = AjaxNav.options.scrollto_auto_key,
				    ii,
				    invalid_count = 0,
				    invalid_max = 3;
				log(textStatus+'; data ('+(typeof data)+'):');
				log(data)
				for (key in data) {
					if (key.startsWith('@')) {
						if (key == '@url') {
							newurl = data[key];
						} else if (key == '@title') {
							newtitle = data[key];
						} else if (key == '@ok') {
							reply_ok = data[key];
						} else if (key == '@noajax') {
							log('use_url('+url+'): ' + key + ' found');
							reply_ok = false;
						} else if (key == '@scrollto') {
							scrollto = data[key];
						} else {
							alert('Invalid special data key: "' +
							      key + '"; value: "' +
							      data[key] +'"');
						}
					} else {  // normal key --> HTML data
						selector = selectors[key];
						if (typeof selector === 'undefined') {
							invalid_count += 1;
							// log call deleted
							if (invalid_count <= invalid_max) {
								alert('Selector for key "'+key+'" unknown!');
							} else if (invalid_count > 100) {
								break;
							}
						} else if (AjaxNav.fill_first(selector, data[key])) {
							// yes, we found some place for our data:
							data_keys.push(key);
						}
					}
				}
				if (reply_ok === null) {
					if (data_keys) {
						reply_ok = true;
					} else {
						reply_ok = false;
					}
				}
				if (reply_ok) {
					AjaxNav.history_and_title(newurl, newtitle, data);
					if (scrollto === '@auto') {
						if (auto_key) {
							scrollto = selectors[auto_key];
							if (! scrollto) {
								AjaxNav.log('@scrollto[@auto]: no selector ' +
								            'for "'+auto_key+'"!');
							}
						} else {
							scrollto = null;
						}
					}
					if (scrollto) {
						$(scrollto).scrollTop(deltay);
					} else {
						window.scrollTo(0, deltay);
					}
				}

				if (DEBUG_DOTTED) {
					$('h1').css('border', '3px dotted lime');
				} else {
					$('h1').css('border', '3px dashed red');
				}
				DEBUG_DOTTED = ! DEBUG_DOTTED;
			}});
		return reply_ok;
	}  // ... use_url(url, query)

	/* The click handling function
	 *
	 * This function is called whenever an <a> element is clicked
	 * (unless blacklisted; see the init function).
	 *
	 * First, it will check whether the target is obviously inappropriate for
	 * AJAX loading; if the <a> elements lacks an href attribute, or if it it
	 * points outside the current domain, it will un-attach itself and return
	 * true to allow for the intended processing.
	 *
	 * Then it will try up to two @ajax-nav urls (see --> urls2try, splitview)
	 * in order to get the payload of the requested target page in JSON format.
	 */
	var clickfunc = function (event) {
		log('AjaxNav.clickfunc(event); event:');
		log(event);
		log('this:');
		log(this);
		// collect information about the target:
		var clickedon = $(this),
		    href = clickedon.attr('href'),
		    cls  = clickedon.attr('class'),
		    data = clickedon.data();

		log('clickedon:');
		log(clickedon);
		if (data) {
			log('clickedon.data():');
			log(data);
		} else
			log('AjaxNav: no data attributes');
		if (cls) {
			log('clickedon.attr("class"):');
			log(clickedon.attr("class"));
		} else
			log('AjaxNav: no class attribute');

		if (! href) {
			log('AjaxNav: no href attribute ("' + href + '")');
			$(this).off('click', AjaxNav.click);
			return true;  // continue with non-AJAX processing
		} else if (href.startsWith('#')) {
			log('AjaxNav: *local* href destination ("' + href + '")');
			$(this).off('click', AjaxNav.click);
			return true;  // continue with non-AJAX processing
		}
		if (hostname_mismatch(href)) {
			log('AjaxNav: Hostname mismatch ("'+href+'")');
			$(this).off('click', AjaxNav.click);
			return true;  // continue with non-AJAX processing
		}

		// includes mismatch detection (non-AJAX urls:):
		var urls_list = urls2try(href);
		if (! urls_list) {
			return true;
		}

		// -------------------------- [ compile query object ... [
		var i, a, len,
		    query = parsed_qs(href);
		// !!! query['_given_url'] = href;

		for (a in data) {
			query['data-'+a] = data[a];
		}
		if (cls) {
			query['_class'] = cls;
		}
		// !!! query._href = full_url(href);
		// -------------------------- ] ... compile query object ]

		// --------------------------- [ try one or two urls ... [
		for (i=0, len = urls_list.length; i < len; i++) {
			if (use_url(urls_list[i], query)) {
				event.preventDefault();
				return false;
			} else {
				log("Can't use URL " + urls_list[i]);
			}
		}
		// --------------------------- ] ... try one or two urls ]
		return true;
	};  // clickfunc(event)
	AjaxNav.click = clickfunc;
	log('AjaxNav loaded.')
	return AjaxNav;
})();

// To be called explicitly, optionally providing a key:
AjaxNav.init = function (key) {
	if (typeof key === 'undefined') {
		key = 'default';
	}

	var ajaxnav_init = function (data, textStatus, jqXHR) {
		AjaxNav.log('AjaxNav.init('+key+') received data:');
		AjaxNav.log(data);

		// ------------------------ [ initial (un)delegation ... [
		var whitelist = data.whitelist,
		    blacklist = data.blacklist,
		    i, len, ii, blacklist_length=null, nested,
		    selector;

		if (whitelist === undefined) {
			whitelist = ['body'];
		}

		if (blacklist === undefined) {
			nested = false;
			blacklist = [];
		} else {
			nested = data.nested_blacklist;
			blacklist_length = blacklist.length;
			if (nested === undefined) {
				nested = data.nested_blacklist = false;
			}
		}

		for (var i=0, len=whitelist.length; i < len; i++) {
			selector = whitelist[i];
			$(selector).on('click', 'a', AjaxNav.click);
			if (nested) {
				for (var ii=0; ii < blacklist_length; ii++) {
					$(selector).off('click', blacklist[ii], AjaxNav.click);
				}
			}
		}
		if (blacklist_length && ! nested) {
			for (var i=0; i < blacklist_length; i++) {
				selector = blacklist[i]
				$(selector).off('click', 'a', AjaxNav.click);
			}
		}
		// ------------------------ ] ... initial (un)delegation ]

		// ------------------------- [ view name recognition ... [
		// (for path components after a final "/" but w/o "@@")
		if (typeof data.view_ids === 'undefined') {
			data.view_ids = ['view',
			                 'edit',
			                 'base_edit'];
		}
		if (typeof data.view_prefixes === 'undefined') {
			data.view_prefixes = ['manage_'];
		}
		if (typeof data.view_suffixes === 'undefined') {
			data.view_suffixes = ['_view'];
		}
		// ------------------------- ] ... view name recognition ]

		// ------------------------------------- [ blacklist ... [
		// (view ids which will always be loaded the non-AJAX way)
		if (typeof data.blacklist_view_ids === 'undefined') {
			data.blacklist_view_ids = ['edit',
			                           'base_edit',
			                           'manage'];
		}
		if (typeof data.blacklist_view_prefixes === 'undefined') {
			data.blacklist_view_prefixes = ['manage_'];
		}
		if (typeof data.blacklist_view_suffixes === 'undefined') {
			data.blacklist_view_suffixes = ['_edit'];
		}
		// ------------------------------------- ] ... blacklist ]

		// ---------------------------- [ keys --> selectors ... [
		if (typeof data.selectors === 'undefined') {
			data.selectors = {
				content: '#content'
			};
		}
		// ---------------------------- ] ... keys --> selectors ]

		// --------------------------- [ @@scrollto defaults ... [
		if (typeof data.scrollto_default_selector === 'undefined') {
			data.scrollto_default_selector = null;
		}
		if (typeof data.scrollto_default_deltay === 'undefined') {
			data.scrollto_default_deltay = 0;
		}
		if (typeof data.scrollto_auto_key === 'undefined') {
			data.scrollto_auto_key = 'content';
		}
		if (! data.scrollto_auto_key) {
			data.scrollto_auto_key = null;
		}
		// --------------------------- ] ... @@scrollto defaults ]
		AjaxNav.options = data;
		AjaxNav.log('AjaxNav.init('+key+') completed.');
	}  // ... ajaxnav_init

	$.ajax({
		dataType: 'json',
		url: location.href+'/@@ajax-siteinfo',
		success: function (data, textStatus, jqXHR) {
			AjaxNav.origin = data.site_url;
			$.ajax({
				// dataType: 'json',
				cache: false,  // development
				url: AjaxNav.origin+'/@@ajaxnav-options-'+key
			})
			.done(ajaxnav_init)
			.fail(function (jqXHR, textStatus, errorThrown) {
				AjaxNav.log('E:AjaxNav.init('+key+') --> Error '+textStatus+':');
				AjaxNav.log(jqXHR);
				if (errorThrown !== undefined) {
					AjaxNav.log(errorThrown);
				}
				alert('AjaxNav.init: Error '+textStatus+' for key "'+key+'"');
			});
		}
	});
};
// -*- coding: utf-8 -*- vim: ts=4 sw=4 sts=4 noet ai noic tw=79 cc=+1
