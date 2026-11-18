#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: setup.py
#   REVISION: May, 2026
#   CREATION DATE: October, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   Code that runs before the Flask web server starts
#
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import sys, os, datetime, hashlib, json, copy

#
#   This comes from the rebert class library and manages API keys
#   You should use it to store your OpenAI API key locally, so your
#   key is not stored as a constant in the code.
from causeconnect_ai.rebert.classes.data.KeyManager import KeyManager

from causeconnect_ai._causeconnect_1_0_.web.config import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.utilities import *    # MODIFIED

MODULE_SETUP_DEBUG = False

if not MODULE_DEBUG_OVERRIDE:
    MODULE_SETUP_DEBUG = GLOBAL_DEBUG

##############
#
#   SERVER SETUP
#
##############

def initalize_server_state():
    server_state = CC_SERVER_STATE_TEMPLATE.copy()
    #   Create a key manager object - it automatically loads
    #   the available key information - if you added a key    
    key_manager = KeyManager()
    #
    #   Returns a list of keys - should only be one
    key_list = key_manager.findRecord(domain="api.openai.com")
    #
    #   Extract just the api key from the key record
    server_state['OPENAI_KEY'] = key_list[0]['key']
    #
    return server_state
