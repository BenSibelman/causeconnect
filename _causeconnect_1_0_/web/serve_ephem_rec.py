#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: serve_ephem_rec.py
#   REVISION: June, 2026
#   CREATION DATE: October, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   Server code to generate ephemeral recommendations. Question generation by the LLM
#   and recommendations based on the user's answers to the questions.
#
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import sys, os, datetime, hashlib, random, json, copy

from flask import render_template
from markupsafe import escape
#
#
from causeconnect_ai._causeconnect_1_0_.web.config import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.prompts import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.llm import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.utilities import *    # MODIFIED
#
#  
#
MODULE_EPHEM_REC_DEBUG = True
#
if not MODULE_DEBUG_OVERRIDE:
    MODULE_EPHEM_REC_DEBUG = GLOBAL_DEBUG
#
#
#
#
##############
#
#   EPHEMERAL RECOMMENDATION PAGE GENERATION
#
##############
#
#
#
def serve_next_ephem_question(request, server_state):
    #   Collect the data from the form submission
    ui_state = extract_main_page_form_data(request)
    #   Attempt to load a state file for this session
    session_state = load_session_state(ui_state['session_id'])
    #
    #   Set the last discussion turns
    ui_state['discuss_content'] = get_discussion_content_list(session_state)
    #
    #   Return the basic page when done with Q&A
    state = session_state['ephem_status']['state']
    if not state:
        #   Empty emphem_status state - means we're done with ephem Q&A
        ui_state['ephem_p_text'] = ""
        ui_state['ephem_s_state'] = 0
        ui_state['ephem_q_state'] = 0
        ui_state['ephem_q_last'] = 1
        page = render_template("mainpage.html",
                                state = ui_state,
                                session = session_state)
        print_server_log(f"Q&A is done!",
                        "serve_next_ephem_question()",
                        MODULE_EPHEM_REC_DEBUG)
        return page
    #
    #   Try to get more from the user when their response is really short
    answer_words = ui_state['ephem_answer'].split()
    if (len(answer_words) < 3) or (len(ui_state['ephem_answer']) < 10):
        old_prompt = session_state['ephem_status'][str(state)]['prompt']
        retry = random.sample(CC_EPHEM_RETRY_OPTIONS,1)[0]
        new_prompt = f"{retry} ... {old_prompt}"
        ui_state['ephem_p_text'] = new_prompt
        page = render_template("mainpage.html",
                                state = ui_state,
                                session = session_state)
        print_server_log(f"Short response for question {state}, trying to get more.",
                        "serve_next_ephem_question()",
                        MODULE_EPHEM_REC_DEBUG)
        return page
    #
    #   The response must have been something, so save that response and move to
    #   the next Q&A prompt pair
    session_state['ephem_status'][str(state)]['response'] = ui_state['ephem_answer']
    state += 1
    session_state['ephem_status']['state'] = state
    if state == 0:
        ui_state['ephem_q_last'] = 1
    elif state == 4:
        session_state['ephem_status'][str(state)]['prompt'] = EPHEM_QUESTION_4
        ui_state['ephem_p_text'] = EPHEM_QUESTION_4
        ui_state['ephem_q_last'] = 1
    elif state > 4:
        #   This code is here as a - just in case - this should not execute
        #   The UI should show a button that calls serve_ephemeral_rec()
        session_state['ephem_status']['state'] = 0
        ui_state['ephem_p_text'] = ""
        ui_state['ephem_s_state'] = 0
        ui_state['ephem_q_state'] = 0
        ui_state['ephem_q_last'] = 1
        page = render_template("mainpage.html",
                                state = ui_state,
                                session = session_state)
        print_server_log(f"Q&A is done!",
                        "serve_next_ephem_question()",
                        MODULE_EPHEM_REC_DEBUG)
        return page
    else:
        #
        #   Get a question from the LLM and save that
        qna_str = create_ephem_qna_str(session_state)
        assistant_turn = qna_question_request(session_state, qna_str, server_state['OPENAI_KEY'])
        session_state['ephem_status'][str(state)]['prompt'] = assistant_turn['content']
        ui_state['ephem_p_text'] = assistant_turn['content']

    ui_state['ephem_s_state'] = 0
    ui_state['ephem_q_state'] = 1
    #   Save the session state 
    save_session_state(session_state)
    #
    page = render_template("mainpage.html",
                            state = ui_state,
                            session = session_state)
    return page


