"""Enables CRUD operations with Bugzilla 5.1 REST API

.. _Bugzilla REST API Docs:
   https://wiki.mozilla.org/Bugzilla:REST_API
   http://bugzilla.readthedocs.org/en/latest/api/index.html

"""


import os
import sys
import json
import requests
from outlawg import Outlawg


if os.environ['BUGZILLA_HOST']:
    BUGZILLA_HOST = os.environ['BUGZILLA_HOST']
else:
    sys.exit('ERROR: BUGZILLA_HOST not specified. --> Aborting!')

if os.environ['BUGZILLA_API_KEY']:
    BUGZILLA_API_KEY = os.environ['BUGZILLA_API_KEY']
else:
    sys.exit('ERROR: BUGZILLA_API_KEY not specified. --> Aborting!')

if os.environ['BUGZILLA_EMAIL']:
    BUGZILLA_EMAIL = os.environ['BUGZILLA_EMAIL']
else:
    sys.exit('ERROR: BUGZILLA_EMAIL not specified. --> Aborting!')

BUGZILLA_PRODUCT = 'Cloud Services'
BUGZILLA_COMPONENT = 'General'
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}


class BugzillaRESTClient(object):
    """Performs CRUD operations against Bugzilla REST API"""

    def __init__(self):
        self.output = Outlawg()
        self.bugzilla_product = BUGZILLA_PRODUCT
        self.bugzilla_component = BUGZILLA_COMPONENT
        self.host = BUGZILLA_HOST
        self.api_key = BUGZILLA_API_KEY

    def _get_json_create(self, short_desc, status, description,
                         cc_mail='', depends_on='', blocks=''):
        """Returns bugzilla JSON string to POST to REST API

        Example:
            short_desc = '[deployment] {0} {1} - {2}'.format(
                application, release_num, environment)

        """
        data = {
            'product': self.bugzilla_product,
            'component': self.bugzilla_component,
            'version': 'unspecified',
            'op_sys': 'All',
            'rep_platform': 'All',
            'short_desc': short_desc,
            'description': description,
            'status': status
        }
        if cc_mail:
            data.update({'cc': [cc_mail]})
        if depends_on:
            data.update({'depends_on': [depends_on]})
        if cc_mail:
            data.update({'blocks': [blocks]})
        return data

    def _get_json_update(self, comment, bug_id):
        """Returns bugzilla JSON as string to PUT to REST API

        """

        data = {
            'ids': [bug_id],
            'comment': comment
        }
        return data

    def _get_json_search(self, summary):
        """Returns bugzilla JSON as string to GET from REST API"""

        data = {
            'summary': summary,
            'product': self.bugzilla_product,
            'component': self.bugzilla_component
        }
        return data

    def bug_read(self, bug_id):
        """Read bug with given bug_num

        Returns:
            json string from REST API

        """
        url = '{0}/rest/bug?api_key={1}&id={2}'.format(
            self.host, self.api_key, bug_id)
        try:
            req = requests.get(url, headers=HEADERS)
        except KeyError:
            exit('\nERROR: {0}!\n'.format(req.text))

        return req.text

    def bug_quicksearch(self, search_string, search_type='content'):
        """Search for bugs with given search_string in bug content

        Note:
            Does not include content in bug title nor do multi-param searches

        Returns:
            list of bug IDs from REST API

        """
        if search_type not in ['content', 'keyword', 'whiteboard']:
            exit('ERROR: invalid search_type.  --> Aborting!')

        url = '{0}/rest/bug?api_key={1}&quicksearch={2}:"{3}"'.format(
            self.host, self.api_key, search_type, search_string)

        try:
            req = requests.get(url, headers=HEADERS)
        except KeyError:
            exit('\nERROR: {0}!\n'.format(req.text))

        return [bug['id'] for bug in req.json()['bugs']]

    def bug_create(self, short_desc, status, description,
                   cc_mail='', depends_on='', blocks=''):
        """Create bugzilla bug with description

        Note:
            On bugzilla-dev - available status:
            NEW, UNCONFIRMED, ASSIGNED, RESOLVED

            On bugzilla - available status:
            NEW, UNCONFIRMED, RESOLVED, REOPENED, VERIFIED
            FIXED, INVALID, WONTFIX, DUPLICATE, WORKSFORME, INCOMPLETE

        Returns:
            json string to POST to REST API

        """

        self.output.header('Creating new bug via bugzilla REST API...')
        url = '{0}/rest/bug?api_key={1}'.format(self.host, self.api_key)
        data = self._get_json_create(
            short_desc, status, description, cc_mail, depends_on, blocks
        )

        print(data)

        req = requests.post(url, data=json.dumps(data), headers=HEADERS)
        try:
            new_bug_id = req.json()['id']
        except KeyError:
            exit('\nERROR: {0}!\n'.format(req.text))

        print('\nNew bug ID: {0}\nDONE!\n\n'.format(new_bug_id))
        return new_bug_id

    def bug_update(self, bug_id, comment='dummy text here'):
        """Update bugzilla bug with new comment

        Returns:
            json string to POST to REST API

        """

        if not bug_id:
            exit('ERROR: bug_id not provided. --> Aborting!')

        self.output.header(
            'Updating bug #{0} via bugzilla REST API...'.format(bug_id))
        url = '{0}/rest/bug/{1}/comment?api_key={2}'.format(
            self.host, bug_id, self.api_key)

        data = self._get_json_update(comment, bug_id)
        print(data)

        req = requests.post(url, data=json.dumps(data), headers=HEADERS)
        new_comment_id = req.json()['id']

        if new_comment_id:
            print(
                '\nComment created! - new comment ID: {0}\n \
                DONE!\n\n'.format(new_comment_id))
        else:
            print(
                '\nERROR: Comment not created!\n\n'.format(new_comment_id))

        return new_comment_id

    def _bug_latest_matching(self, json_bugs_matching):
        """Returns Bug ID from bug with latest time stamp from
        json_search_results

        Returns:
            Bug ID as string

        """
        self.output.header('Retrieve all matching bugs')

        bugs_unsorted = []
        bugs = json_bugs_matching["bugs"]

        for i in range(len(bugs)):
            id = bugs[i]["id"]
            creation_time = bugs[i]["creation_time"]
            bugs_unsorted.append([id, creation_time])

        print(bugs_unsorted)

        self.output.header('Sort bugs by creation_time')
        bugs_sorted = sorted(
            bugs_unsorted, key=lambda bugs_sorted: bugs_sorted[1])

        print(bugs_unsorted)
        print('DONE!')

        self.output.header('Get last bug from sorted list')
        bug_latest = bugs_sorted[-1]

        # return id only
        return bug_latest[0]

    def bug_search(self, summary):
        """ Searches for bugzilla bugs matching summary string

        Returns:
            json string to GET from REST API

        """
        self.output.header('Searching bugs with summary: {0} \n \
            via bugzilla REST API...'.format(summary))
        url = '{0}/rest/bug'.format(self.host)

        print('----------')
        data = self._get_json_search(summary)
        print(data)

        req = requests.get(url, params=data)
        return self._bug_latest_matching(req.json())


def main():

    bz = BugzillaRESTClient()
    status = 'NEW'
    description = 'description here'
    cc_mail = BUGZILLA_EMAIL

    # Example: bug create
    bug_info = {
        'short_desc': 'short_desc: title here',
        'status': status,
        'description': description,
        'cc_mail': cc_mail
    }
    out = bz.bug_create(**bug_info)
    print(out)

    # Example: bug search
    search_info = {
        'summary': 'Loop-Client'
    }
    print(bz.bug_search(**search_info))


if __name__ == '__main__':

    main()
