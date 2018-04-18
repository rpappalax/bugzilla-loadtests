import os
import sys
import shutil
import pickle
import json
from random import randint
from itertools import cycle
import pytest
from bugzilla_rest_client import BugzillaRESTClient
# from data.lorem import LOREM as TEXT_RANDOM
from data.moby import MOBY as TEXT_RANDOM


BUGZILLA_TITLE_CHAR_LIMIT = 255
BUGZILLA_COMMENT_CHAR_LIMIT = 65535

PATH_CACHE = '.cache'
RANDOM_URLS = ['google.com', 'youtube.com', 'facebook.com', 'pbskids.org',
               'ebay.com', 'google.es', 'wordpress.com', 'msn.com',
               'cnn.com', 'nytimes.com', 'theguardian.com', 'yahoo.com',
               'dw.com', 'twitter.com', 'rfi.fr', 'amazon.com',
               'washingtonpost.com', 'npr.org', 'bing.com']


bugzilla_client = BugzillaRESTClient()

if not os.path.exists(PATH_CACHE):
    os.makedirs(PATH_CACHE)

if os.environ['BUGZILLA_HOST']:
    BUGZILLA_HOST = os.environ['BUGZILLA_HOST']
else:
    sys.exit('ERROR: BUGZILLA_HOST env var not found. -->Aborting!')


def cache_stack(name_test, named_function, kwargs):
    """Pickler/Unpickler

    Checks if pre-existing data found in local cache. If so, then
    retrieves it.  If not, creates it using the named_function provided,
    then caches for future use

    Args:
        named_function -- function object that can be executed here
        kwargs -- any further args to pass to named_function

    Returns:
        bug_id[s] -- True if cache found, False if not

    """
    path = '{0}/{1}.p'.format(PATH_CACHE, name_test)
    try:
        p = pickle.load(open(path, "rb"))
    except:
        print('DATA CACHE: No cache data found --> creating new')
        resp = named_function(**kwargs)
        p = {name_test: resp}
        pickle.dump(p, open(path, "wb"))

        # read bug_ids needed for loadtests
        path_json = '{0}/{1}.json'.format(PATH_CACHE, name_test.lower())
        with open(path_json, 'w') as f:
            f.write(json.dumps(p))
        return (p[name_test], False)
    else:
        print('DATA CACHE: pre-existing data found --> loading')
        return (p[name_test], True)


def linkify(comment, max_links=6, comment_num=1, name_test=''):
    """Takes text string and intersperses with valid links

    Note:
        creates either Bug ID or Bug comment links

    Args:
        comment -- raw comment text (to be linkified)
        max_links -- # of links per comment
        comment_num -- number of current comment

    Returns:
        comment string with links

    """
    # create list of real bug IDs
    bug_ids = real_bug_ids(max_links + 1)

    link_comment_count = comment_num - 2
    bug_ids_count = 0

    new = []
    link_count = 0
    add_links = True
    words = comment.split(' ')
    # comment_max = comment_num - 1
    for i, word in enumerate(words):

        pair = word
        if add_links:
            if link_count < max_links:
                if i & 1:
                    bug_id = bug_ids[bug_ids_count]
                    pair = '{0} Bug {1}'.format(word, bug_id)
                    bug_ids_count += 1
                else:
                    if link_comment_count > 0:
                        pair = '{0} Comment #{1}'.format(word, link_comment_count) # noqa
                    link_comment_count += 1
                link_count += 1
            else:
                add_links = False
        new.append(pair)
    return ' '.join(new)


def random_text(comment_count, add_links, comment_char_size=500,
                max_links=6, random=True):
    """Generates random text strings from TEXT_RANDOM

    Args:
        comment_count -- # of comments to append to list
        add_links -- boolean True to add links to comment, False for text only
        comment_char_size -- int indicating char size or max char size if
                             random=True
        max_links -- # of links per comment

    Returns:
        list of random comments

    """
    comments = []

    # create an array of comments
    for i in range(0, comment_count):

        comment = ''
        # paragraph 'chunks' to build comment
        for chunk in TEXT_RANDOM:
            if random:
                size = randint(10, comment_char_size)
            else:
                size = comment_char_size
            comment += chunk

            # truncate to comment_char_size (or random size)
            if len(comment) > size:
                comment = comment[:size]
                break

        # add links
        if add_links:
            comment = linkify(comment, max_links, i)
        comments.append(comment)
    return(comments)


