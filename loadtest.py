"""basic loadtest scenario(s) for bugzilla server"""

import os
import sys
import aiohttp
import json
import random
from molotov import scenario


try:
    BUGZILLA_HOST = os.environ['BUGZILLA_HOST']
except KeyError:
    sys.exit('ERROR: set BUGZILLA_HOST as env var ---> Aborting!')


# WEIGHT_BUG_VIEW_100_LINKED,           bug_with_comments_plus_links_100
# WEIGHT_BUG_VIEW_5_LINKED,             bug_with_comments_5
# WEIGHT_BUG_VIEW_5_XL,                 bug_with_xl_comments_5
# WEIGHT_TREE_VIEW_75,                  meta_bug_dependency_tree_depth_75', 'show_tree  # noqa
# keyword=regression (LIMIT=500)
# WEIGHT_QUICKSEARCH_KEYWORD,           quicksearch_limited, show_quicksearch_limited   # noqa
# keyword=regression
# WEIGHT_QUICKSEARCH_KEYWORD_UNLIMITED, quicksearch_unlimited, show_quicksearch_unlimited # noqa
# content=website
# WEIGHT_QUICKSEARCH_CONTENT,           quicksearch_content, show_quicksearch_content # noqa

WEIGHT_BUG_VIEW_100_LINKED = int(os.getenv('WEIGHT_BUG_VIEW_100_LINKED') or '0') # noqa
WEIGHT_BUG_VIEW_5_LINKED = int(os.getenv('WEIGHT_BUG_VIEW_5_LINKED') or '0')
WEIGHT_BUG_VIEW_5_XL = int(os.getenv('WEIGHT_BUG_VIEW_5_XL') or '0')
WEIGHT_TREE_VIEW_75 = int(os.getenv('WEIGHT_TREE_VIEW_75') or '0')
WEIGHT_QUICKSEARCH_KEYWORD = int(os.getenv('WEIGHT_QUICKSEARCH_KEYWORD') or '0')  # noqa
WEIGHT_QUICKSEARCH_KEYWORD_UNLIMITED = int(os.getenv('WEIGHT_QUICKSEARCH_KEYWORD_UNLIMITED') or '0')  # noqa
WEIGHT_QUICKSEARCH_CONTENT = int(os.getenv('WEIGHT_QUICKSEARCH_CONTENT') or '0')  # noqa


def cache_bug_list(name_file):
    name_file = name_file.lower()
    path_cache = '.cache/{0}.json'.format(name_file)
    try:
        with open(path_cache) as f:
            return json.load(f)
    except IOError:
        print('ERROR - file: {0}.json not found'.format(name_file))


def url_api(name_file, scenario_type='show_bug'):

    key = name_file.upper()
    # BUG_VIEW
    if scenario_type == 'show_bug':
        res = cache_bug_list(name_file)
        url = '{0}/show_bug.cgi'.format(BUGZILLA_HOST)
        url = '{0}?id={1}'.format(url, res[key])
    # QUICKSEARCH_LIMITED
    elif scenario_type == 'show_quicksearch_limited':
        url = '{0}/buglist.cgi?quicksearch=keyword\%3Dregression'.format(BUGZILLA_HOST)  # noqa
    # QUICKSEARCH_UNLIMITED
    elif scenario_type == 'show_quicksearch_unlimited':
        url = '{0}/buglist.cgi?bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&field0-0-0=keywords&query_format=advanced&type0-0-0=equals&value0-0-0=regression&order=bug_status\%2Cpriority\%2Cassigned_to\%2Cbug_id&limit=0'.format(BUGZILLA_HOST)  # noqa
    # QUICKSEARCH_CONTENT
    elif scenario_type == 'show_quicksearch_content':
        url = '{0}/buglist.cgi?quicksearch=content\%3Awebsite'.format(BUGZILLA_HOST)  # noqa
    # SHOW_TREE
    else:  # scenario_type == 'show_tree':
        res = cache_bug_list(name_file)
        url = '{0}/showdependencytree.cgi'.format(BUGZILLA_HOST)
        url = '{0}?id={1}'.format(url, random.choice(res[key]))
    return url


@scenario(WEIGHT_BUG_VIEW_100_LINKED)
async def load_page_bug_view(session):  # noqa
    _url = url_api('bug_with_comments_plus_links_100')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200


@scenario(WEIGHT_BUG_VIEW_5_LINKED)
async def load_page_bug_view_average(session):
    _url = url_api('bug_with_comments_5')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200


@scenario(WEIGHT_BUG_VIEW_5_XL)
async def load_page_tree_view(session):
    _url = url_api('bug_with_xl_comments_5')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200


@scenario(WEIGHT_TREE_VIEW_75)
async def load_page_tree_view(session):
    _url = url_api('meta_bug_dependency_tree_depth_75', 'show_tree')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200


@scenario(WEIGHT_QUICKSEARCH_KEYWORD)
async def load_quicksearch_limited(session):
    _url = url_api('quicksearch_limited',
                   scenario_type='show_quicksearch_limited')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200


@scenario(WEIGHT_QUICKSEARCH_KEYWORD_UNLIMITED)
async def load_quicksearch_unlimited(session):
    _url = url_api('quicksearch_unlimited',
                   scenario_type='show_quicksearch_unlimited')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200


@scenario(WEIGHT_QUICKSEARCH_CONTENT)
async def load_quicksearch_content(session):
    _url = url_api('quicksearch_content',
                   scenario_type='show_quicksearch_content')

    async with session.get(_url) as resp:
        print(_url)
        assert resp.status == 200
