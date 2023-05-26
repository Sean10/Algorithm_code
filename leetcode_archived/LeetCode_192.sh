#!/bin/bash
cat words.txt | tr -s [:blank:] '\n' | sort -n | uniq -c | sort -r  | awk '{print $2,$1}'
