import pytest

# from bugzilla_rest_client import BugzillaRESTClient
from conftest import (
    bug_with_comments,
    bug_with_many_urls_in_title,
    meta_bug_dependency_tree,
    BUGZILLA_COMMENT_CHAR_LIMIT,
)


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_5_xl_comments(benchmark, rounds):
    bug_with_comments(5,
                      'BUG_WITH_XL_COMMENTS',
                      add_links=False,
                      comment_char_size=BUGZILLA_COMMENT_CHAR_LIMIT,
                      random=False)


# @pytest.mark.skip(reason="TBD")
def test_read_bug_with_5_comments(benchmark, rounds):
    bug_with_comments(5, 'BUG_WITH_COMMENTS')


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_100_comments_plus_links(benchmark, rounds):
    bug_with_comments(100,
                      'BUG_WITH_COMMENTS_PLUS_LINKS',
                      comment_char_size=10000,
                      add_links=True,
                      max_links=6,
                      random=True)


@pytest.mark.skip(reason="TBD")
def test_read_meta_bug_dependency_tree_depth_75(benchmark, rounds):
    meta_bug_dependency_tree(75)


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_many_urls_in_title(benchmark, rounds):
    bug_with_many_urls_in_title()
