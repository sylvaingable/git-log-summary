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

## Design notes

Even though this is a simple script, it was implemented with the following considerations in mind:
- It must be kept as a single file so that it can easily be copy/pasted to be used.
- It should have no dependency except the Python standard library so that it doesn't require a preliminary `pip install` to be run.
- It should not use any fancy new feature to stay compatible with older versions of Python (it was tested to work with Python 3.6).
- Even though it would probably not be a problem except for a very large git log, the code processing it uses generators as much as possible for memory efficiency.