def bz_comments_add(bug_num, comment_count=100, add_links=True,
                    comment_char_size=500, max_links=6, random=True):
    comment = ''
    comments = random_text(comment_count, add_links, comment_char_size,
                           max_links, random)
    comments = cycle(comments)
    for i in range(0, comment_count):
        comment = str(next(comments)) + ' '
        bugzilla_client.bug_update(bug_num, comment)


def bz_title(type='generic'):
    """Creates bug title

    Note:
        Bugzilla short_desc size limit <= BUGZILLA_TITLE_CHAR_LIMIT

    """
    if type == 'many_urls':
        titles = ['https://www.' + url for url in RANDOM_URLS]
        title = ' '.join(titles)
        print('TITLE: {0}'.format(title))
        return title[:BUGZILLA_TITLE_CHAR_LIMIT]
    else:
        return 'GENERIC_BUG'


def bug_info(name_test, depends_on='', bug_count=''):
    info = {
        'short_desc': name_test.upper(),
        'status': 'NEW',
        'description': TEXT_RANDOM[0]
    }
    if depends_on:
        info.update({'depends_on': depends_on})
    if bug_count:
        info.update({'bug_count': bug_count})
    return info


def bz_create_bug(**kwargs):
    return bugzilla_client.bug_create(**kwargs)


def bz_create_bugs(bug_count, **kwargs):
    """Create bugs

    Args:
        bug_count -- how many bugs to create
        **kwargs -- variable json blob of bug options

    Returns:
        bug_id_meta -- for page load times, we just want meta bug ID
        (bug_id_meta, [bug_ids]) -- include list of real bugs for cases when
                                    we need to include real bug links in
                                    comments

    """
    bug_id_previous = ''
    bug_ids = []
    for i in range(0, bug_count + 1):
        if i > 0:
            name_test = 'DEPENDENT OF Bug {0}'.format(bug_id_previous)
            b_info = bug_info(name_test, depends_on=bug_id_previous)
            bug_id_previous = bz_create_bug(**b_info)
        else:
            name_test = '[META] DEPTH = {0}'.format(bug_count)
            b_info = bug_info(name_test)
            bug_id_previous = bz_create_bug(**b_info)
        bug_ids.append(bug_id_previous)
    return bug_ids


def real_bug_ids(bug_count=5, name_test='GENERIC_BUG_LIST'):
    """Generates and returns a list of real bug IDs from existing
    bugs on bugzilla host

    Returns:
        bug_ids -- list of real bug IDs

    """
    info = bug_info(name_test, bug_count=bug_count)
    bug_ids, found = cache_stack(name_test, bz_create_bugs, info)
    return bug_ids


@pytest.fixture
def bug_with_comments(comment_count=10, name_test='BUG_WITH_COMMENTS',
                      add_links=True, comment_char_size=500, max_links=6,
                      random=True):
    info = bug_info(name_test)
    bug_title = '{0}_{1}'.format(name_test, comment_count)
    bug_id, found = cache_stack(bug_title, bz_create_bug, info)
    if not found:
        bz_comments_add(bug_id, comment_count, add_links, comment_char_size,
                        max_links, random)
    return bug_id


@pytest.fixture
def bug_with_many_urls_in_title():
    name_test = sys._getframe().f_code.co_name
    bug_title = bz_title('many_urls')
    info = bug_info(bug_title)
    bug_id, found = cache_stack(name_test, bz_create_bug, info)
    return bug_id


@pytest.fixture
def meta_bug_dependency_tree(bug_count=10):
    name_test = sys._getframe().f_code.co_name
    bug_title = '{0}_depth_{1}'.format(name_test, bug_count).upper()
    info = bug_info(bug_title, bug_count=bug_count)
    bug_ids, found = cache_stack(bug_title, bz_create_bugs, info)
    # meta bug is the first one
    return bug_ids[0]


def pytest_addoption(parser):
    parser.addoption("--clear-cache", action="store_true",
                     help="clear bugzilla query cache")
    parser.addoption("--rounds",
                     default=1, help="number of benchmarking rounds")


def pytest_generate_tests(metafunc):
    clearcache = metafunc.config.getoption('clear_cache')
    if clearcache:
        shutil.rmtree(PATH_CACHE)
        os.makedirs(PATH_CACHE)


@pytest.fixture
def rounds(request):
    rounds = request.config.getoption("rounds")
    if rounds:
        return int(rounds)
    else:
        return 1
