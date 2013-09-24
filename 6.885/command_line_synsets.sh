#!/bin/sh

cat synsets.txt | sed 's/[0-9]*,\(.*\),.*/\1/' | uniq -u | wc -l
cat synsets.txt | sed 's/[0-9]*,\(.*\)$/\1/' > synsets.csv
