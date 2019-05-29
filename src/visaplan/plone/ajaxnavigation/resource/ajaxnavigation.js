/* visaplan.plone.ajaxnavigation: AJAX navigation for Plone sites
 * Copyright (C) 2019  visaplan GmbH, Bochum, Germany
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
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
    var me = {},
        log = function (txt) {
            if (console && console.log) {
                console.log(txt);
            }
        };
    me.log = log;
	var url = window.location.href;
	var pos1 = url.indexOf('://');
	var tmp = url.slice(pos1+3); // alles ab dem Hostnamen
	var pos2 = tmp.indexOf('/');
	var hostname: tmp.slice(3, tmp.indexOf('/'));
	me.rooturl =  url.slice(0, pos1 + 3 + pos2);
	alert('root-URL ist '+me.rooturl);
	var clickfunc = function (e) {
		log('AjaxNav.click :-)');
		log(e)
		alert(e);
		log(this);
		if (! confirm('OK für AJAX-Laden; Abbruch für undelegate:')) {
			$(this).undelegate('click', clickfunc);
		}
	}
	me.click = clickfunc
	return me;
})();
AjaxNav.init = function (key) {
	if (key === undefined) {
		key = 'default';
	}
	$.ajax({
		dataType: 'json',
		url: rooturl+'/ajaxnav-options-'+key,
		success: function (data, textStatus, jqXHR) {
			AjaxNav.log('AjaxNav.init('+key+') received data:');
			AjaxNav.log(data);
			AjaxNav.options = data;

			var thelist = data.whitelist,
				selector;
			if (thelist === undefined) {
				thelist = ['body'];
			}
			for (var i=0; i < thelist.length; i++) {
				selector = thelist[i]
				$(selector).delegate('a', 'click', AjaxNav.click);
			}
			thelist = data.blacklist;
			if (thelist !== undefined) {
				for (var i=0; i < thelist.length; i++) {
					selector = thelist[i]
					$(selector).undelegate('a', 'click', AjaxNav.click);
				}
			}
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
