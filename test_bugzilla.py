import requests
import pytest

from bugzilla_rest_client import BugzillaRESTClient
from conftest import (
    bug_with_comments,
    bug_with_many_urls_in_title,
    meta_bug_dependency_tree,
    BUGZILLA_HOST,
    BUGZILLA_COMMENT_CHAR_LIMIT,
)


def bugzilla_url_page(host, bug_id, view_type='bug_view'):
    if view_type == 'tree_view':
        return '{0}/showdependencytree.cgi?id={1}'.format(host, bug_id)
    else:
        return '{0}/show_bug.cgi?id={1}'.format(host, bug_id)


def bz_read_page(bug_id, view_type='bug_view', print_html=True):
    """ Queries entire HTML page of bug to simulate performance of user
    experience

    Note:
        REST API only queries specific pieces of data. By querying the same URL
        as the user, we can largely mimic user performance.  Printing out HTML
        to a file give us an easier way to verify we've landed on the correct
        page

    """
    url = bugzilla_url_page(BUGZILLA_HOST, bug_id, view_type)
    resp = requests.get(url)
    # TODO: we need to do a selenium HEADLESS browser launch here.
    if print_html:
        with open('{0}.html'.format(view_type), "w") as html_file:
            html_file.write(resp.text)


def bz_quicksearch(search_string, search_type):
    bz = BugzillaRESTClient()
    return bz.bug_quicksearch(search_string)


# DOCKER
# @pytest.mark.skip(reason="TBD")
def test_quicksearch_limited(benchmark, rounds):
    search_string = 'lorem'
    search_type = 'keyword_limited'
    bugs = bz_quicksearch(search_string, search_type)
    print(bugs)


# DOCKER
# @pytest.mark.skip(reason="TBD")
def test_quicksearch_unlimited(benchmark, rounds):
    search_string = 'lorem'
    search_type = 'keyword_unlimited'
    bugs = bz_quicksearch(search_string, search_type)
    print(bugs)


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_1_xl_comment(benchmark, rounds):
    bug_id = bug_with_comments(1,
                               'BUG_WITH_WITH_XL_COMMENT',
                               add_links=False,
                               comment_char_size=BUGZILLA_COMMENT_CHAR_LIMIT)
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


# DOCKER
# @pytest.mark.skip(reason="TBD")
def test_read_bug_with_5_xl_comments(benchmark, rounds):
    bug_id = bug_with_comments(5,
                               'BUG_WITH_XL_COMMENTS',
                               add_links=False,
                               comment_char_size=BUGZILLA_COMMENT_CHAR_LIMIT,
                               random=False)
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_10_xl_comments(benchmark, rounds):
    bug_id = bug_with_comments(10,
                               'BUG_WITH_WITH_XL_COMMENTS',
                               add_links=False,
                               comment_char_size=BUGZILLA_COMMENT_CHAR_LIMIT)
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


# DOCKER
# @pytest.mark.skip(reason="TBD")
def test_read_bug_with_5_comments(benchmark, rounds):
    bug_id = bug_with_comments(5, 'BUG_WITH_COMMENTS')
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_100_comments(benchmark, rounds):
    bug_id = bug_with_comments(100, 'BUG_WITH_COMMENTS')
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


# DOCKER
# @pytest.mark.skip(reason="TBD")
def test_read_bug_with_100_comments_plus_links(benchmark, rounds):
    bug_id = bug_with_comments(100, 'BUG_WITH_COMMENTS_PLUS_LINKS',
                               comment_char_size=10000, add_links=True,
                               max_links=6, random=True)
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_200_comments(benchmark, rounds):
    bug_id = bug_with_comments(200, 'BUG_WITH_COMMENTS')
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_300_comments(benchmark, rounds):
    bug_id = bug_with_comments(300, 'BUG_WITH_COMMENTS')
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


@pytest.mark.skip(reason="TBD")
def test_read_bug_with_many_urls_in_title(benchmark, rounds):
    bug_id = bug_with_many_urls_in_title()
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs={'bug_id': bug_id})


@pytest.mark.skip(reason="TBD")
def test_read_meta_bug_dependency_tree_depth_3(benchmark, rounds):
    bug_id = meta_bug_dependency_tree(3)
    kwargs = {'bug_id': bug_id, 'view_type': 'tree_view', 'print_html': False}
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs=kwargs)


@pytest.mark.skip(reason="TBD")
def test_read_meta_bug_dependency_tree_depth_50(benchmark, rounds):
    bug_id = meta_bug_dependency_tree(50)
    kwargs = {'bug_id': bug_id, 'view_type': 'tree_view', 'print_html': False}
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs=kwargs)


# DOCKER
# @pytest.mark.skip(reason="TBD")
def test_read_meta_bug_dependency_tree_depth_75(benchmark, rounds):
    bug_id = meta_bug_dependency_tree(75)
    kwargs = {'bug_id': bug_id, 'view_type': 'tree_view', 'print_html': False}
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs=kwargs)


@pytest.mark.skip(reason="TBD")
def test_read_meta_bug_dependency_tree_depth_100(benchmark, rounds):
    bug_id = meta_bug_dependency_tree(100)
    kwargs = {'bug_id': bug_id, 'view_type': 'tree_view', 'print_html': False}
    benchmark.pedantic(bz_read_page, rounds=rounds, kwargs=kwargs)
