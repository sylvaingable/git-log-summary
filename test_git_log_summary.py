import runpy
from io import StringIO

import pytest

from git_log_summary import CSV_OUTPUT, TEXT_OUTPUT, summarize_git_log


@pytest.fixture
def git_log():
    yield StringIO(GIT_LOG_SAMPLE)


@pytest.mark.parametrize("output_format", [TEXT_OUTPUT, CSV_OUTPUT])
def test_summarize_git_log(git_log, snapshot, output_format):
    """
    Given the git log output of a project with 10 commits from 3 authors.
    When summarizing the git log using the default options.
    Then the text summary is correct.
    """
    summary = summarize_git_log(git_log, output_format=output_format)
    assert summary == snapshot


@pytest.mark.parametrize("author_filter", ["Alice", "alice@example.com"])
def test_can_exclude_commits_by_author(git_log, author_filter):
    """
    Given the git log output of a project with 10 commits from 3 authors.
    When summarizing the git log excluding Alice.
    Then Alice's commits are not included in the summary.
    """
    summary = summarize_git_log(git_log, excluded_authors=[author_filter])
    assert "Alice" not in summary


def test_can_execute_as_cli(monkeypatch, capsys, git_log):
    """
    Given the git log output of a project with 10 commits from 3 authors.
    When running the script as a CLI command.
    Then the output is not empty.
    """
    monkeypatch.setattr("sys.argv", ["git_log_summary.py"])
    monkeypatch.setattr("sys.stdin", git_log)
    runpy.run_module("git_log_summary", run_name="__main__")
    captured = capsys.readouterr()
    assert captured.out != ""


GIT_LOG_SAMPLE = """
commit b7fa8da016c6e7570be246861ed8c2ca3f0b3abe
Author: Alice <alice@example.com>
Date:   2024-04-01

    more ignored words 

 7 files changed, 95 insertions(+), 107 deletions(-)

commit 23c48e63babb0cd39a847dac5458c67bea5aeabb
Author: Bob <bob@example.com>
Date:   2024-04-01

    Don't mess with Voodoo

 3 files changed, 53 insertions(+), 12 deletions(-)

commit fb0446c77f4eb45e7cae648ea77aa6da0a6c88a1
Author: Alice <alice@example.com>
Date:   2024-04-01

    should work now.

 15 files changed, 345 insertions(+), 437 deletions(-)

commit 179797fb36a6252426ddcdc02f5f10bd68b17e9a
Author: Charlie <charlie@example.com>
Date:   2024-04-01

    Temporary commit.

 8 files changed, 191 insertions(+), 11 deletions(-)

commit fe50e85b063036614a86fb1147a7315b43932f80
Author: Bob <bob@example.com>
Date:   2024-04-01

    pay no attention to the man behind the curtain

 2 files changed, 61 insertions(+), 14 deletions(-)

commit c63bfcf27050117d60e5edc43fa8a1667344c07b
Author: Bob <bob@example.com>
Date:   2024-04-01

    hmmm

 1 file changed, 31 deletions(-)

commit 32d0414004a0263cbec83469ff0fc4b3dcde2695
Author: Bob <bob@example.com>
Date:   2024-03-29

    We Had To Use Dark Magic To Make This Work

 1 file changed, 12 insertions(+)

commit 3ff3b1d296089003a93c75b736974cc33d3d4af5
Author: Bob <bob@example.com>
Date:   2024-03-28

    It's getting hard to keep up with the crap I've trashed

 18 files changed, 433 insertions(+), 275 deletions(-)

commit f18a416618d472aed9e9483609664099be392e50
Author: Charlie <charlie@example.com>
Date:   2024-03-28

    Gotta make you understand

 10 files changed, 238 insertions(+), 1 deletion(-)

commit 7a4db0e1cc4810207b2f49ef0006e4d7e0153c2c
Author: Alice <alice@example.com>
Date:   2024-03-28

    Spinning up the hamster...

 15 files changed, 577 insertions(+), 106 deletions(-)
"""
