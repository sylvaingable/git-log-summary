# git log summary

A Python command-line utility to summarize the output of `git log --short-stat`. It aggregates the number of commits and changes made by each author, allowing for different ordering and output formats.

## Getting started

Count commits and changes by author for each day, from all branches and ignoring merge commits:
```
git log --all --no-merges --shortstat --date=short | python git_log_summary.py
```

The git log date format determines the date grouping. For example, here is how to group commits by month:
```
git log --all --no-merges --shortstat --date=format:'%Y-%m' | python git_log_summary.py
```

To write to a file, use the output redirection of your shell. For example, to export to a CSV file:

```
git log --all --no-merges --shortstat --date=short | python git_log_summary.py --output-format csv > commits_summary.csv
```

## Usage
```
git_log_summary.py [-h] [--ordering {chronological,top-changes,top-commits}] [--output-format {text,csv}] [-x [author]]

options:
  -h, --help                                        
  --ordering {chronological,top-changes,top-commits}
  --output-format {text,csv}                        
  -x [author], --exclude [author]
```