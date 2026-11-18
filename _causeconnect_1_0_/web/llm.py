#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: llm.py
#   REVISION: June, 2026
#   CREATION DATE: October, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   The functions that handle interacting with the LLM
#
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import sys, os, datetime, time, hashlib, json, copy
#
from causeconnect_ai._causeconnect_1_0_.web.config import *
from causeconnect_ai._causeconnect_1_0_.web.prompts import *
from causeconnect_ai._causeconnect_1_0_.web.utilities import *
from causeconnect_ai._causeconnect_1_0_.web.check_website import CheckWebsite
#
#
#   This comes from the rebert class library and manages API keys
#   You should use it to store your OpenAI API key locally, so your
#   key is not stored as a constant in the code.
from causeconnect_ai.rebert.classes.data.KeyManager import KeyManager
#
#   This class encapsulates the OpenAI chat completion API. It is
#   a 'souped up' version of the calls that were being made to
#   the requests library in the prior prototypes. This Chat class
#   will help with some error handling and simplify how we make
#   API calls.
from causeconnect_ai.rebert.classes.OpenAI.Chat import Chat
#
#   These two classes are data structures that help construct and
#   manage the chat request body. As our requests get more complex
#   we will want a way to manage them.
from causeconnect_ai.rebert.classes.OpenAI.payload.ChatMessage import ChatMessage
from causeconnect_ai.rebert.classes.OpenAI.payload.ChatRequestPayload import ChatRequestPayload
#
#
#

MODULE_LLM_DEBUG = True

if not MODULE_DEBUG_OVERRIDE:
    MODULE_LLM_DEBUG = GLOBAL_DEBUG


##############
#
#   OpenAI - LLM
#
##############
#
#   The code needs to maintain the status of the chat. This status 
#   will include parameters that tell the model how it should respond
#   as well as all of the user questions and the responses.
#
def new_root_context(org_data_str=""):
    chat_context = ChatRequestPayload()
    sprompt = ROOT_CONTEXT_PROMPT.format(org_data_str=org_data_str)
    
    system_turn = ChatMessage()
    system_turn.setRole("system")
    system_turn.setContent(sprompt)
    
    chat_context.addMessage(system_turn)
    return chat_context
#
#
def new_discussion_context(org_title=""):
    chat_context = ChatRequestPayload()
    sprompt = ORG_CONTEXT_PROMPT.format(org_title=org_title)
    system_turn = ChatMessage()
    system_turn.setRole("system")
    system_turn.setContent(sprompt)
    
    chat_context.addMessage(system_turn)
    return chat_context

#
#
#   This sets the configuration parameters, based on constants defined in the
#   config.py file. If a constant is undefined, then this will use the model
#   default value.
def configure_model_params(chat_context=None):
    #   If there is no chat context, raise an error
    if not chat_context:
        raise Exception("No chat_context has been supplied")
    #
    #   Set configuration values
    used_pres_penalty = False
    try:
        chat_context.setModel(CC_LLM_MODEL)
    except NameError as ex:
        print_server_log(f"There must be a model to make a request!","make_chat_request()",
                        MODULE_LLM_DEBUG)
        print_server_log(f"Caught exception","make_chat_request()",MODULE_LLM_DEBUG)
        print_server_log(f"{e}","make_chat_request()",MODULE_LLM_DEBUG)
        raise
    
    try:
        chat_context.setTemperature(CC_LLM_TEMPERATURE)
    except NameError as e:
        pass
        #print_server_log(f"Using default LLM temperature","configure_model_params()",
        #                MODULE_LLM_DEBUG)
        #print_server_log(f"Caught exception","configure_model_params()",MODULE_LLM_DEBUG)
        #print_server_log(f"{e}","configure_model_params()",MODULE_LLM_DEBUG)
    
    try:
        chat_context.setMaxTokens(CC_LLM_TOKEN_LIMIT)
    except NameError as e:
        pass
        #print_server_log(f"Using default max completion tokens", "configure_model_params()",
        #                MODULE_LLM_DEBUG)
        #print_server_log(f"Caught exception","configure_model_params()",MODULE_LLM_DEBUG)
        #print_server_log(f"{e}","configure_model_params()",MODULE_LLM_DEBUG)
    
    try:
        chat_context.setPresencePenalty(CC_LLM_PRES_PENALTY)
        used_pres_penalty = True
    except NameError as e:
        pass
        #print_server_log(f"Using default LLM presence_penalty","configure_model_params()",
        #                MODULE_LLM_DEBUG)
        #print_server_log(f"Caught exception","configure_model_params()",MODULE_LLM_DEBUG)
        #print_server_log(f"{e}","configure_model_params()",MODULE_LLM_DEBUG)

    #
    #   Can only use one of either frequency penalty or presence penalty
    if not used_pres_penalty:
        try:
            chat_context.setFrequencyPenalty(CC_LLM_FREQ_PENALTY)
        except NameError as e:
            pass
            #print_server_log(f"Using default LLM frequency_penalty","configure_model_params()",
            #                MODULE_LLM_DEBUG)
            #print_server_log(f"Caught exception","configure_model_params()",MODULE_LLM_DEBUG)
            #print_server_log(f"{e}","configure_model_params()",MODULE_LLM_DEBUG)
    
    return chat_context
