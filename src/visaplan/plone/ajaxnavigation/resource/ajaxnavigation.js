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

    var full_url = function (given) {
        var parsed = urlSplit(given),
            offset = 0,
            drop = 0,
            path,
            pathlist,
            shortened,
            suffix,
            parsedloc;  // parsed current location

        // a full url is returned unchanged
        if (parsed.protocol) {
            AjaxNav.log('full_url('+given+'): complete URL');
            return given;
        }

        // site-absolute paths start with '/'
        if (given.startsWith('/')) {
            AjaxNav.log('full_url('+given+'): complete path');
            return AjaxNav.origin + given;
        }

        // query string and fragment
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
                } else if (divider == '') {
                    // a single word; usually the id of a subpage
                    return [_join_path(full_url(viewname), suffix+qs)];
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
        return urlSplit(origin + '/' + s).queryObject;
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
     * A helper for the method history_and_title (below):
     * Set the base url of the page, creating the html > head > base element
     * if necessary.
     */
    var set_base_url = function (url) {
        var head=null,
            base=$('html base').first();
        if (base) {
            base.attr('href', url);
            log('set base[href] to '+url);
        } else {
            $(document).add('<base>').attr('href', url);
            log('created <base> and set href to '+url);
        }
        // Maintain main menu items
        var parsed = urlSplit(url),
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
        if (typeof common_selectors !== 'undefined') {
            for (i=0, len=common_selectors.length; i < len; i++) {
                local_selectors.push(common_selectors[i]);
            }
        }
        return local_selectors;
    };
    AjaxNav.get_fill_selectors = get_fill_selectors;

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
    var use_url = function (url, query) {
        var reply_ok = null,
            newtitle = null,
            newurl = null,
            data_keys = [];
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
                            reply_ok = false;
                            noajax = true;  // from AjaxNav.click
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
            } else if (http_status == 401) {
                unauthorized = true;
                log(url+': unauthorized (NON-NUMERIC)');
            } else {
                log(url+': OTHER ERROR');
            }
            reply_ok = false;
        });  // ... use_url>ajax.fail
        return reply_ok;
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
            unauthorized = false,
            noajax = false;

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
            query['data-'+a] = elem_data[a];
        }
        if (cls) {
            query['_class'] = cls;
        }
        // !!! query._href = full_url(href);
        // -------------------------- ] ... compile query object ]

        // --------------------------- [ try one or two urls ... [
        for (i=0, len=urls_list.length; i < len; i++) {
            if (use_url(urls_list[i], query)) {
                event.preventDefault();
                return
            } else if (unauthorized) {
                return true;
            } else {
                log("Can't use URL " + urls_list[i]);
            }
        }
        // --------------------------- ] ... try one or two urls ]
        return true;
    };  // clickfunc(event)
    AjaxNav.click = clickfunc;

    /* process_data: for the browser history
     *
     * Performs a simplified subset of the processing done by the use_use_url
     * function, (hopefully) sufficient to rebuild a pre-built page from the
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
                    if (data[key]) {
                        reply_ok = false;
                        noajax = true;  // from AjaxNav.click
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

    log('AjaxNav loaded.')
    return AjaxNav;
})();

// To be called explicitly, optionally providing a key:
AjaxNav.init = function (key) {
    if (typeof key === 'undefined' || ! key) {
        key = 'default';
    }

    var ajaxnav_init = function (data, textStatus, jqXHR) {
        AjaxNav.log('AjaxNav.init('+key+') received data:');
        AjaxNav.log(data);

        // ------------------------ [ initial (un)delegation ... [
        var whitelist = data.whitelist,
            blacklist = data.blacklist,
            i, len, ii, blacklist_length=null, nested,
            key, val, newval, newlist, chunk,
            selector;

        if (whitelist === undefined) {
            data.whitelist = whitelist = ['body'];
        }

        if (blacklist === undefined) {
            data.nested_blacklist = nested = false;
            data.blacklist = blacklist = [];
        } else {
            nested = data.nested_blacklist;
            blacklist_length = blacklist.length;
            if (nested === undefined) {
                data.nested_blacklist = nested = false;
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
                                       'logout',
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
        } else {  // convert the strings to lists:
            newval = {}
            for (key in data.selectors) {
                newlist = newval[key] = [];
                val = data.selectors[key].split(',');
                for (i=0, len=val.length; i < len; i++) {
                    chunk = val[i].trim();
                    if (chunk) {
                        newlist.push(chunk);
                    }
                }
            }
            data.selectors = newval;
        }
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
        if (typeof data.development_style_delegate === 'undefined') {
            data.development_style_delegate = {
                'background-color': "lime"
            }
        }
        if (typeof data.development_style_undelegate === 'undefined') {
            data.development_style_undelegate = {
                'background-color': "yellow"
            }
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
        url: location.href+'/@@ajax-siteinfo'
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
};
/*
$(window).on('popstate', function (event) {
    console.log('popstate:');
    console.log(event.state);
});
*/
// -*- coding: utf-8 -*- vim: ts=4 sw=4 sts=4 expandtab ai noic tw=79 cc=+1
