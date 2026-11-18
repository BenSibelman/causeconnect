#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: config.py
#   REVISION: June, 2026
#   CREATION DATE: October, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   configuration file for the CauseConnect AI web app
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
#   Two version strings that are used when logging output to the web server.
#   These are also used when saving server and session files.
#
CC_VERS = "p1.0"
CC_VERS_STR = "causeconnect_"+CC_VERS
#
#   These flags control which parts of the system generate debugging output.
#   Debugging is by printing information to the server logs. The first flag
#   GLOBAL_DEBUG indicates the global debugging state. It should probably be
#   False in most cases to limit the total amount of output. The second flag
#   MODULE_DEBUG_OVERRIDE determines whether a specific file (module) can
#   override the GLOBAL_DEBUG state. This should probably be True to allow
#   each module to independently produce debug output.
#
GLOBAL_DEBUG = False            # the global state of the debugging
MODULE_DEBUG_OVERRIDE = True    # if True module debugging overrides global debug
#
#   All LLMs have parameters that allow each request to configure how the LLM
#   should respond. This is a set of global variables that can be used to set
#   a small number of OpenAI parameters. If the flag is commented out then the
#   API request uses the default value of the given model.
#
CC_LLM_MODEL = "gpt-5.4"                 # the version of the model to be used
#CC_LLM_TEMPERATURE = 1.7                # range 0.0 .. 2.0 - Default 1.0
#CC_LLM_TOKEN_LIMIT = 450                # sets a max number of tokens to be generated
#CC_LLM_PRES_PENALTY = 0.5               # range -2.0 .. 2.0 - Default 0.0
#CC_LLM_FREQ_PENALTY = 1.2               # range -2.0 .. 2.0 - Default 0.0
#
#
#   A set of file and directory global varables. The CC_TEMP_FILE_DIRECTORY
#   should be a directory where server data and session state files are stored.
#   The other file name templates are for server data and session data files.
#
#CC_TEMP_FILE_DIRECTORY = "/var/tmp"
CC_TEMP_FILE_DIRECTORY = "web/tmp"
#
CC_SESS_FILE_TEMPLATE = "cc_session_{session_id}.json"
#
#
#   This is a template to store state information that is needed by the web
#   server. A copy of this template is created and loaded when the web server
#   is launched.
#
CC_SERVER_STATE_TEMPLATE = {
    "OPENAI_KEY":       "",         # API key for OpenAI - set on server boot up
}
#
#
#   This is a template that stores session information. Session information
#   is info that we want to persist for the same user for their entire session
#   with Rebert.
#   
CC_SESSION_STATE_TEMPLATE = {
    "session_id":       "",         # a string session ID
    "rec_response":     "",         # text of the LLM response to the recommendation request
    "highlights":       None,       # a list of the highlighted organizations
    "rec_flags":        None,       # a list of the recommendation flags for session
    "ephem_status":     None,       # the state of the ephemeral Q&A
    "active_branch":    "root",     # the name/key for the chat context
    "chat_turns":       None        # a dictionary of chat turn lists
}
#
#   The interface will show a specific set of organizations - right now it is 6.
#   These displayed groups are called 'highlights' to note that they are the current
#   set of organizations that are showing in the display.
#
CC_HIGHLIGHT_TEMPLATE = {
    "column":           "",         # the slot number, or column for this item
    "title":            "",         # the name of this organization
    "synop":            "",         # the text synsopsis of what the organization is about
    "url":              "",         # the URL of the organization's website
    "linktext":         "",         # the text to display on the link to the organization's website
    "rating":           "",         # the AI rating string
    "rationale":        "",         # the rationale for the rating
    "warning":          ""          # any warnings about this item, e.g. that it might be hallucinated
}
#
#   These are the small flags that appear over an organization card when
#   we make a recommendation of an org. There should be six of these, one
#   for each org in the highlight list. The column is used to keep track
#   of which flag matches which org in the interface.
#
CC_REC_FLAGS_TEMPLATE = {
    "column":           "",         # the slot number, or column that this rec flag matches
    "flag":             "",         # the flag is an image
    "text":             "",         # used for the alt text
    "rating":           -1,         # the best rating found
    "rationale":        ""          # the extracted AI rationale for the rating
}
#
#   This template is used in a list where the order of the list corresponds
#   to the order of the organization highlights. This sets the last response that
#   CauseConnect made for a chat on the specific org in the given slot. This is
#   used by the interface to reset the visual of the last turn when the user
#   switches back to discussing an organization they had previously discussed
#
CC_DISCUSSION_TEMPLATE = {
    "column":           "",         # the slot number, or column that this discussion matches
    "last_turn":        ""          # the text of the last turn
}
#
#   The UI state template maintains the variable state of the web interface.
#   These are the interaction elements that appear on the web page, that should
#   be maintained through each round-trip to the server. These variables are
#   collected from the web request, and reset in the web page template before
#   the web server response is sent back to the user.
#
CC_MAINPAGE_UI_STATE_TEMPLATE = {
    "session_id":       "",         # a string session ID
    "cc_text":          "",         # the text of the prior cc_response
    "user_question":    "",         # the text of the user's next turn in the chat
    "synopsis_state":   0,          # state of the toast - showing the synopsis
    "discuss_state":    0,          # which slot (organization) is being discussed
    "ephem_s_state":    1,          # the state of the ephemeral soliciation
    "ephem_q_state":    0,          # the state of the ephemeral rec Q&A session
    "ephem_p_text":     "",         # the ephemeral question being asked
    "ephem_answer":     "",         # the user answer to the ephemeral rec question
    "ephem_q_last":     0,          # if this is the last ephemeral Q&A question
    "highlights_msg":   "",         # message to show above or in place of the highlighted orgs
    "discuss_content":  None,       # list of CC_DISCUSSION_TEMPLATE
    "response_rows":    5,          # the number of rows, estimate to fit a response
    "cc_response":      ""          # the response being returned to the user
}