#
#
#   Making a request is about modifying the growing chat_context
#   setting up the HTTP request URL and request headers, and making
#   the request.
def make_chat_request(chat_context=None, chat_key=""):
    #   If there is no chat context, raise an error
    if not chat_context:
        print_server_log(f"No chat_context was supplied","make_chat_request()",
                        MODULE_LLM_DEBUG)
        raise Exception("No chat_context has been supplied")
    
    chat_api = Chat()
    chat_api.setBearerToken(chat_key)
    #
    #   Set configuration values
    chat_context = configure_model_params(chat_context)
    #    
    chat_api.setRequestPayload(chat_context.json(clean=True))
    chat_api.queueRequest()
    chat_api.makeRequest()
    response = chat_api.nextResponse()
    resp_dict = response.json()
    
    #   There is a lot in the response - just extract the message
    assistant_turn = ChatMessage()
    message = resp_dict['choices'][0]['message']
    assistant_turn.setRole("assistant")
    assistant_turn.setMessage(message)
    
    return assistant_turn
#
#   Generate a string of KEY:value items for each org
#   Keys should correspond to the keys defined in the
#   ROOT_CONTEXT_PROMPT
#
#   This prototype adds the synop key and inserts that
#   value when creating the prompt data string.
def create_org_info_str(org_list=[]):
    org_info_str = ""
    for org in org_list:
        data = f"\tORGANIZATION NAME: {org['title']}\n"
        data = data + f"\tDESCRIPTION: {org['synop']}\n"
        if not org_info_str:
            org_info_str = data
        else:
            org_info_str = org_info_str + "\n" + data
    return org_info_str
#
#
#
def new_user_turn(user_text=""):
    user_turn = ChatMessage()
    user_turn.setRole("user")
    user_turn.setContent(user_text)
    return user_turn
#
#
#
def restore_chat_context(session_state=None):
    chat_context = ChatRequestPayload()
    chat_turns = session_state['chat_turns'][session_state['active_branch']]
    for turn in chat_turns:
        chat_message = ChatMessage()
        chat_message.setMessage(turn)
        chat_context.addMessage(chat_message)
    return chat_context
#
#
#
def create_ephem_qna_str(session=None):
    #
    #   Construct the question and answer string, based on what we have from the user
    qna_str = str()
    for i in range(1,5):
        if session['ephem_status'][str(i)]['response']:
            print_server_log(f"Have Q&A pair {i}",
                            "create_ephem_qna_str()",
                            MODULE_LLM_DEBUG)
            qna_str = qna_str + f"QUESTION:\n\t{session['ephem_status'][str(i)]['prompt']}\n"
            qna_str = qna_str + f"ANSWER:\n\t{session['ephem_status'][str(i)]['response']}\n"
    qna_str = qna_str+"\n"
    return qna_str
#
#
#   If session data is provided, then it produces a prompt that includes
#   the data from the prior questions.
#
def qna_question_request(session=None, qna_str="", chat_key=""):
    #   Must have a qna_str to make the request
    if not qna_str:
        print_server_log(f"Missing Q&A string!",
                        "qna_question_request()",
                        MODULE_LLM_DEBUG)
        raise Exception(f"Missing Q&A string!")

    if not session or not session['ephem_status']:
        print_server_log(f"Missing session!",
                         "qna_question_request()",
                         MODULE_LLM_DEBUG)
        raise Exception(f"Missing session!")

    if session['ephem_status']['state'] == 2:
        question_prompt = EPHEM_QUESTION_2_PROMPT;
        print_server_log(f"Asking question 2",
                         "qna_question_request()",
                         MODULE_LLM_DEBUG)
    elif session['ephem_status']['state'] == 3:
        question_prompt = EPHEM_QUESTION_3_PROMPT;
        print_server_log(f"Asking question 3",
                         "qna_question_request()",
                         MODULE_LLM_DEBUG)
    else:
        question_prompt = EPHEM_QUESTION_PROMPT_GENERIC;
        print_server_log(f"Unexpected state: {session['ephem_status']['state']}",
                         "qna_question_request()",
                         MODULE_LLM_DEBUG)
    #
    #   Pass in a string of the conversation so far to help the LLM think about a good question
    sprompt = EPHEM_QUESTION_SYSTEM_PROMPT.format(ephem_qna_pairs=qna_str)

    chat_context = ChatRequestPayload()
    
    system_turn = ChatMessage()
    system_turn.setRole("system")
    system_turn.setContent(sprompt)    
    chat_context.addMessage(system_turn)

    user_turn = ChatMessage()
    user_turn.setRole("user")
    user_turn.setContent(question_prompt)
    chat_context.addMessage(user_turn)
    
    chat_api = Chat()
    chat_api.setBearerToken(chat_key)
    #
    #   Set configuration values
    chat_context = configure_model_params(chat_context)
    #    
    chat_api.setRequestPayload(chat_context.json(clean=True))
    chat_api.queueRequest()
    chat_api.makeRequest()

    if chat_api.last_error:
        print_server_log(f"Error: {chat_api.last_error}",
                        "qna_question_request()",
                        MODULE_LLM_DEBUG)

    response = chat_api.nextResponse()
    resp_dict = response.json()
    
    #   There is a lot in the response - just extract the message
    assistant_turn = ChatMessage()
    message = resp_dict['choices'][0]['message']
    assistant_turn.setRole("assistant")
    assistant_turn.setMessage(message)
    
    return assistant_turn



