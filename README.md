# git log summary

A Python command-line utility to summarize the output of `git log --short-stat`. It aggregates the number of commits and changes made by each author for each month, allowing for different ordering and output formats.

## Getting started

Count commits and changes by author for each month, from all branches and ignoring merge commits:
```
git log --all --no-merges --shortstat --date=short | python git_log_summary.py
```