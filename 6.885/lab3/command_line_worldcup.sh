#!/bin/sh

cat worldcup.txt | sed 's/\[\[\([0-9]*\)[^]]*\]\]/\1/g; s/.*fb|\([A-Za-z]*\)}}/\1/g; s/<sup><\/sup>//g; s/|bgcolor[^|]*//g; s/|align=center[^|]*//g' | tail -171 | head -168 | grep -v '-' | grep -v '|[0-9]\+\s\?$' | awk '/^[A-Z]/ {country = $0} !/^[A-Z]/ {print country, $0}' | sed 's/|[0-9]\+/|/g' | grep '[0-9]' | awk '/.*$/ {blah = $0} BEGIN { i = 0} { if (i == 4) { i = 1 } else { i += 1 }; print i, ",", blah }' | sed 's/[\(\)]/ /g' | awk -F '|' '{n = split($2, years, ","); for (i=1; i<=n; i++) {print $1, ",", years[i]} }' | sed 's/\s\+//g'
