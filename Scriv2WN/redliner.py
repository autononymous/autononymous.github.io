# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 12:02:05 2026

@author: rkiss
"""

import json as js
from datetime import datetime as dt
import os, sys, glob, time, csv
import copy

def timestamp(): 
    return dt.now().isoformat();



def ReadJSON(path=None):
    '''! Interpret a JSON file, if encoded correctly.'''
    
    # Clarify the file path.
    filepath = path
    
    # If no file path, do not proceed and return empty dictionary.
    if filepath is None:
        print('Unable to retrieve JSON file.','ERROR')
        return {}
    # Open and read the file.
    print(f"Actions taken on filename {filepath}.")
    with open(filepath, 'r', encoding='utf-8', errors="ignore") as file:
        try:
            content = file.read().replace('\n','');  
        # If there is an issue with encoding.
        except UnicodeDecodeError as e: 
            print(f'Unable to read file in {e.encoding} at position {e.start}','ERROR')
        # Try loading it as as JSON file.
        try:
            loaded = js.loads(content)
        # If there's an error, preview where it is.
        except ValueError as e:
            ERRline = e.lineno
            ERRcol = e.colno            
            err_str = "> Error in compilation of the JSON file.\n Exception occured at LINE " + str(ERRline) + ", COL " + str(ERRcol) + ".\nError occured aroundhere:\n\n"
            err_str += content[ERRcol-50:ERRcol-5] + "    --->" + content[ERRcol-4:ERRcol+4] + " <---    " + content[ERRcol+5:ERRcol+50]
            print(err_str,'INFO')  
            raise Exception()
        print('JSON file successfully loaded.','INFO')  
        return loaded

REDLINE_TEMPLATE = {
    "Title":"",
    "Description":"",
    "Created":"",
    "Scope":
    {
            "Act":-1,
            "Chapter":-1,
            "Scene":-1,
            "Type":-1,          
    },
    "Difficulty":0,
    "Importance":0
}
    

argorder = ["Full","Act","Chapter","Scene"]

arg = "null",
story = "null"
TOCdata = []
TOCparsed = {}
MENU = True
while MENU:
    try:
        arg = input("Select story to add redlines:\n\n  [1] Firebrand\n  [2] Paragate\n\n > ")
        story = ["Firebrand","Paragate"][int(arg)-1]
        print(f"Selected story is {story}.")     
        MENU = False
    except:
        if arg == "q" or arg == "Q":
            MENU = False
            print("Exiting program.")
            break
        print(f"Invalid input for story: {arg}")
        
url = os.getcwd() + '\\TOC\\' + f"TOC_{story}.json"
TOCdata = ReadJSON(url)
Existing = []
chlist = ""
for entry in TOCdata["ChapterList"]:
    if f"{entry['Act']}" not in Existing: 
        Existing.append(f"{entry['Act']}");
        TOCparsed[f"{entry['Act']}"] = "Full act of the story."
    Existing.append(f"{entry['Act']}.{entry['Chapter']}")
    TOCparsed[f"{entry['Act']}.{entry['Chapter']}"] = f"{entry['ChapterName']} : {entry['Blurb']}"
    scindex = 0;
    for scenes in entry["Settings"]:
        Existing.append(f"{entry['Act']}.{entry['Chapter']}.{scindex}")
        TOCparsed[f"{entry['Act']}.{entry['Chapter']}.{scindex}"] = f"{entry['ChapterName']} : {entry['Blurb']}"
        scindex += 1;
    blength = 60
    blurb = entry['Blurb'] if len(entry['Blurb']) < blength else entry['Blurb'][0:blength] + "..."
    chlist += f"\n {entry['Act']}.{entry['Chapter']}\t{entry['ChapterName']}\n\t\t  > Summary: {blurb}\n\t\t  > Scenes: {scindex}\n"
    
print(chlist)
while arg != "q" and arg != "Q":
    newRedline = copy.deepcopy(REDLINE_TEMPLATE);    
    # Prompt ID
    MENU = True
    while MENU and arg != "q" and arg != "Q":
        arg = input(f"Enter scope of redline for {story}. \n  X.X.X for scene \n  X.X for full chapter \n  X for full act \n  0 for full story \n > ")
        try:
            argparse = arg.split(".")
            scopenum = 0;
            scopes = newRedline["Scope"]
            scopes["ID"] = arg
            if arg == "0":
                scopes["isFull"] = True
            else:
                for argentry in argparse:
                    scopenum += 1;
                    scopes[argorder[scopenum]] = int(argentry)
            scopes["Type"] = scopenum     
            if arg in Existing:
                print(f"Exists in Table Of Contents list: this is a(n) {['full story redline','act redline','chapter redline','scene redline'][int(scopes['Type'])]}.")
                print(f"{TOCparsed[arg]}")
                MENU = False
            else:
                print("Entry does not exist in Table of Contents.")
           
        except:
            print("Invalid entry.")
        
    newRedline["Created"] = timestamp()
    MENU = True
    while MENU and arg != "q" and arg != "Q":
        arg = input("Enter a title/quick summary for this redline.\n > ")
        newRedline["Title"] = arg
        arg = input("Enter a description of this redline.\n > ")
        newRedline["Description"] = arg
        arg = input("Difficulty of redline? \n [1 ~ 10] > ")
        try:
            newRedline["Difficulty"] = 10 if int(arg) > 10 else 1 if int(arg) < 1 else int(arg)
        except:
            newRedline["Difficulty"] = 1
        arg = input("Criticality of redline? \n [1 ~ 10] > ")
        try:
            newRedline["Importance"] = 10 if int(arg) > 10 else 1 if int(arg) < 1 else int(arg)
        except:
            newRedline["Importance"] = 1
        MENU = False
        print(f"New redline '{newRedline['Title']}' for {story} scope {newRedline['Scope']['ID']} created.\n\n")
        print(newRedline)
        time.sleep(2)
    
        