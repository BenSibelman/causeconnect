#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: serve_main_page.py
#   REVISION: November, 2026
#   CREATION DATE: June, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   First cut web prototype
#
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import sys, os, datetime, hashlib, random, json, copy
#
from flask import render_template
from markupsafe import escape
#
#
from causeconnect._causeconnect_0_1_.web.config import *    # MODIFIED
from causeconnect._causeconnect_0_1_.web.prompts import *    # MODIFIED
from causeconnect._causeconnect_0_1_.web.llm import *    # MODIFIED
from causeconnect._causeconnect_0_1_.web.utilities import *    # MODIFIED
#
#  
#
MODULE_MAIN_PAGE_DEBUG = False
#
if not MODULE_DEBUG_OVERRIDE:
    MODULE_MAIN_PAGE_DEBUG = GLOBAL_DEBUG
#
#
##############
#
#   MAIN PAGE GENERATION
#
##############
#
def serve_home_page(request, server_state):
    #
    #   This is a hit on the main page - create a session for this user
    session_state = CC_SESSION_STATE_TEMPLATE.copy()
    session_state['session_id'] = generate_session_id(request)
    #
    #   Set up a way to track the current state of the UI - what comes
    #   in the request, and some of what we need to send back
    ui_state = CC_MAINPAGE_UI_STATE_TEMPLATE.copy()
    ui_state['session_id'] = session_state['session_id']
    #
    session_state['highlights'] = list()
    #
    ui_state['discuss_content'] = get_discussion_content_list(session_state)
    #
    #   Iniitalize the list - this relies on the specific highlights
    #rec_flags = init_recommendation_list(session_state)
    session_state['rec_flags'] = dict() #rec_flags
    #
    #   Need to pick one of the ephemeral question starts at random
    session_state['ephem_status'] = CC_EPHEM_Q_TEMPLATE.copy()
    state = session_state['ephem_status']['state']
    if state:
        ui_state['ephem_p_text'] = random.sample(CC_EPHEM_Q1_OPTIONS,1)[0]
        session_state['ephem_status'][str(state)]['prompt'] = ui_state['ephem_p_text']
    else:
        #   Empty emphem_status state - means feature is turned off here
        ui_state['ephem_p_text'] = ""
        ui_state['ephem_s_state'] = 0
        ui_state['ephem_q_state'] = 0
    
    #   Save the session state 
    save_session_state(session_state)
    #
    #   Generate the page
    page = render_template("mainpage.html",
                            state = ui_state,
                            session = session_state)
    print_server_log(f"Session ID: {ui_state['session_id']}",
                    "serve_home_page()",
                    MODULE_MAIN_PAGE_DEBUG)
    return page


