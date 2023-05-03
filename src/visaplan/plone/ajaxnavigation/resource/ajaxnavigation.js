/* visaplan.plone.ajaxnavigation: AJAX navigation for Plone sites
 * Copyright (C) 2020  visaplan GmbH, Bochum, Germany
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
// startsWith polyfill; taken from
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/startsWith#Polyfill
if (!String.prototype.startsWith) {
    Object.defineProperty(String.prototype, 'startsWith', {
        value: function(search, rawPos) {
            var pos = rawPos > 0 ? rawPos|0 : 0;
            return this.substring(pos, pos + search.length) === search;
        }
    });
}
// https://stackoverflow.com/a/1418059/1051649:
if (typeof(String.prototype.trim) === "undefined") {
    String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

var AjaxNav = (function () {
    var AjaxNav = {},
        DEBUG_DOTTED = true,
        REGEX_UID = /^[0-9a-f]{32}$/,
        SPECIAL_QV_PREFIX = '@',
        DATA_PREFIX = SPECIAL_QV_PREFIX+'data-',
        CLASS_VARNAME = SPECIAL_QV_PREFIX+'class',
        URL_VARNAME = SPECIAL_QV_PREFIX+'original_url',
        VIEW_VARNAME = SPECIAL_QV_PREFIX+'viewname',
        log = function (txt) {
        if (typeof console !== 'undefined' &&
                typeof console.log === 'function') {
                console.log(txt);
            }
        };
    var looks_like_uid = AjaxNav.looks_like_uid = REGEX_UID.test;
    log('AjaxNav loading ...')
    AjaxNav.log = log;
    if (typeof URL === 'undefined') {
        var URL = window.URL;
    }
    if (typeof location.origin === 'undefined') {
        AjaxNav.origin = location.protocol + '//' +
                         location.host;  // includes port, if any
    } else {
        AjaxNav.origin = location.origin;
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
            if (s === list[i]) {
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
     * NOTE: When following other charactes, a '@@' is not sufficient for Zope
     *       to recognise a method name; '/@@' is required. For simplicity, we
     *       are a little bit sloppy here. But we use hyperlinks here which
     *       have been used as classic full-page links anyway, so we don't
     *       expect such invalid input anyway.
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

    var full_url = function (given, options) {
        var parsed = urlSplit(given),
            options = options || {},
            strip_suffixes = typeof options.strip_suffixes !== 'undefined'
                             ? options.strip_suffixes
                             : false,
            offset = 0,
            drop = 0,
            path,
            pathlist,
            shortened,
            suffix='',
            parsedloc;  // parsed current location

        // a full url is returned unchanged
        if (parsed.protocol) {
            AjaxNav.log('full_url('+given+'): complete URL');
            if (strip_suffixes) {
                return parsed.protocol + '://'
                       + parsed.domain
                       + parsed.path;
            }
            return given;
        }

        // site-absolute paths start with '/'
        if (given.startsWith('/')) {
            AjaxNav.log('full_url('+given+'): complete path');
            if (strip_suffixes) {
                return AjaxNav.origin + parsed.path;
            }
            return AjaxNav.origin + given;
        }

        // query string and fragment
        if (! strip_suffixes) {
            if (parsed.query) {
                suffix = '?'+parsed.query;
            }
            if (parsed.fragment) {
                suffix += '#' + parsed.fragment;
            }
        }
        shortened = given;
        AjaxNav.log('full_url('+given+'): assembling ...');

        // remove leading './' and '../'
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
    };

    var parse_qs = function (qs) {
        var i, len, liz1, liz2,
            key, val,
            query = {};
        if (qs.substr(0, 1) === '?') {
            qs = qs.substr(1);
        }
        liz1 = qs.split('&');
        for (i=0, len=liz1.length; i < len; i++) {
            // Note: only one '=' taken into account ...
            liz2 = liz1[i].split('=');
            key = liz2[0];
            val = liz2[1];
            if (typeof query[key] === 'undefined') {
                query[key] = val
            } else if (typeof query[key] === 'string') {
                query[key] = [query[key], val];
            } else {
                query[key].push(val);
            }
        }
        return query;
    }

    /**
     * url object - create a URL object, suitable for -> use_url
     *
     * Arguments:
     *
     * - url[_o] - a string (the URL to use, usually ".../@@ajax-nav";
     *             -> the 'url' attribute of the returned object)
     *             or an object with at least a 'url' attribute
     * - original - a string: the "original" (reloadable) URL presented as the
     *              page address
     *              -> the 'original' attribute
     * - qs - the query string, optionally prefixed by '?',
     *        or a readily parsed query object
     *        -> the 'query' attribute
     *
     * ... and, optionally:
     * - viewname - an assumed view name
     *              -> the 'viewname' attribute, if truish
     */
    var url_object = function (url_o, original, qs, viewname) {
        var query;
        if (typeof url_o !== 'object') {
            url_o = {url: url_o};
        }
        if (original) {
            url_o['original'] = original;
        }
        if (viewname) {
            url_o['viewname'] = viewname;
        }
        if (typeof qs === 'object') {
            query = qs
        } else if (qs) {
            query = parse_qs(qs);
        } else {
            query = null;
        }
        url_o.query = query;
        return url_o
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
            fu_opt = {strip_suffixes: true},
            parsed = splitview(fullpath),
            i, len,
            prefix = parsed[0],
            divider = parsed[1],
            viewname = parsed[2],
            qs = parsed[3];
        if (id_match(viewname, 'blacklist_view', 'blacklisted')) {
            return null;
        } else {
            if (viewname) {
                if (REGEX_UID.test(viewname)) {
                    // found a UID (invalid viewname): append /@@ajax-nav
                    res.push(url_object(prefix+divider+viewname+'/'+suffix,
                                        fullpath,
                                        qs));
                } else
                if (divider == '@@') {
                    log('followed @@, must be a view: "'+viewname+'"');
                    if (prefix) {
                        res =  [url_object(_join_path(full_url(prefix),
                                                      suffix),
                                           fullpath,
                                           qs,
                                           viewname)
                                ];
                    } else {
                        res.push(url_object(suffix,
                                            fullpath,
                                            qs,
                                            viewname));
                    }
                } else if (divider == '') {
                    // a single word; usually the id of a subpage
                    res =  [url_object(_join_path(full_url(viewname),
                                                  suffix),
                                       fullpath,
                                       qs)
                            ];
                } else if (id_match(viewname, 'view', 'whitelisted')) {
                    res =  [url_object(_join_path(full_url(prefix),
                                                  suffix),
                                       fullpath,
                                       qs,
                                       viewname)
                            ];
                } else {
                    // not whitelisted: try two urls:
                    res =  [url_object(prefix+divider+viewname+'/'+suffix,
                                       fullpath,
                                       qs),
                            url_object(prefix+'/'+suffix,
                                       fullpath,
                                       qs,
                                       viewname)
                            ];
                }
            } else {
                // no path, or ends with slash:
                res =  [url_object(_join_path(full_url(fullpath, fu_opt),
                                              suffix),
                                   fullpath,
                                   qs)
                        ];
            }
        }
        len = res.length;
        log('urls2try('+fullpath+'): returning '+len+' objects');
        for (i=0; i < len; i++) {
            log(res[i]);
        }
        return res;
    };
    AjaxNav.urls2try = urls2try;

    var hostname_mismatch = function (s) {
        if (s.indexOf('://') === -1)
            return false;
        var parsed = urlSplit(s),
            host_found = null;
        if (typeof parsed.domain !== 'undefined') {
            host_found = parsed.domain;
        }
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
        return urlSplit(AjaxNav.origin + '/' + s).queryObject;
    };

    /*
     * Originally, this function did the splitting of the one string which
     * could contain several CSS selectors;
     * now this is done by the AjaxNav.get_fill_selectors function.
     *
     * So, is this function still necessary?
     */
    var fill_first = function (selectors, content) {
        var selector,
            i, len,
            done=false;
        for (i = 0, len=selectors.length; i < len; i++) {
            selector = selectors[i].trim();
            if (selector) {
                $(selector).each(function () {
                    $(this).html(content);
                    done = true;
                    return false; // terminate loop
                });
                if (done)
                    return done;
            }
        }
        return done;
    };
    AjaxNav.fill_first = fill_first;

    /*
     * A helper for the method history_and_title (below):
     * Set the base url of the page, creating the html > head > base element
     * if necessary.
     *
     * HOTFIX: sometimes we get a list, which will cause an exception to be
     *         thrown, and in the end the whole page to loaded!
     */
    var set_base_url = function (url) {
        var head=null,
            the_url = typeof url === 'string'      // -- [ HOTFIX ... [
                      ? url
                      : (typeof url[0] !== 'undefined'
                         ? url[0]
                         : null),
            i, len,                                // -- ] ... HOTFIX ]
            base=$('html base').first();
        if (base) {
            base.attr('href', url);
            log('set base[href] to '+url);
        } else {
            $(document).add('<base>').attr('href', url);
            log('created <base> and set href to '+url);
        }
        if (typeof url !== 'string') {              // -- [ HOTFIX ... [
            log('set_base_url: non-string given as url!');
            log(url);
            if (! the_url) {
                return;
            }
            if (typeof url.length !== 'undefined') {
                len = url.length;
                if (len > 1) {
                    for (i=1, len=url.length; i < len; i++) {
                        if (url[i] && url[i] !== the_url) {
                            if (! the_url) {
                                the_url = url[i];
                                log('using url['+i+'] -> '+the_url);
                            } else {
                                log('url['+i+'] ('+url[i]+') != '+the_url+'!');
                            }
                        }
                    }
                }
            }
        }                                           // -- ] ... HOTFIX ]
        // Maintain main menu items
        var parsed = urlSplit(the_url),
            full_url = url+'/',
            path_only = ''
            options = AjaxNav.options,
            menu_item_selector = options.menu_item_selector,
            switched_class = options.menu_item_switched_classname;

        if (typeof menu_item_selector !== 'undefined'
            &&     menu_item_selector) {
        $(options.menu_item_selector).each(function (i, o) {
            var my_href = $(this).attr('href');
            if (my_href) {
                if (my_href.slice(-1) !== '/') {
                    my_href += '/';
                }
                if (full_url.startsWith(my_href) ||
                    path_only.startsWith(my_href))
                {
                    $(this).addClass(switched_class);
                } else {
                    $(this).removeClass(switched_class);
                }
            }
        });
        }
    };
    AjaxNav.set_base_url = set_base_url;

    /*
     * The window history and title are special in not refering to
     * DOM elements in the page text; thus, they are treated differently
     *
     * This function currently also pushes the state to the window.history.
     */
    var history_and_title = function (url, title, data) {
        var stateObj = data;
        if (title) {
            if (AjaxNav.options.development_mode) {
                title = '(AJAX) ' + title;  // DEBUG / Development
            }
            document.title = title;
        }
        if (url) {
            set_base_url(url);
            window.history.pushState(stateObj, '', url);
        } else {
            window.history.pushState(stateObj, '');
        }
    };
    AjaxNav.history_and_title = history_and_title;

    /* get fill selectors
     *
     * For some pages, special fill targets should be prefered, if available;
     * e.g., if a news is loaded from a list, it might be desired to load it
     * below the batch navigation which might not be present in other contexts
     * (e.g., when loading the news from a carousel).
     */
    var get_fill_selectors = function (data, key) {
        var common_selectors = AjaxNav.options.selectors[key],
            local_selectors = [],
            prefered_selectors,
            val,
            selector, i, len;
        if (typeof data['@prefered-selectors'] !== 'undefined') {
            prefered_selectors = data['@prefered-selectors'][key];
            if (typeof prefered_selectors !== 'undefined') {
                for (i=0, len=prefered_selectors.length; i < len; i++) {
                    local_selectors.push(prefered_selectors[i]);
                }
            }
        }
        // AjaxNav.options.selectors[key] is currently server-side configured
        // as a string (which may contain commas),
        // but converted to a list during loading of options.
        if (typeof common_selectors === 'string') {
            log('get_fill_selectors(..., '+key+ '): '+
                'found a string! ('+common_selectors+')');
            common_selectors = common_selectors.split(',');
        }  // (CHECKME: the above might now be obsolete)
        if (typeof common_selectors !== 'undefined') {
            for (i=0, len=common_selectors.length; i < len; i++) {
                val = common_selectors[i];
                if (val) {
                    local_selectors.push(val);
                }
            }
        }
        return local_selectors;
    };
    AjaxNav.get_fill_selectors = get_fill_selectors;

    /* has blacklisted class
     */
    var has_blacklisted_class = function (elem) {
        var cls_raw = $(elem).attr('class'),
            classes, len, i;
        if (! cls_raw) {
            return false;
        }
        classes = cls_raw.trim().split(/\s+/);
        len = classes.length;
        if (len === 0) {
            return false;
        }
        var options = AjaxNav.options,
            class_ids = options.blacklist_class_ids,
            class_prefixes = options.blacklist_class_prefixes,
            len_prefixes = class_prefixes.length,
            class_suffixes = options.blacklist_class_suffixes,
            len_suffixes = class_suffixes.length,
            cls, testval, j, len2;
        for (i=0; i < len; i++) {
            cls = classes[i];
            if (class_ids.indexOf(cls) !== -1) {
                return true;
            }
            for (j=0; j < len_prefixes; j++) {
                if (cls.startsWith(class_prefixes[j])) {
                    return true;
                }
            }
            for (j=0; j < len_suffixes; j++) {
                if (cls.endsWith(class_suffixes[j])) {
                    return true;
                }
            }
        }
        return false;
    };
    AjaxNav.has_blacklisted_class = has_blacklisted_class;

    var amend_target_rel_values = function (elem) {
        var relvals = $(elem).attr('rel'),
            options = AjaxNav.options,
            new_relvals = options.target_rel_values,
            i, len, val,
            changed = false;
            len, i;
        if (typeof relvals === 'string') {
            relvals = relvals.trim().split(/\s+/);
        } else if (typeof relvals !== 'object') {
            relvals = [];
        }
        for (i=0, len = new_relvals.length; i < len; i++) {
            val = new_relvals[i];
            if (relvals.indexOf(val) === -1) {
                relvals.push(val);
                changed = true;
            }
        }
        if (changed) {
            $(elem).attr('rel', relvals.join(' '));
        }
    }
    AjaxNav.amend_target_rel_values = amend_target_rel_values;

    var has_nondefault_target = function (elem) {
        var target = $(elem).attr('target');
        if (! target || target === '_self') {
            return false;
        }
        // our AJAX processing might fail, so we need to
        // do this in any case:
        amend_target_rel_values(elem);
        return AjaxNav.options.regard_target_attribute;
    }
    AjaxNav.has_nondefault_target = has_nondefault_target;

    /* get scrollto selector  (get_scrollto_selector -- NOT YET IMPLEMENTED)
     *
     * We expect one selector here, and we don't intend to use per-request
     * @prefered-selectors (for now).
     *
     * Note: the globally set AjaxNav.options.selectors values currently
     * contain strings which *might* contain commas.  This is perfectly o.k.
     * for AjaxNav.fill_first, but for the the .scrollTop method, the result
     * might be surprising.
     */

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
     *
     * Some of the code here is currently duplicated in AjaxNav.process_data,
     * due to subtle differences of the tasks
     * "load a fresh page from an url which might or might not work"
     * and "rebuild a page from the browser history".
     */
    var use_url = function (url_o, additional_query) {
        var reply_ok = null,
            url_o = url_o || {},
            url = (typeof url_o === 'string'
                   ? url_o
                   : (typeof url_o.url !== 'undefined'
                      ? url_o.url
                      : '@@ajax-nav'
                      )),
            query_from_url = typeof url_o.query === 'object'
                             ? url_o.query
                             : null,
            query = {},
            key,
            viewname = (typeof url_o !== 'object'
                        ? null
                        : (typeof url_o.viewname !== 'undefined'
                           ? url_o.viewname
                           : null
                           )),
            original = (typeof url_o !== 'object'
                        ? null
                        : (typeof url_o.original !== 'undefined'
                           ? url_o.original
                           : null
                           )),
            additional_query = additional_query || null,
            result_o = {'try_other': null,
                        'ok': null,  // <- reply_ok
                        'processed_contents': null,
                        'noajax': null},
            newtitle = null,
            newurl = null,
            noajax = null,
            data_keys = [];
        if (query_from_url) {
            for (key in query_from_url) {
                query[key] = query_from_url[key];
            }
        }
        if (additional_query) {
            for (key in additional_query) {
                if (typeof query[key] !== 'undefined') {
                    continue;
                }
                query[key] = additional_query[key];
            }
        }
        if (viewname) {
            query[VIEW_VARNAME] = viewname;
        }
        if (original) {
            query[URL_VARNAME] = original;
        }
        $.ajax(url, {
            async: false,
            cache: false,  // development
            dataType: 'json',
            data: query
        })
        .done(function (data, textStatus, jqXHR) {  // use_url>ajax.done
            var key,
                selectors = null,
                http_status = jqXHR.status,
                // null or a CSS selector:
                scrollto = AjaxNav.options.scrollto_default_selector,
                auto_key = AjaxNav.options.scrollto_auto_key,
                ii,
                invalid_count = 0,
                invalid_max = 3;
            // we've got JSON data, so we had the correct URL already:
            result_o.try_other = false;
            log(textStatus+'; data ('+(typeof data)+'):');
            log(data)
            for (key in data) {   // iterate response data ...
                if (key.startsWith('@')) {
                    if (key == '@url') {
                        newurl = data[key];    // from use_url
                    } else if (key == '@title') {
                        newtitle = data[key];  // from use_url
                    } else if (key == '@ok') {
                        reply_ok = data[key];
                    } else if (key == '@noajax') {
                        log('use_url('+url+'): ' + key + ' found');
                        if (data[key]) {
                            noajax = true;  // from use_url
                        } else {
                            log('Hu? data[' + key +
                                '] is not truish! ('+data[key]+')');
                        }
                    } else if (key == '@scrollto') {
                        scrollto = data[key];
                    } else if (key == '@prefered-selectors') {
                        // directly used via AjaxNav.get_fill_selectors()
                        log(data[key]);
                    } else if (key == '@devel-info') {
                        log(data[key]);  // PRESERVE
                    } else {
                        alert('Invalid special data key: "' +
                              key + '"; value: "' +
                              data[key] +'"');
                    }
                } else {  // normal key --> HTML data
                    selectors = AjaxNav.get_fill_selectors(data, key);
                    if (selectors.length === 0) {
                        invalid_count += 1;
                        // log call deleted
                        if (invalid_count <= invalid_max) {
                            alert('Selector for key "'+key+'" unknown!');
                        } else if (invalid_count > 100) {
                            break;
                        }
                    } else if (AjaxNav.fill_first(selectors, data[key])) {
                        // yes, we found some place for our data:
                        data_keys.push(key);
                    }
                }
            }  // ... use_url>ajax.done: iterate response data
            if (reply_ok === null) {
                reply_ok = data_keys.length > 0;
            }
            if (noajax === null) {
                noajax = data_keys.length === 0;
            }
            result_o.processed_contents = data_keys.length > 0;
            result_o.ok = reply_ok;
            result_o.noajax = noajax;
            if (noajax) {
                // we might have inserted some placeholder "content",
                // but we surely want to load the requested page
                // conventionally:
                return;
            }
            if (reply_ok) {
                AjaxNav.history_and_title(newurl, newtitle, data);
                AjaxNav.scroll_to(scrollto);
            }

            if (AjaxNav.options.development_mode) {
            if (DEBUG_DOTTED) {
                $('h1').css('border', '3px dashed lime');
            } else {
                $('h1').css('border', '3px dashed red');
            }
            DEBUG_DOTTED = ! DEBUG_DOTTED;
            }
        })  // ... use_url>ajax.done
        .fail(function (jqXHR, textStatus, errorThrown) {
            var http_status = jqXHR.status;
            log('AjaxNav failed ('+textStatus+
                '; HTTP status code: '+http_status+
                ') for URL '+url);
            if (http_status === 401) {
                unauthorized = true;
                log(url+': unauthorized');
                result_o.try_other = false;
            } else if (http_status === 404) {
                // if this is the first URL tried, at least:
                result_o.try_other = true;
            } else if (http_status == 401) {
                unauthorized = true;
                log(url+': unauthorized (NON-NUMERIC)');
                result_o.try_other = false;
            } else {
                log(url+': OTHER ERROR');
            }
            result_o.ok = false;
        });  // ... use_url>ajax.fail
        return result_o;
    };  // ... use_url(url, query)

    /* The click handling function
     *
     * This function is called whenever an <a> element is clicked
     * (unless blacklisted; see the init function).
     *
     * First, it will check whether the target is obviously inappropriate for
     * AJAX loading; if the <a> elements lacks an href attribute, or if it
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
            href =      clickedon.attr('href'),
            cls  =      clickedon.attr('class'),
            elem_data = clickedon.data(),
            result_o =  null,
            unauthorized = false;

        log('clickedon:');
        log(clickedon);

        if (typeof elem_data.fullpageOnly !== 'undefined'
            &&     elem_data.fullpageOnly) {
            return true;  // server-side mark "always load full page"
        }

        if (! href) {
            log('AjaxNav: no href attribute ("' + href + '")');
            $(this).off('click', AjaxNav.click);
            return true;  // continue with non-AJAX processing
        } else if (href.startsWith('#')) {
            log('AjaxNav: *local* href destination ("' + href + '")');
            $(this).off('click', AjaxNav.click);
            return true;  // continue with non-AJAX processing
        }
        if (has_blacklisted_class(clickedon)) {
            log('AjaxNav: has blacklisted class');
            // $(this).off('click', AjaxNav.click);
            return true;  // continue with standard processing
        }

        if (has_nondefault_target(clickedon)) {
            // By default, we regard the target attribute
            return true;
        }

        if (hostname_mismatch(href)) {
            log('AjaxNav: Hostname mismatch ("'+href+'"); urlSplit:');
            log(urlSplit(href));
            $(this).off('click', AjaxNav.click);
            return true;  // continue with non-AJAX processing
        }

        // includes mismatch detection (non-AJAX urls:):
        var urls_list = urls2try(href);
        if (urls_list.length === 0) {
            return true;
        }

        // -------------------------- [ compile query object ... [
        var i, a, len,
            query = parsed_qs(href);
        // !!! query['_given_url'] = href;

        for (a in elem_data) {
            query[DATA_PREFIX+a] = elem_data[a];
        }
        if (cls) {
            query[CLASS_VARNAME] = cls;
        }
        // !!! query._href = full_url(href);
        // -------------------------- ] ... compile query object ]

        // --------------------------- [ try one or two urls ... [
        for (i=0, len=urls_list.length; i < len; i++) {
            result_o = use_url(urls_list[i], query);
            if (result_o.try_other) {
                continue;
            } else if (result_o.noajax) {
                return true;
            } else if (result_o.ok) {
                event.preventDefault();
                return
            } else if (result_o.unauthorized) {
                if (result_o.processed_contents) {
                    event.preventDefault();
                    return;
                } else {
                    return true;
                }
            } else {
                log("Can't use URL " + urls_list[i]+ '; result_o:');
                log(result_o);
            }
        }
        // --------------------------- ] ... try one or two urls ]
        return true;
    };  // clickfunc(event)
    AjaxNav.click = clickfunc;

    /* load url: e.g. triggered by form actions
     */
    var load_url = function (href, query) {
        var i, len,
            query = query || {},
            result_o =  null,
            unauthorized = false;

        if (typeof query.fullpageOnly !== 'undefined'
            &&     query.fullpageOnly) {
            return true;  // server-side mark "always load full page"
        }

        if (! href) {
            log('AjaxNav: no href attribute ("' + href + '")');
            return true;  // continue with non-AJAX processing
        }
        if (hostname_mismatch(href)) {
            log('AjaxNav: Hostname mismatch ("'+href+'"); urlSplit:');
            log(urlSplit(href));
            return true;  // continue with non-AJAX processing
        }

        // includes mismatch detection (non-AJAX urls:):
        var urls_list = urls2try(href);
        if (urls_list.length === 0) {
            return true;
        }

        // --------------------------- [ try one or two urls ... [
        for (i=0, len=urls_list.length; i < len; i++) {
            result_o = use_url(urls_list[i], query);
            if (result_o.try_other) {
                continue;
            } else if (result_o.noajax) {
                return true;
            } else if (result_o.ok) {
                return
            } else if (result_o.unauthorized) {
                if (result_o.processed_contents) {
                    return;
                } else {
                    return true;
                }
            } else {
                log("Can't use URL " + urls_list[i]+ '; result_o:');
                log(result_o);
            }
        }
        // --------------------------- ] ... try one or two urls ]
        return true;
    };
    AjaxNav.load_url = load_url;

    /* process_data: use the browser history
     *
     * Performs a simplified subset of the processing done by the use_url
     * function, sufficient to rebuild a pre-built page from the
     * browser history
     */
    var process_data = function (data) {
        if (typeof data !== 'object') {
            return;
        }
        var key,
            scrollto = AjaxNav.options.scrollto_default_selector,
            data_keys = [],
            selectors = null,
            newurl = null,
            noajax = null,
            invalid_count = 0,
            invalid_max = 3,
            auto_key = AjaxNav.options.scrollto_auto_key;

        log(data)
        for (key in data) {   // iterate response data ...
            if (key.startsWith('@')) {
                if (key == '@url') {
                    newurl = data[key];
                } else if (key == '@title') {
                    log('key '+key+' processed by browser, right? ('+
                        data[key]+')');
                    // newtitle = data[key];
                } else if (key == '@ok') {
                    reply_ok = data[key];
                } else if (key == '@noajax') {
                    log('use_url('+url+'): ' + key + ' found');
                    log("THIS COMES UNEXPECTEDLY!");
                    if (data[key]) {
                        reply_ok = false;
                        noajax = true;  // from use_url
                    } else {
                        log('Hu? data[' + key + ']'+
                            ' is not truish! ('+data[key]+')');
                    }
                } else if (key == '@scrollto') {
                    scrollto = data[key];
                } else if (key == '@prefered-selectors') {
                    // directly used via AjaxNav.get_fill_selectors()
                    log(data[key]);
                } else if (key == '@devel-info') {
                    log(data[key]);  // PRESERVE
                } else {
                    alert('Invalid special data key: "' +
                          key + '"; value: "' +
                          data[key] +'"');
                }
            } else {  // normal key --> HTML data
                selectors = AjaxNav.get_fill_selectors(data, key);
                if (selectors.length === 0) {
                    invalid_count += 1;
                    // log call deleted
                    if (invalid_count <= invalid_max) {
                        if (AjaxNav.options.development_mode) {
                        alert('Selector for key "'+key+'" unknown!');
                        }
                    } else if (invalid_count > 100) {
                        break;
                    }
                } else if (AjaxNav.fill_first(selectors, data[key])) {
                    // yes, we found some place for our data:
                    data_keys.push(key);
                }
            }
        }
        AjaxNav.scroll_to(scrollto);
        // from history_and_title; but we don't want to push to the state stack
        // here:
        AjaxNav.set_base_url(newurl);
        if (AjaxNav.options.development_mode) {
            if (DEBUG_DOTTED) {
                $('h1').css('border', '3px dotted lime');
            } else {
                $('h1').css('border', '3px dotted red');
            }
            DEBUG_DOTTED = ! DEBUG_DOTTED;
        }
    };
    AjaxNav.process_data = process_data;

    var scroll_to = function (scrollto) {
        var auto_key =         AjaxNav.options.scrollto_auto_key,
            common_selectors = AjaxNav.options.selectors,
            deltay =           AjaxNav.options.scrollto_default_deltay;
        if (scrollto === '@auto') {
            if (auto_key) {  // e.g. 'content'
                scrollto = common_selectors[auto_key];
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
    };
    AjaxNav.scroll_to = scroll_to;

    /**
     * split and trimmed - given a string, return an array
     *
     * options:
     * - splitter - a string, by default ','
     * - trim     - a boolean, by default true
     *
     * The default options are suitable to split e.g. a string which contains
     * one or more CSS selectors.
     * The returned value is a list which doesn't contain empty strings.
     *
     * A non-string argument is expected to be a list already
     * and returned unchanged.
     */
    var split_and_trimmed = function (s, options) {
        var res = [],
            splitter = (typeof options['splitter'] !== 'undefined'
                        ? options['splitter']
                        : ','),
            do_trim = (typeof options['trim'] !== 'undefined'
                       ? (options['trim'] && true || false)
                       : true),
            tmpstr,
            tmplst = [],
            i, len;
        if (! s) {
            return [];
        } else if (typeof s !== 'string') {
            return s;
        }
        if (! splitter) {
            if (do_trim) {
                s = s.trim();
            }
            if (s) {
                return [s];
            } else {
                return [];
            }
        }
        tmplst = s.split(splitter);
        for (i=0, len=tmplst.length; i < len; i++) {
            if (do_trim) {
                tmpstr = tmplst[i].trim();
            } else {
                tmpstr = tmplst[i];
            }
            if (tmpstr) {
                res.push(tmpstr);
            }
        }
        return res;
    }
    AjaxNav.split_and_trimmed = split_and_trimmed;

    /**
     * coerce to list of strings
     *
     * Arguments:
     *
     * - key - an option name
     *
     * - data - an object to contain a <key> which
     *          - might contain data already
     *          - which is converted to a list, if necessary
     * - options - an options object with the following optional keys:
     *             - default - used if data[key] is undefined
     *             - novalue - a list of "non-values" to be returned from
     *               data[key], defaulting to ['@novalue'].
     *
     * There is no return value; the data object is updated in place.
     *
     * data[key], options['default'] and options['novalue'] are converted using
     * AjaxNav.split_and_trimmed as necessary.
     */
    var coerce_to_list_of_strings = function (key, data, options) {
        var val = null,       // defaults for split_and_trimmed:
            options = options || {trim: true, splitter: ","},
            tmpstr,
            tmplst = [],
            novalues,
            i, len,
            changed=false;

        // use default?
        if (typeof data[key] === 'undefined') {
            if (typeof options['default'] !== 'undefined') {
                val = split_and_trimmed(options['default'], options);
                changed = true;
            } else {
                data[key] = [];
                return;
            }
        } else {
            val = data[key];
            if (! val) {
                data[key] = [];
                return;
            }
        }
        // ... default used, if necessary.
        // It might still need to be checked for no-values.

        novalues = (typeof options['novalues'] !== 'undefined'
                    ? split_and_trimmed(options['novalues'], options)
                    : ['@novalue']);
        if (typeof val !== 'object') {
            val = split_and_trimmed(val, options);
            changed = true;
        }
        if (typeof novalues !== 'object') {
            novalues = split_and_trimmed(novalues, options)
        }

        for (i=0, len=val.length; i < len; i++) {
            tmpstr = val[i];
            if (novalues.indexOf(tmpstr) === -1) {
                tmplst.push(tmpstr);
            } else {
                changed = true;
            }
        }
        if (changed) {
            data[key] = tmplst;
        }
    };
    AjaxNav.coerce_to_list_of_strings = coerce_to_list_of_strings;

    // To be called explicitly, optionally providing a key:
    AjaxNav.init = function (key) {
        if (typeof key === 'undefined' || ! key) {
            key = 'default';
        }

        var ajaxnav_init = function (data, textStatus, jqXHR) {
            AjaxNav.log('AjaxNav.init('+key+') received data:');
            AjaxNav.log(data);

            // ------------------------ [ initial (un)delegation ... [
            var whitelist,
                blacklist = data.blacklist,
                i, len, ii, blacklist_length=null, nested,
                key, val, subdata, newlist, chunk,
                selector;

            coerce_to_list_of_strings('whitelist', data, {
                'default': ['body']
                });
            whitelist = data.whitelist;

            coerce_to_list_of_strings('blacklist', data, {
                'default': []
                });
            blacklist = data.blacklist;
            blacklist_length = blacklist.length;
            if (typeof data.nested_blacklist === 'undefined') {
                data.nested_blacklist = false;
            }
            nested = data.nested_blacklist;

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
            coerce_to_list_of_strings('view_ids', data, {
                'default':  ['view',
                             'edit',
                             'base_edit']
                });
            coerce_to_list_of_strings('view_prefixes', data, {
                'default': ['manage_']
                });
            coerce_to_list_of_strings('view_suffixes', data, {
                'default': ['_view']
                });
            // ------------------------- ] ... view name recognition ]

            // ------------------------------------- [ blacklist ... [
            // (view ids which will always be loaded the non-AJAX way)
            coerce_to_list_of_strings('blacklist_view_ids', data, {
                'default': ['edit',
                            'base_edit',
                            'logout',
                            'manage']
                });
            coerce_to_list_of_strings('blacklist_view_prefixes', data, {
                'default': ['manage_']
                });
            coerce_to_list_of_strings('blacklist_view_suffixes', data, {
                'default': ['_edit']
                });
            // ------------------------------------- ] ... blacklist ]

            // --------------------- [ blacklisted by attributes ... [
            // for certain links, identified by classes,
            // we might have a working solution already
            coerce_to_list_of_strings('blacklist_class_ids', data, {
                'default': ['lightbox']
                });
            coerce_to_list_of_strings('blacklist_class_prefixes', data, {
                'default': []
                });
            coerce_to_list_of_strings('blacklist_class_suffixes', data, {
                'default': []
                });
            // Following the Principle of Least Surprise, we regard
            // existing target=_blank attributes by default.
            // You may choose to ignore them, though, since the use of
            // this feature is not recommended.
            if (typeof data.regard_target_attribute === 'undefined') {
                data.regard_target_attribute = true;
            }
            // --------------------- ] ... blacklisted by attributes ]

            // -------------------------------------- [ security ... [
            // see e.g. https://mathiasbynens.github.io/rel-noopener/:
            coerce_to_list_of_strings('target_rel_values', data, {
                'default': ['noopener']
                });
            // -------------------------------------- ] ... security ]

            // ---------------------------- [ keys --> selectors ... [
            if (typeof data.selectors === 'undefined') {
                data.selectors = {
                    content: '#content'
                };
            }
            // convert the strings to lists:
            subdata = data.selectors;
            for (key in subdata) {
                coerce_to_list_of_strings(key, subdata);
            }
            data.selectors = subdata;
            // ---------------------------- ] ... keys --> selectors ]

            // ----------------------------------- [ menu topics ... [
            if (typeof data.menu_item_selector === 'undefined') {
                data.menu_item_selector = '.mainmenu-item > a';
            }
            if (typeof data.menu_item_switched_classname === 'undefined') {
                data.menu_item_switched_classname = 'selected';
            }
            // ----------------------------------- ] ... menu topics ]

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
            // --------------------------- [ development support ... [
            if (typeof data.development_mode === 'undefined') {
                data.development_mode = true;
            }
            // --------------------------- ] ... development support ]
            AjaxNav.options = data;
            // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions
            window.addEventListener('popstate', event => {
                   const { state } = event;
                   console.log(state);
                   AjaxNav.process_data(state);
            });
            AjaxNav.log('AjaxNav.init('+key+') completed.');
        };  // ... ajaxnav_init

        $.ajax({
            dataType: 'json',
            url: '@@ajax-siteinfo'
        })
        .done(function (data, textStatus, jqXHR) {
            var url = AjaxNav.origin = data.site_url;
            url += '/@@ajaxnav-options-'+key;
            AjaxNav.log('Site url is        '+AjaxNav.origin);
            AjaxNav.log('Sending request to '+url);
            $.ajax({
                // dataType: 'json',
                cache: false,  // development
                // url: AjaxNav.origin+'/@@ajaxnav-options-'+key
                url: url
            })
            .done(ajaxnav_init)
            .fail(function (jqXHR, textStatus, errorThrown) {
                AjaxNav.log('E:AjaxNav.init('+key+') --> Error '+textStatus+':');
                AjaxNav.log(jqXHR);
                if (errorThrown !== undefined) {
                    AjaxNav.log(errorThrown);
                }
                // alert('AjaxNav.init: Error '+textStatus+' for key "'+key+'"');
            });
        });
    };  // AjaxNav.init

    log('AjaxNav loaded.')
    return AjaxNav;
})();
// -*- coding: utf-8 -*- vim: ts=4 sw=4 sts=4 expandtab ai noic tw=79 cc=+1