#
#
#
def serve_ephem_recommendation(request, server_state, local_only):
    #   Collect the data from the form submission
    ui_state = extract_main_page_form_data(request)
    #   Attempt to load a state file for this session
    session_state = load_session_state(ui_state['session_id'])
    #
    #   Try to get more from the user when their response is really short
    state = session_state['ephem_status']['state']
    answer_words = ui_state['ephem_answer'].split()
    if (len(answer_words) < 3) or (len(ui_state['ephem_answer']) < 10):
        old_prompt = session_state['ephem_status'][str(state)]['prompt']
        retry = random.sample(CC_EPHEM_RETRY_OPTIONS,1)[0]
        new_prompt = f"{retry} ... {old_prompt}"
        ui_state['ephem_p_text'] = new_prompt
        if (state == 4) or (state == 0):
            ui_state['ephem_q_last'] = 1
        page = render_template("mainpage.html",
                                state = ui_state,
                                session = session_state)
        print_server_log(f"Short response for question {state}, trying to get more.",
                        "serve_ephem_recommendation()",
                        MODULE_EPHEM_REC_DEBUG)
        return page
    #
    #   Save the response and update the state count
    session_state['ephem_status'][str(state)]['response'] = ui_state['ephem_answer']
    state += 1
    session_state['ephem_status']['state'] = state
    print_server_log(f"User completed Q&A",
                    "serve_ephem_rec()",
                    MODULE_EPHEM_REC_DEBUG)
    if (state == 4) or (state == 0):
        ui_state['ephem_q_last'] = 1
    elif state > 4:
        #   This sets the last question - below we make the recommendation
        session_state['ephem_status']['state'] = 0
        ui_state['ephem_p_text'] = ""
        ui_state['ephem_s_state'] = 0
        ui_state['ephem_q_state'] = 0
        ui_state['ephem_q_last'] = 1
    #
    #
    print_server_log(f"Starting ephemeral recommendation request after answering question {state - 1}, with local_only={local_only}.",
                    "serve_ephem_recommendation()",
                    MODULE_EPHEM_REC_DEBUG)
    start_time = datetime.datetime.now()
    session_state = make_ephem_rec_request(session_state, server_state['OPENAI_KEY'], local_only)
    finish_time = datetime.datetime.now()
    runtime = finish_time-start_time
    print_server_log(f"Ephemeral recommendation elapsed time: {runtime}",
                    "serve_ephem_recommendation()",
                    MODULE_EPHEM_REC_DEBUG)
    #
    #   Check if we have highlights; if not, the LLM response should explain why
    if (len(session_state['highlights']) == 0):
        ui_state['highlights_msg'] = session_state['rec_response']
    else:
        ui_state['highlights_msg'] = CC_DEFAULT_HIGHLIGHTS_MESSAGE
        #
        #   Need to update the flag images based on the recommendation results
        rec_flags = update_recommendation_flags(session_state)
        session_state['rec_flags'] = rec_flags
        #
        #   Make sure there is a 'root' context for a chat - the interface tries to keep
        #   a discussion on the topic of a specific organization - but the user might go more generic
        if (not session_state['chat_turns']) or ('root' not in session_state['chat_turns']):
            initialize_root_chat_context(session_state)
        #
        #   Set the last discussion turns - with the data from the recommendations
        ui_state['discuss_content'] = get_discussion_content_list(session_state)

    #   Save the session
    save_session_state(session_state)
    #
    page = render_template("mainpage.html",
                            state = ui_state,
                            session = session_state)
    return page



