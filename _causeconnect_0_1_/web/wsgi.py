#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: wsgi.py
#   REVISION: June, 2026
#   CREATION DATE: June, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   Rebert server web page dispatch. This maps the incoming URLs to specific functions
#   in the code base.
#
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import sys, os

from flask import Flask, request
#
#
from causeconnect_ai._causeconnect_1_0_.web.config import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.setup import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.serve_main_page import *    # MODIFIED
from causeconnect_ai._causeconnect_1_0_.web.serve_ephem_rec import *    # MODIFIED
#
#   Required set up before any serving actions
app = Flask(__name__)
#   This also seems to work
#app = Flask("causeconnect_ai._causeconnect_1_0_.web.wsgi")    # MODIFIED
#
global SERVER_STATE
SERVER_STATE = initalize_server_state()
#
#
MODULE_WSGI_DEBUG = True
#
if not MODULE_DEBUG_OVERRIDE:
    MODULE_WSGI_DEBUG = GLOBAL_DEBUG
#
#
#
##############
#
#   HOME PAGE GENERATION
#
##############
@app.route("/", methods=['GET', 'POST'])
def home_page():
    #   comes from serve_main_page.py
    page = serve_home_page(request, SERVER_STATE)
    return page


##############
#
#   ASK REBERT PAGE GENERATION
#
##############
#
@app.route("/ask_causeconnect", methods=['POST'])
def ask_causeconnect():
    #   comes from serve_main_page.py
    page = serve_ask_causeconnect_response(request, SERVER_STATE)
    return page


##############
#
#   EPHEMERAL RECOMMENDATION GENERATION
#
##############
#
@app.route("/next_question", methods=['POST'])
def ephem_next_question():
    #   comes from serve_ephem_rec.py
    page = serve_next_ephem_question(request, SERVER_STATE)
    return page
#
#
@app.route("/ephem_recommend", methods=['POST'])
def ephem_recommendation():
    #   comes from serve_ephem_rec.py
    page = serve_ephem_recommendation(request, SERVER_STATE, False)
    return page
#
#
@app.route("/ephem_recommend_local", methods=['POST'])
def ephem_recommendation_local():
    #   comes from serve_ephem_rec.py
    page = serve_ephem_recommendation(request, SERVER_STATE, True)
    return page
