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
var AjaxNav = (function () {
    var AjaxNav = {},
        log = function (txt) {
            if (console && console.log) {
                console.log(txt);
            }
        };
    AjaxNav.log = log;
	if (typeof URL === 'undefined') {
		var URL = Window.URL;
	}
	var rooturl = AjaxNav.rooturl = window.location.protocol + '//' +
	                                window.location.host;
	var myhost = AjaxNav.myhost = window.location.hostname;
	alert('root-URL ist '+AjaxNav.rooturl);

	var id_match_logger = function (s, label) {
		if (typeof label !== 'undefined') {
			log(label + ' view id: "'+s+'"');
		}
	}
	var id_match = function (s, ids, suffixes, label) {
		var i;
		if (typeof ids === 'undefined') {
			ids = [];
		}
		for (i = 0; i < ids.length; i++) {
			if (s == ids[0]) {
				id_match_logger(s, label);
				return true;
			}
		}
		if (typeof suffixes === 'undefined') {
			suffixes = [];
		}
		for (i = 0; i < suffixes.length; i++) {
			if (s.endsWith(suffixes[0])) {
				id_match_logger(s, label);
				return true;
			}
		}
		return false;
	}
	AjaxNav.id_match = id_match;

	var splitpath = function (s) {
		/*
		 * split a path and return a list [prefix, div, view]:
		 * div -- '@@' or '/'
		 * prefix -- everything before <div>
		 * view -- a suspected view name (after <div>)
		 */
		var res = [],
		    posa = fullpath.indexOf('@@'),
		    poslasl = fullpath.lastIndexOf('/');
		if (poslasl > -1) {  // position of last slash
			if (posa > poslasl) {
				return [s.substring(0, posa),
				        '@@',
				        s.substring(posa+2)]
			} else {
				return [s.substring(0, poslasl),
				        '/',
				        s.substring(poslasl+1)]
			}
		}
		if (posa > -1) {
			return [s.substring(0, posa),
			        '@@',
			        s.substring(posa+2)]
		} else {
			return ['',
			        '',
			        s]
		}
	}
	AjaxNav.splitpath = splitpath;

	var urls2try = function (fullpath) {
		/* The URLs to try: for .../full/path:
		 * - .../full/path/perhaps_a_view@ajax-nav
		 * - .../full/path@ajax-nav
		 *
		 * for .../any/path@@any-view:
		 * - .../any/path@@ajax-view
		 */
		var res = [],
		    suffix = '@@ajax-nav',
		    parsed = splitpath(fullpath),
		    prefix = parsed[0],
		    divider = parsed[1],
		    viewname = parsed[2];
		if (id_match(viewname, AjaxNav.blacklist_view_ids, AjaxNav.blacklist_view_suffixes, 'blacklisted')) {
			return null;
		} else {
			if (viewname) {
				if (divider == '@@') {
					log('followed @@, must be a view: "'+viewname+'"');
					return [prefix + suffix];
				} else if (id_match(viewname, AjaxNav.whitelist_ids, AjaxNav.whitelist_suffixes, 'whitelisted')) {
					return [prefix + suffix];
				} else {
					return [fullpath + suffix,
					        prefix + suffix];
				}
			} else {
				return [fullpath + suffix];
			}
		}
	}
	AjaxNav.urls2try = urls2try;

	var hostname_mismatch = function (s) {
		var pos = s.indexOf('://'),
		    pos2,
		    host_found;
		if (pos === -1) {
			return false;
		}
		pos2 = s.indexOf('/', pos);
		if (pos2 === -1) {
			host_found = s.slice(pos+3);
		} else {
			host_found = s.slice(pos+3, pos2);
		}
		return host_found !== AjaxNav.myhost;
	}
	AjaxNav.hostname_mismatch = hostname_mismatch;

	// from https://www.joezimjs.com/javascript/3-ways-to-parse-a-query-string-in-a-url/
	var parseQueryString = function (queryString) {
		var params = {}, queries, temp, i, l;
		// Split into key/value pairs
		queries = queryString.split("&");
		// Convert the array of strings into an object
		for (i = 0, l = queries.length; i < l; i++) {
			temp = queries[i].split('=');
			params[temp[0]] = temp[1];
		}
		return params;
	};

	var clickfunc = function (e) {
		log('AjaxNav.click :-)');
		log(e);
		log('e:');
		alert(e);
		log('this:');
		log(this);
		var clickedon = $(this),
		    href = clickedon.attr('href'),
		    cls = clickedon.attr('class'),
		    data = clickedon.data();

		log('clickedon:');
		log(clickedon);
		log('clickedon.data():');
		log(clickedon.data());
		log('clickedon.attr("class"):');
		log(clickedon.attr("class"));

		if (! href) {
			log('AjaxNav: no href attribute ("' + href + '")');
			$(this).off('click', AjaxNav.click);
			return true;  // continue with non-AJAX processing
		}
		if (hostname_mismatch(href)) {
			log('AjaxNav: Hostname mismatch ("'+href+'")');
			$(this).off('click', AjaxNav.click);
			return true;  // continue with non-AJAX processing
		}

		var paths = urls2try(href);
		if (! paths) {
			return true;
		}
		var i, a,
		    base = window.location.href,
			query = parseQueryString(href);
		query['_given_url'] = href;

		spa = data.getOwnPropertyNames();
		for (i=0; i < spa.length; i++) {
			a = spa[i];
			query['data-'+a] = sp[a];
		}
		if (cls) {
			query['_class'] = cls;
		}
		query._href = URL(href, base).toString();

		var inner_ajaxhandler = function (e, i) {
			var url = URL(paths[i], base);
			$.ajax({
				datatype: 'json',
				url: url,
				// Merged querystring, data(), attr(class) ...
				data: query,
				success: function (data, textStatus, jqXHR) {
					var keys = data.getOwnPropertyNames(),
					    ii, aa;
					if (typeof data.title !== 'undefined') {
						document.title = data.title;
					}
					if (typeof data.url !== 'undefined') {
						alert('TODO: push '+data.url+ ' to history');
					}
					for (ii=0; ii < keys.length; ii++) {
						aa = keys[ii];
						if (aa === 'title' || aa === 'url') {
							continue;
						}
						alert('TODO: get selector for key "'+key
							  + '" and fill the resp. element');
					}
					return false;
				},
				error: function (jqXHR, textStatus, errorThrown) {
					i ++;
					if (i < paths.length) {
						inner_ajaxhandler(e, i);
					} else {
						log('AjaxNav failed for URL '+url);
						return true;
					}
				}
			});
		}
		inner_ajaxhandler(e, 0);
	}
	AjaxNav.click = clickfunc;
	return AjaxNav;
})();

