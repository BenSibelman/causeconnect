#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#   FILE: ReviewArticleBase.py
#   REVISION: June, 2026
#   CREATION DATE: June, 2026
#   AUTHOR: Ben Sibelman
#
#   This is a simple class for querying a URL to see if it exists and has an expected page title.
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
###
#
#   This base class is a type of HTTPConnection to connect to the
#   different websites
#
import requests.exceptions
from causeconnect_ai.rebert.classes.base.HTTPConnection import HTTPConnection
#
#   Common exceptions we might hit
from requests.exceptions import SSLError
from urllib3.exceptions import MaxRetryError
#
from causeconnect_ai._causeconnect_1_0_.web.config import *
from causeconnect_ai._causeconnect_1_0_.web.utilities import *
from urllib3.exceptions import MaxRetryError

#
CHECK_WEBSITE_DEBUG = True
#
if not CHECK_WEBSITE_DEBUG:
    CHECK_WEBSITE_DEBUG = GLOBAL_DEBUG

#####
#
#   START class CheckWebsite definition
#
#####

###
#
#
#
class CheckWebsite(HTTPConnection):
    '''
    The CheckWebsite class is a subclass of HTTPConnection that connects to a
    website to see if it exists and has an expected page title.
    '''

    def __init__(self, name="CheckWebsite", *args, **kwargs):
        '''
        Initializes the object.

        Optional Parameters:
        name        : An optional description or name for the object
        logger      : An optional Logger object (causeconnect_ai.rebert.classes.base.Logger)
        '''
        super().__init__(name=name, logger=None, *args, **kwargs)
        #
        #   Set a rate limit so that rogue code won't abuse the site
        #   This is quite slow.
        self.setThrottleRate(rps=CC_WEBSITE_VERIFICATION_RPS)
        self.throttlingOn()
        #
        #   Pick a random user agent to simulate a browser reqeust
        self.setUserAgent()

        return

    def check_website(self, url=None, expected_title=None):
        '''
        This requests a webpage using the supplied URL and checks it.

        Parameters:
        url:            a URL to a webpage to be requested and processed
        expected_title: a string used to check the title of the webpage

        Returns
            a code indicating whether the webpage was found and whether the title matched
        '''
        #   Make sure we have at least one of these two parameters
        if not (url):
            print_server_log(f"'url' was empty!",
                             "checkWebsite()",
                             CHECK_WEBSITE_DEBUG)
            return WEBSITE_VERIFICATION_RESULT_NO_PAGE

        url_lower = url.lower()
        self.setRequestPath(url_lower)

        #   Try to get the page
        self.queueRequest()
        try:
            print_server_log(f"Requesting '{url_lower}'",
                             "checkWebsite()",
                             CHECK_WEBSITE_DEBUG)
            self.makeRequest()
        except (requests.exceptions.ConnectionError, SSLError, MaxRetryError):
            print_server_log(f"Hit a connection error!",
                             "checkWebsite()",
                             CHECK_WEBSITE_DEBUG)
            return CC_WEBSITE_VERIFICATION_RESULT_NO_PAGE

        if not self.responses():
            #   No page
            resp_info = self.getPriorRequests()
            if resp_info:
                error = resp_info[0]['error']
                print_server_log(f"HTTP response code: {error['status_code']}, {error['error_message']}",
                                 "checkWebsite()",
                                 CHECK_WEBSITE_DEBUG)

            return CC_WEBSITE_VERIFICATION_RESULT_NO_PAGE

        #   If we get here, the webpage was successfully retrieved

        if not expected_title:
            #   Caller doesn't care about title matching, so just assume it's a match because the page exists
            return WEBSITE_VERIFICATION_RESULT_TITLE_MATCH

        resp = self.nextResponse()
        page = resp.text
        print_server_log(f"Retrieved page with {len(page)} characters",
                         "checkWebsite()",
                         CHECK_WEBSITE_DEBUG)

        #   Remove any part of the expected title after a dash or parenthesis, which will generally be an acronym
        #   or the name of a specific subgroup or program
        expected_title = expected_title.lower()
        expected_title = expected_title.partition(' -')[0]
        expected_title = expected_title.partition(' –')[0]
        expected_title = expected_title.partition(' (')[0]

        #   Try to find the title tag; account for the possibility that it has attributes
        title = parse_tag_contents(page, "<title")
        if title:
            title = title.lower()
            print_server_log(f"Checking actual title '{title}' against expected title '{expected_title}'",
                             "checkWebsite()",
                             CHECK_WEBSITE_DEBUG)

            #   Check if all words in the expected title are also in the actual title
            #   This overcomes issues with e.g. "Red Cross Northwest Region" vs. "Northwest Region | American Red Cross"
            #   We also separate hyphenated words, e.g. "Seattle-King County" in case the website doesn't hyphenate them.
            expected_title_words = expected_title.replace('-', ' ').split(' ')
            found_unmatched_word = False
            for word in expected_title_words:
                if word not in title:
                    found_unmatched_word = True
                    break

            if not found_unmatched_word:
                return CC_WEBSITE_VERIFICATION_RESULT_TITLE_MATCH

        #   If we get here, the title tag didn't return a match. As a last effort, we search the whole page
        #   for the whole title (matching words separately won't work for this).
        print_server_log(f"Checking for expected title '{expected_title}' in page contents",
                         "checkWebsite()",
                         CHECK_WEBSITE_DEBUG)
        page = page.lower()
        if page.find(expected_title) != -1:
            return CC_WEBSITE_VERIFICATION_RESULT_TITLE_MATCH
        else:
            return CC_WEBSITE_VERIFICATION_RESULT_TITLE_MISMATCH