##############
#
#   ASK REBERT PAGE GENERATION
#
##############
#
def serve_ask_causeconnect_response(request, server_state):
    #
    #   Collect the data from the form submission
    ui_state = extract_main_page_form_data(request)
    try:
        discuss_slot = int(ui_state['discuss_state'])-1
    except Exception as e:
        print_server_log(f"Could not convert '{ui_state['discuss_state']}' to a slot number.",
                        "serve_ask_causeconnect_response()",
                        MODULE_MAIN_PAGE_DEBUG)
        raise
    #
    #   Attempt to load a state file for this session
    session_state = load_session_state(ui_state['session_id'])
    #
    #   Pull some session variables that we might need - some came from the POST form
    rec_flags = session_state['rec_flags']
    highlight = session_state['highlights'][(discuss_slot)]
    title = highlight['title']
    title_lower = highlight['title'].lower()
    #
    #   Will need to fill this in before generating the resonse
    chat_context = None
    #
    #   If the user didn't ask a question, return mostly the same page
    #   The question needs to have at least 3 'words' and be at least 
    #   10 characters long - that's still pretty short
    question_words = ui_state['user_question'].split()
    if (len(question_words) < 3) or (len(ui_state['user_question']) < 10):
        ui_state['discuss_content'] = get_discussion_content_list(session_state)
        if ui_state['user_question']:
            ui_state['cc_response'] = f"I'm not sure how to answer: \"{ui_state['user_question']}\""
            ui_state['discuss_content'][discuss_slot]['last_turn'] = ui_state['cc_response']
        page = render_template("mainpage.html",
                                state = ui_state,
                                session = session_state)
        return page
    #
    #   We got here, so the user asked a question
    user_turn = new_user_turn(ui_state['user_question'])
    #
    #   If we come back to an existing branch context, restore that
    if (session_state['chat_turns'] is not None) and (title_lower in session_state['chat_turns']):
        session_state['active_branch'] = title_lower
        #   Need to reconstitute the chat context
        chat_context = restore_chat_context(session_state)
        session_state['chat_turns'][session_state['active_branch']].append(user_turn)
        chat_context.addMessage(user_turn)
    else:
        #   This is a new discussion context
        chat_context = new_discussion_context(title)
        #   We just created the context - first message is the system
        #   message - we want that for the chat_turns list
        system_turn = chat_context.getLastMessage()
        session_state['active_branch'] = title_lower
        if not session_state['chat_turns']:
            session_state['chat_turns'] = dict()
        session_state['chat_turns'][session_state['active_branch']] = list()
        session_state['chat_turns'][session_state['active_branch']].append(system_turn)
        #
        session_state['chat_turns'][session_state['active_branch']].append(user_turn)
        chat_context.addMessage(user_turn)
    #
    #   Have a session_state that is new - or from an existing chat
    #   The question that was asked by the user in the web form
    #
    #   Make the request of the remote LLM
    assistant_turn = make_chat_request(chat_context, server_state['OPENAI_KEY'])
    #
    #   Check to see if this is a branching response
    if is_branching_response(assistant_turn):
        #   Remove the user turn, because it is part of the 'branch'
        session_state['chat_turns'][session_state['active_branch']] =\
            session_state['chat_turns'][session_state['active_branch']][:-1]
        assistant_turn = follow_branching_context(user_turn, assistant_turn, 
                                                  session_state, server_state)
    elif is_returning_response(assistant_turn):
        #   Remove the user turn, because it is part of the 'root'
        session_state['chat_turns'][session_state['active_branch']] =\
            session_state['chat_turns'][session_state['active_branch']][:-1]
        assistant_turn = restore_root_context(user_turn, assistant_turn, 
                                              session_state, server_state)
    #
    #   Whatever the assistant said, save that
    session_state['chat_turns'][session_state['active_branch']].append(assistant_turn)
    #   Put the response text into the UI state
    ui_state['cc_response'] = assistant_turn['content']
    #   Save the session state 
    save_session_state(session_state)
    #   Set the last discussion turns
    ui_state['discuss_content'] = get_discussion_content_list(session_state)
    #   Maintain the state of the ephemeral questions
    state = session_state['ephem_status']['state']
    if state:
        ui_state['ephem_p_text'] = session_state['ephem_status'][str(state)]['prompt']
    else:
        #   Empty emphem_status state - means we're done with ephem Q&A
        ui_state['ephem_p_text'] = ""
        ui_state['ephem_s_state'] = 0
        ui_state['ephem_q_state'] = 0
    #
    #   Quick guess of how large the <textarea> could be
    ui_state = estimate_response_textarea_size(ui_state)
    
    page = render_template("mainpage.html",
                            state = ui_state,
                            session = session_state)
    return page


def estimate_response_textarea_size(ui_state=None):
    #   Calculate the number of characters in the response
    rr_len = len(ui_state['cc_response'])
    #   Calculate the number of rows in the response
    rr_rows = len(ui_state['cc_response'].split('\n'))
    
    if (rr_len < 525) and (rr_rows <= 5): 
        ui_state['response_rows'] = "5"
    elif (rr_len < 1025) and (rr_rows <= 8): 
        ui_state['response_rows'] = "8"
    elif (rr_len < 1350) and (rr_rows <= 12): 
        ui_state['response_rows'] = "12"
    else: 
        ui_state['response_rows'] = "15"
    return ui_state


