#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: utilities.py
#   REVISION: June, 2026
#   CREATION DATE: October, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   A set of utility functions to support the CauseConnect AI web app
#
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import sys, os, datetime, hashlib, json

#   Used when reading variables from user data fields
from markupsafe import escape

from causeconnect._causeconnect_0_1_.web.config import *    # MODIFIED



MODULE_UTILITIES_DEBUG = False

if not MODULE_DEBUG_OVERRIDE:
    MODULE_UTILITIES_DEBUG = GLOBAL_DEBUG


##############
#
#   UTILITIES
#
##############
#
#   We will want a session tracker so that we can keep track of sessions with
#   individuals. It would be best to store this in a DB but we're going to use
#   a set of flat files for the prototypes
#
def generate_session_id(request=None):
    #   HTTP request headers are not provided in a parsed form, they are not a JSON thing
    #   We have to extract key:values manually
    agent = "No.User-Agent"
    try:
        #
        #   Check that we have some kind of string
        headers_str = str(request.headers)
        ua_pos = headers_str.find('User-Agent:')
        if ua_pos >= 0:
            ua_end = headers_str.find('\n',(ua_pos+1))
            ua_pos = ua_pos + len('User-Agent:')
            agent = headers_str[ua_pos:ua_end]
            agent = agent.strip()
            #sys.stderr.write(f"[{ua_pos}:{ua_end}] = {agent}\n")
    except Exception as e:
        #print_server_log(f"Caught exception","generate_session_id()",MODULE_UTILITIES_DEBUG)
        #print_server_log(f"{e}","generate_session_id()",MODULE_UTILITIES_DEBUG)
        agent = "No.User-Agent"
    #
    ts = str(datetime.datetime.now())
    #
    #   create a string of the User-Agent and the current time
    #   make that string a set of 'bytes'
    id_gen = bytes(agent+"++/++"+ts,'utf-8')
    #
    #   With the Blake2 algorithm create a hash that is 'short'
    h = hashlib.blake2s(digest_size=8)
    h.update(id_gen)
    #   Use the text of that short string as a session ID
    new_session_id = "ses_"+str(h.hexdigest())
    print_server_log(f"Generated session id: {new_session_id}",
                    "generate_session_id()",
                    MODULE_UTILITIES_DEBUG)
    return new_session_id


def extract_main_page_form_data(request=None):
    ui_state = CC_MAINPAGE_UI_STATE_TEMPLATE.copy()
    try:
        ui_state['session_id'] = escape(request.form["session_id"])
        ui_state['cc_text'] = escape(request.form["ask_output"])
        ui_state['user_question'] = escape(request.form["question_text"])
        ui_state['synopsis_state'] = request.form["synopsis_state"]
        ui_state['discuss_state'] = request.form["discuss_state"]
        ui_state['ephem_q_state'] = request.form["ephem_q_state"]
        ui_state['ephem_s_state'] = request.form["ephem_s_state"]
        ui_state['ephem_answer'] = escape(request.form["ephem_answer"])
    except Exception as e:
        #   An exception here is really, really, bad - always output this exception
        keys_str = str(list(request.form.keys()))
        print_server_log(f"Caught an exception when reading form variables:",
                        "extract_main_page_form_data()")
        print_server_log(f"Request form includes the following variables:\n\t{keys_str}",
                        "extract_main_page_form_data()")
        print_server_log(f"{e}","extract_main_page_form_data()")
        raise

    #   Make sure we have a list here, we've had occasional crashes where a None value ended up in the UI
    ui_state['discuss_content'] = list()
    return ui_state



def load_session_state(session_id=None):
    if not session_id: return None
    session_state = None
    state_filename = CC_SESS_FILE_TEMPLATE.format(session_id=session_id)
    state_file_path = os.path.join(CC_TEMP_FILE_DIRECTORY,state_filename)
    if os.path.isfile(state_file_path):
        try:
            session_file = open(state_file_path,"r")
            session_state = json.load(session_file)
            session_file.close()
        except Exception as e:
            print_server_log(f"Caught exception","load_session_state()")
            print_server_log(f"{e}","load_session_state()")
            print_server_log(f"Returning 'None' for session_state","load_session_state()")
            session_state = None
            session_file = None
    return session_state
#
#
#   We need this class to serialize the chat message turns in the session state
from causeconnect.rebert.classes.data.DictionaryValidatorFromTemplate import DVFTJSONEncoder

def save_session_state(session_info=None):
    if not session_info: 
        print_server_log(f"NO session_info to save",
                        "save_session_state()",
                        MODULE_UTILITIES_DEBUG)
        return
    session_id = session_info['session_id']
    state_filename = CC_SESS_FILE_TEMPLATE.format(session_id=session_id)
    state_file_path = os.path.join(CC_TEMP_FILE_DIRECTORY,state_filename)
    try:
        print_server_log(f"Saving: {state_file_path}",
                        "save_session_state()",
                        MODULE_UTILITIES_DEBUG)
        session_file = open(state_file_path,"w")
        json.dump(session_info,session_file, cls=DVFTJSONEncoder)
        session_file.close()
    except Exception as e:
        print_server_log(f"Caught exception","save_session_state()")
        print_server_log(f"{e}","save_session_state()")
        session_file = None
    return


def print_server_log(text="", proc="", emit=True):
    if emit:
        if proc:
            sys.stderr.write(f"{CC_VERS_STR}@{proc}: {text}\n")
        else:
            sys.stderr.write(f"{CC_VERS_STR}: {text}\n")
    return


def parse_tag_contents(source, tag_name, start_index = 0):
    end_tag = "</" + tag_name[1:]
    tag_start = source.find(tag_name, start_index)
    if (tag_start < 0):
        return ""
    content_start = tag_start + len(tag_name)
    content_end = source.find(end_tag, content_start)
    if (content_end < 0):
        return ""
    return source[content_start:content_end]