def get_discussion_content_list(session_state):
    discussion_contents = list()
    for i in range(0,6):
        discussing = CC_DISCUSSION_TEMPLATE.copy()
        discussing['column'] = str(i+1)
        discussing['last_turn'] = INIT_DISCUSSION_CONVERSATION
        if session_state['rec_flags'] and session_state['rec_flags'][i]['rationale']:
            rating = session_state['rec_flags'][i]['rating'].lower()
            turn = f"Based on the answers you gave to my mini interview, I predict this organization is {rating} with your interests.\n\n"
            turn = turn + session_state['rec_flags'][i]['rationale']+"\n\n"
            turn = turn + "What else would you like to know about this organization?"
            discussing['last_turn'] = turn

        discussion_contents.append(discussing)
    #
    #
    if session_state['chat_turns']:
        for org in session_state['highlights']:
            column = int(org['column'])-1
            title_lower = org['title'].lower()
            if title_lower in session_state['chat_turns']:
                last_turn = session_state['chat_turns'][title_lower][-1]
                discussion_contents[column]['last_turn'] = last_turn['content']
                print_server_log(f"Replaced 'rationale' with last turn for '{title_lower}'.",
                                  "get_discussion_content_list()",
                                  MODULE_EPHEM_REC_DEBUG)
            else:
                print_server_log(f"Kept 'rationale' as last turn for '{title_lower}'.",
                                  "get_discussion_content_list()",
                                  MODULE_EPHEM_REC_DEBUG)
    return discussion_contents



def update_recommendation_flags(session_state):
    rec_list = list()
    if session_state['highlights']:
        for i in range(0, len(session_state['highlights'])):
            recitem = CC_REC_FLAGS_TEMPLATE.copy()
            recitem['column'] = str(i + 1)
            recitem['flag'] = ""
            recitem['text'] = ""
            rec_list.append(recitem)

        for org in session_state['highlights']:
            column = int(org['column'])-1
            title_lower = org['title'].lower()
            #
            #   Save the rating and rationale strings with the org
            rating = org['rating'].lower()
            rec_list[column]['rating'] = org['rating']
            rec_list[column]['rationale'] = org['rationale']
            #
            #   Now, assign a recommendation flag
            if 'highly' in rating:
                #   CauseConnect thinks there is a strong match
                rec_list[column]['flag'] = "rec-highly-small.png"
                rec_list[column]['text'] = "recommendation: highly recommended"
            elif 'mildly' in rating:
                #   CauseConnect thinks there is some match, but not as strong
                rec_list[column]['flag'] = "rec-suggested-small.png"
                rec_list[column]['text'] = "recommendation: suggested"
            else:
                print_server_log(f"Unexpected rating for '{title_lower}': '{rating}'",
                                 "update_recommendation_flags()",
                                 MODULE_EPHEM_REC_DEBUG)
                continue
            print_server_log(f"Recommendation for '{title_lower}' is '{rec_list[column]['text']}'",
                             "update_recommendation_flags()",
                             MODULE_EPHEM_REC_DEBUG)
                             
    return rec_list


#
#   This creates a 'root' context for a chat - in case the org context breaks
#   and the discussion of a specific org becomes more generic.
#
def initialize_root_chat_context(session_state=None):
    #   Have not yet started answering questions about orgs
    org_info_str = create_org_info_str(session_state['highlights'])
    #   Create a 'root' context, including the new release information
    chat_context = new_root_context(org_info_str)
    #   In that chat context, the first message is the system message
    #   we want that for the chat_turns list
    system_turn = chat_context.getLastMessage()
    if not session_state['chat_turns']:
        session_state['chat_turns'] = dict()
    session_state['chat_turns']['root']  = list()
    session_state['chat_turns']['root'].append(system_turn)
    return

