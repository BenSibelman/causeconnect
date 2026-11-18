#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: recommender_0.1.py
#   REVISION: November, 2024
#   CREATION DATE: October, 2024
#   Authors: David W. McDonald, Ben Sibelman
#
#   First cut launcher
#
#{{RELEASE}}
#
#{{COPYRIGHT_NOTICE}}
#
##
#
import os, sys, time, datetime, webbrowser
#
from causeconnect.rebert.classes.utilities.Args import Args
from web.config import *
#
#
SERVER_PROTOCOL = "http://"
#SERVER_PROTOCOL = "https://"
SERVER_LOCALHOST = "127.0.0.1"
SERVER_PORT = 5000
SERVER_SETUP_DELAY = 5.0
SERVER_APP = "web/wsgi"
MOCKUP_APP = "web/mockup"
#
#   The python webbrowser module knows only a certain set of browsers. This is a few
#   of the ones that it knows - and which are quite popular. Check the documentation
#   before adding other browser keys. In many cases the browser needs to be running
#   before the webbrowser module can open the web page.
#
BROWSER_NAMES = ['chrome', 'chromium', 'epiphany', 'firefox', 'konqueror', 
                 'mozilla', 'opera', 'safari', 'default']
BROWSER_DEFAULT = "default"
#
#
#   A template, dictionary, that describes the command line parameters that
#   this program will accept.
PARAMS_TEMPLATE = {
    "-browser" : {
            "required"  : False,        # whether or not this flag is required
            "type"      : str,          # the value type, used for potential conversion
            "notes"     : "<the browser to launch>",     # a note related to the flag
            "default"   : BROWSER_DEFAULT,  # use this browser
            "options"   : BROWSER_NAMES # the set, list of browsers that python knows
        },
    "-delay" : {
            "required"  : False,        # whether or not this flag is required
            "type"      : float,        # the value type, used for potential conversion
            "notes"     : "<delay before browser launch>",     # a note related to the flag
            "default"   : SERVER_SETUP_DELAY,          
            "range"     : [1.0, 180.0]  # range of delay values
        },
    "-port" : {
            "required"  : False,        # whether or not this flag is required
            "type"      : int,          # the value type, used for potential conversion
            "notes"     : "<server port>", # a note related to the flag
            "default"   : SERVER_PORT   # the default port
        },
    "-app" : {
            "required"  : False, 
            "type"      : str, 
            "notes"     : "<application to be run in the server>", 
            "default"   : SERVER_APP    # launch this default app
        },
    "-help" : {
            "required"  : False, 
            "type"      : bool, 
            "notes"     : "<print help message>", 
            "default"   : False         # don't ask for help by default
        },
    "-h" : {
            "required"  : False, 
            "type"      : bool, 
            "notes"     : "<print help message>", 
            "default"   : False          # don't ask for help by default
        }
    }
#
#
#   Use the python webbrowser module to get that browser application, launch it.
#   The module doesn't always launch the browser. This often works better if
#   you already have the web browser running on your machine
#
def select_browser(browser_name=""):
    browser = None
    if browser_name=='default':
        # the 'default' should get the default browser
        browser = webbrowser.get()
    elif browser_name in BROWSER_NAMES:
        browser = webbrowser.get(browser_name)
    else:
        # not recognized, then get the default browser
        browser = webbrowser.get()
    return browser
#
#
def main():
    #   Parse the command line params
    p = Args(template=PARAMS_TEMPLATE)
    p.parse(sys.argv)
    #
    #   If the help flag is on the command line show help and exit
    if p['help'] or p['h']:
        p.usage(sys.argv)
        return
    #
    launch_command = f"flask --app {p['app']} run --port {p['port']}"
    #
    #   Launch the server, either with the mockup or the full app
    server_output_pipe = os.popen(launch_command)
    #
    #   Try to launch a browser, with the server's URL
    try:
        time.sleep(p['delay'])
        server_url = SERVER_PROTOCOL+SERVER_LOCALHOST+":"+str(p['port'])
        browser = select_browser(p['browser'])
        browser.open(server_url,new=1)
    except Exception as e:
        print(str(e))
        print(f"Was not able to launch the '{p['browser']}' browser.")
    #
    #   Now, start printing the output of the server to the terminal window
    print(server_output_pipe.read())
    return


if __name__ == '__main__':
    main()   

