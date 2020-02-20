#!/bin/bash
# i18ndude should be available in current $PATH (eg by running
# ``export PATH=$PATH:$BUILDOUT_DIR/bin`` when i18ndude is located in your buildout's bin directory)
#
# For every language you want to translate into you need a
# locales/[language]/LC_MESSAGES/visaplan.plone.ajaxnavigation.po
# (e.g. locales/de/LC_MESSAGES/visaplan.plone.ajaxnavigation.po)

domain=visaplan.plone.ajaxnavigation

set -e
cd $(dirname "$0")
i18ndude rebuild-pot --pot $domain.pot --create $domain ../
i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po

version=$(../../../../../tools/full-version)
echo "I:version is $version"
sed --in-place \
	-e "s,^\(\"Project-Id-Version:\) *\(PACKAGE VERSION\|$domain\)\n\",\1 $domain $version\2," \
	--file=update.sed \
	${domain}.pot */LC_MESSAGES/${domain}.po