def is_branching_response(assistant_turn=None):
    title = ""
    response = assistant_turn['content']
    if "BRANCH_TO" in response:
        title = response.partition("BRANCH_TO")[2]
        title = title.partition("CONTEXT")[0]
        title = title.replace('"','').strip()
        print_server_log(f"Found branching response to: '{title}'",
                         "is_branching_response()",
                         MODULE_MAIN_PAGE_DEBUG)
    return title



def is_returning_response(assistant_turn=None):
    context = ""
    response = assistant_turn['content']
    if "RETURN_TO" in response:
        context = response.partition("RETURN_TO")[2]
        context = context.partition("CONTEXT")[0]
        context = context.strip()
        print_server_log(f"Found return to: 'root'",
                         "is_returning_response()",
                         MODULE_MAIN_PAGE_DEBUG)
    return context



def follow_branching_context(user_turn=None, assistant_turn=None, 
                             session_state=None, server_state=None):
    # use this to get the organization title
    org_title = is_branching_response(assistant_turn)
    title_lower = org_title.lower()
    #
    #   If we come back to an existing branch context, restore that
    if title_lower in session_state['chat_turns']:
        if title_lower != session_state['active_branch']:
            print_server_log(f"Switching to context: '{title_lower}'",
                             "follow_branching_context()",
                             MODULE_MAIN_PAGE_DEBUG)
        session_state['active_branch'] = title_lower
        #   Need to reconstitute the chat context
        chat_context = restore_chat_context(session_state)
        session_state['chat_turns'][session_state['active_branch']].append(user_turn)
        chat_context.addMessage(user_turn)
    else:
        print_server_log(f"New branching context: '{title_lower}'",
                         "follow_branching_context()",
                         MODULE_MAIN_PAGE_DEBUG)
        #
        #   This is a new branching context.
        #   Hopefully the regular discussion prompt is good enough for this.
        chat_context = new_discussion_context(org_title)
        #   We just created the context - first message is the system
        #   message - we want that for the chat_turns list
        system_turn = chat_context.getLastMessage()
        session_state['active_branch'] = title_lower
        session_state['chat_turns'][session_state['active_branch']]  = list()
        session_state['chat_turns'][session_state['active_branch']].append(system_turn)
        #
        #   Make sure that we ask a generic question specific to the org context
        #   that we just created. A hack for the discussion context switch
        user_turn['content'] = f"Tell me more about the organization '{org_title}'"
        session_state['chat_turns'][session_state['active_branch']].append(user_turn)
        chat_context.addMessage(user_turn)
    #
    #   Make the request of the remote LLM
    assistant_turn = make_chat_request(chat_context, server_state['OPENAI_KEY'])
    #
    #   If we return immediately, update that and create a generic response
    if is_returning_response(assistant_turn):
        response = NO_REVIEWS_RESPONSE.format(title=org_title)
        assistant_turn['content'] = response
        session_state['chat_turns'][session_state['active_branch']].append(assistant_turn)
        session_state['active_branch'] = 'root'
    return assistant_turn



def restore_root_context(user_turn=None, assistant_turn=None, 
                             session_state=None, server_state=None):
    print_server_log("Returning to 'root' context",
                     "restore_root_context()",
                     MODULE_MAIN_PAGE_DEBUG)
    #
    session_state['active_branch'] = 'root'
    chat_context = restore_chat_context(session_state)
    session_state['chat_turns'][session_state['active_branch']].append(user_turn)
    chat_context.addMessage(user_turn)
    assistant_turn = make_chat_request(chat_context, server_state['OPENAI_KEY'])
    return assistant_turn



def get_discussion_content_list(session_state=None):
    discussion_contents = list()
    for i in range(0,6):
        discussing = CC_DISCUSSION_TEMPLATE.copy()
        discussing['column'] = str(i+1)
        discussing['last_turn'] = INIT_DISCUSSION_CONVERSATION
        discussion_contents.append(discussing)
    if session_state['chat_turns']:
        for org in session_state['highlights']:
            column = int(org['column'])-1
            title_lower = org['title'].lower()
            if title_lower in session_state['chat_turns']:
                last_turn = session_state['chat_turns'][title_lower][-1]
                discussion_contents[column]['last_turn'] = last_turn['content']
    return discussion_contents