AjaxNav.init = function (key) {
	if (key === undefined) {
		key = 'default';
	}
	$.ajax({
		dataType: 'json',
		url: rooturl+'/@@ajaxnav-options-'+key,
		success: function (data, textStatus, jqXHR) {
			AjaxNav.log('AjaxNav.init('+key+') received data:');
			AjaxNav.log(data);

			var thelist = data.whitelist,
			    selector;
			if (thelist === undefined) {
				thelist = ['body'];
			}
			for (var i=0; i < thelist.length; i++) {
				selector = thelist[i]
				$(selector).on('click', 'a', AjaxNav.click);
			}
			thelist = data.blacklist;
			if (thelist !== undefined) {
				for (var i=0; i < thelist.length; i++) {
					selector = thelist[i]
					$(selector).off('click', 'a', AjaxNav.click);
				}
			}
			// view ids which will always be loaded the non-AJAX way
			if (typeof data.blacklist_view_ids === 'undefined') {
				data.blacklist_view_ids = ['edit',
				                           'base_edit'];
			}
			if (typeof data.blacklist_view_suffixes === 'undefined') {
				data.blacklist_view_suffixes = ['_edit'];
			}
			if (typeof data.view_ids === 'undefined') {
				data.view_ids = ['view',
				                 'edit',
				                 'base_edit'];
			}
			if (typeof data.view_suffixes === 'undefined') {
				data.view_suffixes = ['_view'];
			}
			AjaxNav.options = data;
			AjaxNav.log('AjaxNav.init('+key+') completed.');
		},
		error: function (jqXHR, textStatus, errorThrown) {
			AjaxNav.log('E:AjaxNav.init('+key+') --> Error '+textStatus+':');
			AjaxNav.log(jqXHR);
			if (errorThrown !== undefined) {
				AjaxNav.log(errorThrown);
			}
			alert('AjaxNav.init: Error '+textStatus+' for key "'+key+'" :-(');
		}
	});
}
// -*- coding: utf-8 -*- vim: ts=4 sw=4 sts=4 noet ai noic tw=79 cc=+1
