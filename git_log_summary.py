from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from functools import reduce
from itertools import chain, cycle, tee
from typing import Generator, NamedTuple, TextIO

CHRONOLOGICAL_ORDERING = "chronological"
TOP_CHANGES_ORDERING = "top-changes"
TOP_COMMITS_ORDERING = "top-commits"

TEXT_OUTPUT = "text"
CSV_OUTPUT = "csv"


def main(args: list[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ordering",
        choices=[CHRONOLOGICAL_ORDERING, TOP_CHANGES_ORDERING, TOP_COMMITS_ORDERING],
        default=CHRONOLOGICAL_ORDERING,
    )
    parser.add_argument(
        "--output-format", choices=[TEXT_OUTPUT, CSV_OUTPUT], default=TEXT_OUTPUT
    )
    parser.add_argument(
        "-x",
        "--exclude",
        nargs="?",
        action="append",
        type=str,
        default=[],
        metavar="author",
        dest="excluded_authors",
    )
    args = parser.parse_args(args)

    commits_logs = chunk_git_log(sys.stdin)
    commits = (parse_commit_log(commit_log) for commit_log in commits_logs)

    data = defaultdict(lambda: defaultdict(lambda: {"commits": 0, "changes": 0}))
    excluded_authors = set(args.excluded_authors)
    for commit in commits:
        if commit.author in excluded_authors or commit.email in excluded_authors:
            continue

        data[commit.date][commit.author]["commits"] += 1
        data[commit.date][commit.author]["changes"] += commit.changes

    for authors in data.values():
        authors_count = len(authors)
        authors["Total"]["commits"] = sum(a["commits"] for a in authors.values())
        authors["Total"]["changes"] = sum(a["changes"] for a in authors.values())
        authors["Average"]["commits"] = authors["Total"]["commits"] // authors_count
        authors["Average"]["changes"] = authors["Total"]["changes"] // authors_count

    commits_stats = sort_commits_stats(data, args.ordering)
    write_to_stdout(commits_stats, args.output_format)


def chunk_git_log(file_object: TextIO) -> Generator[str, None, None]:
    """Chunk a git log by commit."""
    chunk = []
    iterator = iter(file_object)
    while True:
        try:
            line = next(iterator)
        except StopIteration:
            if chunk:
                yield "".join(chunk)
            break
        if line.startswith("commit") and chunk:
            yield "".join(chunk)
            chunk = []
        if bool(line.strip()):  # Skip empty lines
            chunk.append(line)


class Commit(NamedTuple):
    author: str
    email: str
    date: str
    changes: int


# Regular expressions to match author, date and changes
author_re = re.compile(r"Author: (.+) <(.+)>")
date_re = re.compile(r"Date:\s+(\d{4}-\d{2})")
insertions_re = re.compile(r"(\d+) insertions?")
deletions_re = re.compile(r"(\d+) deletions?")
first_group = lambda match: next(iter(match.groups()))  # noqa: E731
first_group = lambda match: match.groups()[0]  # noqa: E731
second_group = lambda match: match.groups()[1]  # noqa: E731


def parse_commit_log(commit_log: str) -> Commit:
    author_match = author_re.search(commit_log)
    date_match = date_re.search(commit_log)
    insertions_match = insertions_re.search(commit_log)
    deletions_match = deletions_re.search(commit_log)

    author = first_group(author_match)
    email = second_group(author_match)
    commit_date = first_group(date_match)
    insertions = int(first_group(insertions_match)) if insertions_match else 0
    deletions = int(first_group(deletions_match)) if deletions_match else 0
    return Commit(author, email, commit_date, insertions + deletions)


def sort_commits_stats(
    commits_stats: dict[str, dict[str, dict[str, int]]], ordering: str
) -> list[str, dict[str, dict[str, int]]]:
    if ordering == CHRONOLOGICAL_ORDERING:
        return sorted(commits_stats.items(), key=lambda t: t[0])
    elif ordering == TOP_CHANGES_ORDERING:
        return sorted(
            commits_stats.items(),
            key=lambda t: t[1]["Average"]["changes"],
            reverse=True,
        )
    elif ordering == TOP_COMMITS_ORDERING:
        return sorted(
            commits_stats.items(),
            key=lambda t: t[1]["Average"]["commits"],
            reverse=True,
        )
    else:
        raise ValueError(f"Unknown ordering: {ordering}")


def to_text(
    file_object: TextIO, commits_stats: list[str, dict[str, dict[str, int]]]
) -> None:
    for date, authors in commits_stats:
        file_object.write(f"Date: {date}\n")
        for author, stats in authors.items():
            file_object.write(
                f'  {author:<20} commits: {stats["commits"]:>4}\tchanges: {stats["changes"]:>6}\n'
            )
        file_object.write("\n")


def to_csv(
    file_object: TextIO, commits_stats: list[str, dict[str, dict[str, int]]]
) -> None:
    # Find the longest list of authors
    authors = reduce(
        lambda acc, authors: authors if len(authors) > len(acc) else acc,
        (authors for _, authors in commits_stats),
        [],
    )
    # Each author requires two columns: one for commits and one for changes
    duplicated_authors = chain.from_iterable(zip(*tee(authors, 2)))
    authors_fields = tuple(
        f"{author} {col}"
        for author, col in zip(duplicated_authors, cycle(["commits", "changes"]))
    )
    # Use a dict writer to set empty values for authors that don't have commits on a
    # given date
    csv_writer = csv.DictWriter(file_object, fieldnames=["Date", *authors_fields])
    csv_writer.writeheader()
    for date, authors in commits_stats:
        row = {"Date": date}
        for author, stats in authors.items():
            row[f"{author} commits"] = stats["commits"]
            row[f"{author} changes"] = stats["changes"]
        csv_writer.writerow(row)


def write_to_stdout(
    commits_stats: list[str, dict[str, dict[str, int]]], output_format: str
):
    if output_format == TEXT_OUTPUT:
        to_text(sys.stdout, commits_stats)
    elif output_format == CSV_OUTPUT:
        to_csv(sys.stdout, commits_stats)


if __name__ == "__main__":
    main(sys.argv[1:])