def make_ephem_rec_request(session=None, chat_key="", local_only=False):
    #
    #   Construct a description string from what we know about user's interests, skills, and location
    #   (interview questions are included in case e.g. the user's response to "Which of these actions
    #   appeals to you?" is "Option 3")
    qna_str = create_ephem_qna_str(session)

    #   Create the prompt based on the user's location preference
    if local_only:
        local_condition = LOCAL_CONDITION_MUST_BE_LOCAL
    else:
        local_condition = LOCAL_CONDITION_ANYWHERE

    sprompt = EPHEM_RECOMMENDATION_PROMPT.format(ephem_qna_pairs = qna_str, local_condition = local_condition)

    #   Now, create the chat that we need to make the request
    chat_context = ChatRequestPayload()

    system_turn = ChatMessage()
    system_turn.setRole("system")
    system_turn.setContent(sprompt)
    chat_context.addMessage(system_turn)

    print_server_log(f"Recommendation prompt:\n{sprompt}",
                    "make_ephem_rec_request()",
                    MODULE_LLM_DEBUG)

    user_turn = ChatMessage()
    user_turn.setRole("user")
    user_turn.setContent(EPHEM_RECOMMENDATION_QUESTION)
    chat_context.addMessage(user_turn)

    print_server_log(f"Creating API requester",
                    "make_ephem_rec_request()",
                    MODULE_LLM_DEBUG)
    chat_api = Chat()
    chat_api.setBearerToken(chat_key)
    #
    #   Set configuration values
    chat_context = configure_model_params(chat_context)
    #
    chat_api.setRequestPayload(chat_context.json(clean=True))
    chat_api.queueRequest()
    chat_api.makeRequest()

    if chat_api.last_error:
        print_server_log(f"Error: " + chat_api.last_error,
                         "make_ephem_rec_request()",
                         MODULE_LLM_DEBUG)

    response = chat_api.nextResponse()
    resp_dict = response.json()

    #   There is a lot in the response - just extract the message
    message = resp_dict['choices'][0]['message']['content']
    session['rec-response'] = message
    print_server_log(f"Response: {message}",
                    "make_ephem_rec_request()",
                    MODULE_LLM_DEBUG)

    #   Parse the organization names out of the response and put them on the page
    session['highlights'] = list()
    column = 1
    start_index = message.find("<ORG>")
    org_info = parse_tag_contents(message, "<ORG>")
    website_checker = CheckWebsite()
    while (org_info != "" and column <= 6):
        poster_item = CC_HIGHLIGHT_TEMPLATE.copy()
        poster_item['column'] = str(column)
        poster_item['title'] = parse_tag_contents(org_info, "<NAME>")
        poster_item['synop'] = parse_tag_contents(org_info, "<DESCRIPTION>")
        poster_item['url'] = parse_tag_contents(org_info, "<URL>")
        poster_item['linktext'] = CC_ORGANIZATION_LINK_TEXT
        poster_item['rating'] = parse_tag_contents(org_info, "<MATCH>")
        poster_item['rationale'] = parse_tag_contents(org_info, "<RATIONALE>")

        #   Check whether the website is real
        website_check_result = website_checker.check_website(poster_item['url'], poster_item['title'])
        if website_check_result == CC_WEBSITE_VERIFICATION_RESULT_NO_PAGE:
            poster_item['warning'] = CC_WARNING_TEXT_NO_PAGE
            poster_item['linktext'] = CC_WARNING_LINK_TEXT_NO_PAGE
            title_for_search = poster_item['title'].replace(' ', '+')
            poster_item['url'] = CC_WARNING_SEARCH_URL_PREFIX + title_for_search
        elif website_check_result == CC_WEBSITE_VERIFICATION_RESULT_TITLE_MISMATCH:
            poster_item['warning'] = CC_WARNING_TEXT_TITLE_MISMATCH
            poster_item['linktext'] = CC_WARNING_LINK_TEXT_TITLE_MISMATCH

        session['highlights'].append(poster_item)
        column += 1
        start_index = message.find("<ORG>", start_index + 5)
        org_info = parse_tag_contents(message, "<ORG>", start_index)

    return session