#
#
#
CC_EPHEM_Q_TEMPLATE = {
    "state":            1,          # if the state is set to zero this
                                    # feature is turned off
    "1": {
        "prompt":       "",         # the prompt that was given to the user
        "response":     ""          # the user's reponse
    },
    "2": {
        "prompt":       "",         # the prompt that was given to the user
        "response":     ""          # the user's reponse
    },
    "3": {
        "prompt":       "",         # the prompt that was given to the user
        "response":     ""          # the user's reponse
    },
    "4": {
        "prompt":       "",         # the prompt that was given to the user
        "response":     ""          # the user's reponse
    }
}
#
#   These are specific starter questions for the ephemeral recommentation 
#   mini-interview. These are basic questions to try and get the user talking or
#   typing about political advocacy. Follow-up questions are driven by the LLM.
#
CC_EPHEM_Q1_OPTIONS = [
    "When you think about changing the world for the better, what issue matters most to you?",
    "Tell me about a time you noticed something going wrong in the world and wished you could do something to change it.",
    "What's the most important aspect of the future you want to create for the next generation?"
]
#
#   When the user doesn't give us enough information, we use these different prompts
#   to try and explain why we are asking again.
#
CC_EPHEM_RETRY_OPTIONS = [
    "I'm going to need a little more description.",
    "What? Maybe you can tell me a bit more information.",
    "I didn't catch that. Could you tell me more?",
    "My recommendation will be better with more description.",
    "I can't make a good suggestion without more info."
]
#
#   The number of requests per second (RPS) to use when querying the URL of an organization
#   to see whether the website really exists. This is meant to be a little slow so that
#   we don't abuse the remote data source.
#
CC_WEBSITE_VERIFICATION_RPS = 2.0
#
#   The possible return values for checking an organization's website.
#
CC_WEBSITE_VERIFICATION_RESULT_NO_PAGE = 0
CC_WEBSITE_VERIFICATION_RESULT_TITLE_MISMATCH = 1
CC_WEBSITE_VERIFICATION_RESULT_TITLE_MATCH = 2
#
#   The default text for organization links.
#
CC_ORGANIZATION_LINK_TEXT = "Get involved!"
#
#   The warning text for different results of website verification.
#
CC_WARNING_TEXT_NO_PAGE = "This organization may not be real. The web address I came up with was invalid."
CC_WARNING_LINK_TEXT_NO_PAGE = "Search to verify"
CC_WARNING_SEARCH_URL_PREFIX = "https://ecosia.org/search?q="
#
CC_WARNING_TEXT_TITLE_MISMATCH = "This organization may not be real. The website title doesn't match what I expected."
CC_WARNING_LINK_TEXT_TITLE_MISMATCH = "View website"
#
#   The default message to show above the highlights.
#
CC_DEFAULT_HIGHLIGHTS_MESSAGE = "Here are some organizations I think would be a good match for your interests and what you have to offer."