# -*- coding: utf-8 -*-
"""
Created on Sat Dec  6 17:03:54 2025

@author Ryan Kissinger

@brief Processes a compiled, Scrivener-exported JSON file into files for a
       webnovel deployment environment in Javascript.
"""

import json as js
import os, sys, glob, time, csv
from datetime import datetime, timedelta
from paragate_gpt_parse import GPT_Parse
import numpy as np
from matplotlib import pyplot as plt

OnesNames = ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen","Twenty"]
TensNames = ["err","err","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]

class DebugLog:
    '''! A class that handles debug messages, and stores them until deployment
         is requested.'''
    def flush(self):
        '''! Retrieve all currently stored messages.'''
        for parcel in self.log:
            infotype = (f'[{parcel[0]}]') if parcel[0] != '' else ''
            source = (f'in {parcel[1]}') if parcel[1] != '' else ''
            message = parcel[2]            
            print(f" {infotype} {source}: {message}")
        self.log = []
    def append(self, message, infotype='', source='', pri=0, flush=True):
        '''! Add a string to the sequential debug message ticker.
             @param message  A string to deploy in the console.
             @param infotype  e.g. ERROR, WARN, INFO
             @param source  Function/class of origin.
             @param pri     Priority of this message.
             @param flush   Whether or not to print message immediately.
             '''
        if pri <= self.priorityLevel:
            self.log.append([infotype,source,str(message)])
            if flush is True:
                self.flush()    
    def __init__(self, priority=0):
        '''! Initializing function of DebugLog.
             @param priorit  Messages at or below this level will be read.'''
        self.priorityLevel = priority
        self.log = []    
        
def GetNumberName(number,spacechar='-'):
    '''! Interpret an integer into a word name.
         @param number  Integer to turn into a word number.
         @param spacechar  Separator to use between tens and ones.'''
    number = int(number)
    # Values not to accept ( @TODO add 100+ but shouldn't be necessary )
    if number > 99 or number < 1:
        debug.append(f'Number value "{number}" not accepted in GetNumberName.','INFO',pri=2)
    # Everything below 20 is unique. No TensName.
    if number < 21:
        OnesName = OnesNames[int(number)]
        TensName = ""
    else:
        # Making sure the number doesn't read "thirty-zero" or something
        if int(number) % 10 == 0:
            OnesName = ""
        else:
            OnesName = spacechar + OnesNames[int(number) % 10]
        TensName = TensNames[int((int(number) - int(number) % 10)/10)]
    return f"{TensName}{OnesName}"

def QueryPath(relpath=None,extension=None) -> None:
    '''! Search for file path. If path string is a file, validate.
         If it is a directory, check existence and return latest file.
         If neither arguments are specified, return latest file from same ROOT 
         directory this program is in.
         @param relpath    String describing relative file/directory location
                           to ROOT. Defaults to ROOT.
         @param extension  The file extension. Defaults to any latest file.'''
    # Get the root directory location this .py file is in.
    root = str(os.getcwd())
    extension = '*' if extension is None else extension
    # Is this a path to a file?
    if os.path.isfile(root + relpath):
        debug.append('Queried path is to a FILE.','INFO',pri=2)
        fullpath = root + relpath
    # Is this a path to a directory?
    elif os.path.isdir(root + relpath):
        debug.append('Queried path is to a DIRECTORY.','INFO',pri=2)       
        basepath = root + relpath
    # If not either, just use base directory.
    else:
        debug.append('Issue with relpath. Using ROOT directory.','WARN',pri=2)
        basepath = root
    # Proceed to evaluate directory.
    list_of_files = glob.glob(basepath + f'/*.{extension}')
    # Are there files in this directory of the type?
    if len(list_of_files) < 1:
        debug.append('No files exist in directory.','ERROR',pri=2)
        return None
    fullpath = max(list_of_files, key=os.path.getctime).replace("\\","/")
    latest_shortname = "~/" + fullpath.split('/')[-2] + "/" + fullpath.split('/')[-1]
    debug.append(f'Most recent file retrieved at {latest_shortname}','INFO',pri=2)        
    return fullpath

def ReadJSON(path=None):
    '''! Interpret a JSON file, if encoded correctly.'''
    # Clarify the file path.
    filepath = QueryPath(path,'JSON')
    # If no file path, do not proceed and return empty dictionary.
    if filepath is None:
        debug.append('Unable to retrieve JSON file.','ERROR')
        return {}
    # Open and read the file.
    with open(filepath, 'r', encoding='utf-8', errors="ignore") as file:
        try:
            content = file.read().replace('\n','');  
        # If there is an issue with encoding.
        except UnicodeDecodeError as e: 
            debug.append(f'Unable to read file in {e.encoding} at position {e.start}','ERROR')
        # Try loading it as as JSON file.
        try:
            loaded = js.loads(content)
        # If there's an error, preview where it is.
        except ValueError as e:
            ERRline = e.lineno
            ERRcol = e.colno            
            err_str = "> Error in compilation of the JSON file.\n Exception occured at LINE " + str(ERRline) + ", COL " + str(ERRcol) + ".\nError occured aroundhere:\n\n"
            err_str += content[ERRcol-50:ERRcol-5] + "    --->" + content[ERRcol-4:ERRcol+4] + " <---    " + content[ERRcol+5:ERRcol+50]
            debug.append(err_str,'INFO')  
            raise Exception()
        debug.append('JSON file successfully loaded.','INFO',pri=1)  
        return loaded
    
# [Scrivener Style Name] => [Javascript Style Name]
StringTypeDict = {
    "BlockQuote"    : "Block",
    "Body"          : "Body",
    "BodyCody"      : "BodyCody",
    "BodyJade"      : "BodyJade",
    "BodyKatiya"    : "BodyKatiya",
    "BodyTitus"     : "BodyTitus",
    "Comment"       : "Comment",
    "Heading1"      : "Heading1",
    "Heading2"      : "Heading2",
    "NoteCody"      : "NoteCody",
    "NoteKatiya"    : "NoteKatiya",
    "NoteJade"      : "NoteJade",
    "NoteTitus"     : "NoteTitus",
    "MessageFrom"   : "MessageFrom",
    "MessageTo"     : "MessageTo",
    "MessageFromDate":"Timestamp", # deprecated
    "MessageToDate" : "Timestamp", # deprecated
    "em"            : "Emphasis",
    "Internal"      : "Internal",
    "MessageTimestamp":"Timestamp",
    "RawHTML"       : "RawHTML"
    }    
# If an orphaned type, default to this section's body style.
PerspectiveDefaults = {
    "Cody"          : "BodyCody",
    "Katiya"        : "BodyKatiya",
    "Jade"          : "BodyJade",
    "Mixed"         : "Body",
    "Titus"         : "BodyTitus",
    "Default"       : "Body"
    }

def getLineMetadata(Sentence,Perspective="Default"):
    '''! Given a line in a passage, return formatted ticker entries.
         @param Sentence  Full uninterpreted text string.
         @param Perspective  This sentence's scene perspective POV.
         @return newlines  Array of arrays containing feed lines.'''
    # init newlines to append to later depending on symbols.
    newlines = []
    # Disregard empty sentences.
    if Sentence == "":
        return None
    # Split sentence character styles (e.g. italics, internal monologue)
    fragments = Sentence.replace('%%','%/%').split('%/%')
    n_frags = len(fragments)
    # Default needs to be different if this is a message line.
    DefaultClass = PerspectiveDefaults[Perspective]
    for i in range(n_frags):
        # Find prefix and suffix containing style name identifier
        prefix = fragments[i].find("{[")
        suffix = fragments[i].find("]}")
        # Both must exist to read identifier and body text, respectively
        if (prefix != -1) and (suffix != -1) and (suffix > prefix):
            try:
                lineclass = StringTypeDict[fragments[i][prefix+2:suffix]]
            except:
                print(f"ERROR parsing line style {fragments[i][prefix+2:suffix]}. Defaulting to {DefaultClass}.")
                lineclass = DefaultClass
            line = fragments[i][suffix+2:len(Sentence)]
            # Set default to a MessageType if this is a MESSAGE LINE.
            if (lineclass == "MessageFrom" or lineclass == "MessageTo"):
                #print(line)
                DefaultClass = lineclass
        # Otherwise, read the fragment as just a line.
        else:
            lineclass = None
            line = fragments[i]
        # Identifier with no line is not appended: disregard.
        if len(line) > 0:
            newlines.append([lineclass,line,False,False,False]) 
            # Order:    [1] CLASS  
            #           [2] LINE TEXT 
            #           [3] isEOL (end of <p>)
            #           [4] do PB instead of </p> if isEOL
            #           [5] Raw HTML?
            # Note: EOL set FALSE but last entry set TRUE later.
    for newline in newlines:
        # Orphaned text without identifier gets section default body style.
        if newline[0] is None:
            newline[0] = DefaultClass
        # Is this raw HTML code?
        if newline[0] == "RawHTML":
            newline[4] = True
    # Set last entry in the sentence as the End Of Line (EOL)
    newlines[-1][2] = True
    # Return newlines as array [[style,text,isEndOfLine],[...]]
    return newlines
    
def InterpretJSON(js,info=True):
    '''! Turn the JSON raw file into something we can interpret a lot easier.
         @param js  The JSON object containing the story.
         @param info  Display info on the story every time this is run.'''
    # Create a new dictionary to sort the story into.
    MANUSCRIPT = {'Story' : {}, 'Metadata' : {}}
    STORY = MANUSCRIPT['Story']         
    META = MANUSCRIPT['Metadata']
    CS = '\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n'
    ActCount = ChapterCount = SceneCount = WrittenCount = UnwrittenCount = 0
    WordCount = int(js['WordCount'].replace(',',''))
    for entry in js['Manuscript']:
        ActCount += entry['DocType'] == 'Act'
        ChapterCount += entry['DocType'] == 'Chapter'
        if entry['DocType'] == 'Scene':
            SceneCount += 1
            if len(entry['Body']) > 10:
                WrittenCount += 1
            else:
                UnwrittenCount += 1                
    CS+= f'     SUMMARY FOR STORY "{js["Manuscript"][2]["StoryName"]}" by {js["Author"]}:\n'
    CS+= '=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n'
    CS+=f" > Word count is {js['WordCount']}.\n"
    CS+=f" > There are {ActCount} acts, {ChapterCount} chapters, and {SceneCount} scenes.\n"
    CS+= " > This manuscript averages:\n"
    CS+=f"   - {int(WordCount/SceneCount)} words per scene.\n"        
    CS+=f"   - {int(WordCount/ChapterCount)} words per chapter.\n"     
    CS+=f"   - {int(SceneCount/ChapterCount*100)/100} scenes per chapter.\n"
    CS+=f" > Out of {SceneCount} planned scenes, {WrittenCount} are written.\n"
    CS+=f" > So the Zero Draft is approximately {int(WrittenCount/SceneCount*1000)/10}% complete.\n"    
    META['ActCount'] = ActCount
    META['ChapterCount'] = ChapterCount
    META['SceneCount'] = SceneCount
    META['WrittenCount'] = WrittenCount
    META['UnwrittenCount'] = UnwrittenCount
    META['Summary'] = CS  
    if info:  
        print(CS)
        
    # Now, we interpret the dictionary created from the JSON file.
    ThisChapter = -1
    ThisChapterName = ''
    ThisAct = 0;
    ThisActName = ''
    doWarnPOV = False; ############################################################## CHECKING POV DATA.
    noPOVwarnings = True;
    PubDate = ""
    WordCounts = {"Scene":[],"Chapter":[],"SumScene":[],"SumChap":[],"SumSceneWrit":[],"SumChapWrit":[]}
    PubDateLog = f"Publication dates of {MANUSCRIPT['Story']} are computed as follows:\n"
    for entry in js['Manuscript']:
        if entry['DocType'] == "Act":
            ThisAct += 1;
            ThisActName = entry['DocName']
        # The data we pull here from the CHAPTER will be supplanted into
        # each following chapter.
        if entry['DocType'] == 'Chapter':
            ThisChapter += 1
            ThisChapterName = entry['GivenName']
            STORY[ThisChapter] = {'Name':ThisChapterName}
            # Friendly name for what we will be modifying.
            ChapterData = STORY[ThisChapter]
            ChapterData['ChapterName'] = entry['GivenName']
            ChapterData['Completion'] = entry['PercentComplete']
            ChapterData['Summary'] = entry['Summary']
            ChapterData['Blurb'] = entry['Synopsis']
            # Pubilshing information.  
            try:
                PubDate = (datetime.strptime(entry['PublishOn'], '%m/%d/%y').date()) if (entry['PublishOn'] != "") else PubDate + timedelta(days=int(entry['NextPublish']))
            except:
                PubDate = datetime.now()
            ChapterData['NextPublish'] = PubDate.strftime('%m/%d/%y')
            if (ThisChapter > 1):
                print(STORY[ThisChapter-1])
                if ('WCs' in STORY[ThisChapter-1].keys() ):
                    PubDateLog += f"\n\t> TOTAL WORD COUNT = {sum(STORY[ThisChapter-1]['WCs'])}"
                    WordCounts["Chapter"].append(sum(STORY[ThisChapter-1]['WCs']))
                    WordCounts["SumChap"].append(sum(WordCounts["Chapter"])*.001)
                    if STORY[ThisChapter-1]['WCs'] != 0: 
                        WordCounts["SumChapWrit"].append(sum(WordCounts["Scene"])*.001)
                        
            PubDateLog +=  f"\n{ChapterData['NextPublish']}\t|\t{ThisAct}.{ThisChapter+1}\t|\t {ChapterData['ChapterName']}\n\t> {entry['Synopsis'][0:200]} ..."
            ChapterData['Scenes'] = 0
            ChapterData['Body'] = []
            ChapterData['POV'] = []        
            ChapterData['IDs'] = []
            ChapterData['Settings'] = [];
            DefaultStorySetting = entry['SettingInfo'];
            ChapterData['WCs'] = []
        if entry['DocType'] == 'Scene':
            ChapterData['Story'] = entry['StoryName']
            ChapterData['History'] = {"Created":entry['CreatedDate'],"Modified":entry['ModifiedDate']}
            ChapterData['Act'] = int(entry['ActNum'])
            ChapterData['ActName'] = ThisActName
            ChapterData['Chapter'] = int(entry['ChapterFull'])
            ChapterData['ChapterNumber'] = GetNumberName(int(entry['ChapterFull']))
            ChapterData['Scenes'] += 1
            if (entry['Perspective'] == "Default") and (doWarnPOV):
                noPOVwarnings = False
                errscene = f"{entry['ActNum']}.{entry['ChapterFull']}.{ChapterData['Scenes']}"
                POVinput = ""
                print(f"UNSPECIFIED POV IN SCENE {errscene}")
                POVinput = input(f"What character perspective is in this scene?\n{(entry['Body'])[0:100]} ...\nHit ENTER to stop searching for error.\n > ")
                if POVinput == "":
                    doWarnPOV = False
                else:
                    ChapterData['POV'].append(POVinput)
            else:
                ChapterData['POV'].append(entry['Perspective'])
            ChapterData['IDs'].append(entry['VerboseID'])
            ChapterData['Written'] = len(entry['Body']) > 10
            ChapterData['Body'].append([])
            if entry['SettingInfo']['ISO'] == "":
                ChapterData['Settings'].append(DefaultStorySetting)
            else:
                ChapterData['Settings'].append(entry['SettingInfo'])
            # What if the setting ISO is timeless, and only has a date?
            if ('TZ' in ChapterData['Settings'][-1]['ISO']):
                ChapterData['Settings'][-1]['ISO'] = ChapterData['Settings'][-1]['ISO'].split('TZ')[0]
            ChapterData['WCs'].append(0)
            Sentences = entry["Body"].replace("</>","\n").replace("<>","").split("\n")
            for Sentence in Sentences:
                Fragments = getLineMetadata(Sentence,ChapterData['POV'][-1])
                if Fragments is not None:
                    for Fragment in Fragments:
                        ChapterData['Body'][-1].append(Fragment)
                        ChapterData['WCs'][-1] += len(Fragment[1].split(" "))    
            
            PubDateLog += f"\n\t\t> SCENE 0{ChapterData['Scenes']} - {ChapterData['WCs'][-1]} WORDS - SETTING: {ChapterData['Settings'][-1]['Area']}, {ChapterData['Settings'][-1]['Region']} - {ChapterData['Settings'][-1]['Location']}" #" \n {ChapterData['Settings'][-1]}"
            WordCounts["Scene"].append(ChapterData['WCs'][-1])
            WordCounts["SumScene"].append(sum(WordCounts["Scene"])*.001)
            if ChapterData['WCs'][-1] != 0: 
                WordCounts["SumSceneWrit"].append(sum(WordCounts["Scene"])*.001)
    PubDateLog += f"\n\t> TOTAL WORD COUNT = {sum(STORY[ThisChapter-1]['WCs'])}"
    
    # STATISTICS FOR NERDS
    PubDateLog += f"\n\n --== CHAPTER STATISTICS ==-- \n\n\t > Mean Scene Word Count is {np.round(np.mean(WordCounts['Scene']),1)}. \n\t > Mean Chapter Word Count is {np.round(np.mean(WordCounts['Chapter']),1)}."
    WordCt = WordCounts['SumChap']
    SceneCt = WordCounts['SumScene']
    ChapNum = np.linspace(1,len(WordCt),len(WordCt))
    SceneNum = np.linspace(1,len(SceneCt),len(SceneCt))
    WrittenChaps = 0
    WrittenScenes = 0
    for entry in WordCounts['Chapter']:
        WrittenChaps = (WrittenChaps + 1) if entry != 0 else WrittenChaps
    for entry in WordCounts['Scene']:
        WrittenScenes = (WrittenScenes + 1) if entry != 0 else WrittenScenes
    WritChapNum = np.linspace(1,WrittenChaps,WrittenChaps)
    WritSceneNum =  np.linspace(1,WrittenScenes,WrittenScenes)
    slopeC = (WritChapNum.dot(WordCounts["SumChap"][0:WrittenChaps])) / (WritChapNum.dot(WritChapNum))
    slopeS = (WritSceneNum.dot(WordCounts["SumScene"][0:WrittenScenes])) / (WritSceneNum.dot(WritSceneNum))
    infostring = f" > WC/Scene: {int(slopeS*1000)}\n > WC/Chap:  {int(slopeC*1000)}\n > Scenes: {WrittenScenes} of {int(SceneNum[-1])} ({np.round(WrittenScenes/SceneNum[-1]*100,1)}%)\n > Chaps:  {WrittenChaps} of {int(ChapNum[-1])}  ({np.round(WrittenChaps/ChapNum[-1]*100,1)}%)\n > Estimated {int(slopeC*ChapNum[-1])}k by Ch {int(ChapNum[-1])}."
    plt.plot(ChapNum,WordCt)
    plt.plot([0,ChapNum[-1]],[0,slopeC*ChapNum[-1]],'--r',linewidth=1)
    t = plt.text(2,0.8*WordCt[-1],infostring)
    t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='gray'))
    plt.title(f"{STORY[0]['Story']} Word Count by Chapter")
    plt.xlabel("Chapter Number")
    plt.ylabel("Word Count [Thousands]")
    plt.grid(True)
    # Some lines require line breaks instead of paragraph tags: the current
    #   example is when a NOTE type is present -- if the next style is also
    #   a NOTE, it should only be a line break instead of a paragraph break,
    #   or else the appearance will be segmented.
    for indexChapter in range(len(STORY)):
        for Scene in STORY[indexChapter]['Body']:
            SceneCount = len(Scene);
            Scene.append(['EndOfScene',' ',True,False,False])
            for indexLine in range(SceneCount):
                NotLastLineOfNote = (Scene[indexLine][0].find('Note') != -1) and (Scene[indexLine+1][0].find('Note') != -1)
                
                if (NotLastLineOfNote ):
                    Scene[indexLine][3] = True;
                    
    if noPOVwarnings: print("No POV errors found in manuscript. Good work.")
    print(f"\n{PubDateLog}\n")
    
    return MANUSCRIPT

def MakeDirIfNotExists(path):
    '''! Handle creating/selecting directories.'''
    if not os.path.isdir(os.getcwd()+path):
        debug.append('Output folder did not exist. Created new folder.','WARN',pri=2)
        os.makedirs(os.getcwd()+path)
    else:
        debug.append('Output folder exists.','INFO',pri=2)

def SaveMasterCopy(manuscriptDict,indentLevel=None):
    '''! Save the full, reformatted JSON content.
    @param manuscript  Manuscript dictionary for full export.
    @param indentLevel  The prettyprint indent level for export.'''
    storyDict = manuscriptDict['Story']
    # Let's make sure the exporting directory exists.
    for path in ['/output',f"/output/{storyDict[0]['Story']}"]:
        MakeDirIfNotExists(path)
    # Get timestamp
    now = datetime.now().strftime("%Y%m%d_%H%M")
    with open(os.getcwd() + f"/output/{storyDict[0]['Story']}/" + f"MC_{now}.json", "w") as f:        
        f.write(js.dumps(manuscriptDict,ensure_ascii=True,indent=indentLevel));  
    with open(os.getcwd() + f"/output/{storyDict[0]['Story']}/" + "MC_Latest.json", "w") as f:
        f.write(js.dumps(manuscriptDict,ensure_ascii=True,indent=indentLevel)); 
    
def SaveSectionedCopy(storyDict,indentLevel=None):
    '''! Separate into JSON files separated by chapter in directories labeled
         by act.
         @param storyDict  Story dictionary (meta stuff doesn't matter here)
         @param indentLevel  The prettyprint indent level for export.'''
    acts = []
    chapters = []
    actchap = {}
    # Make missing directories for 'sectioned' and the Story Name directory.
    for path in ['/sectioned',f"/sectioned/{storyDict[0]['Story']}"]:
        MakeDirIfNotExists(path)
    # Gather a tabulated list of acts/chapters to write.
    for entry in storyDict.values():
        if entry['Act'] not in acts:
            acts.append(entry['Act'])
            actchap[entry['Act']] = []
        if entry['Chapter'] not in chapters and entry['Written'] is True:
            chapters.append(entry['Chapter'])
            actchap[entry['Act']].append(entry['Chapter'])
    # Make a folder for each act in the Story Name folder.
    #print(actchap)
    for act, chapterlist in actchap.items():
        actpath = f"/sectioned/{storyDict[0]['Story']}/{act}"
        MakeDirIfNotExists(actpath)
        for chapter in chapterlist:
            with open(os.getcwd() + actpath + f"/{chapter}.json", "w") as f:
                f.write(js.dumps(storyDict[chapter-1]['Body'],ensure_ascii=True,indent=indentLevel))    

def SaveBasicCopy(storyDict, indentLevel=None):
    acts = []
    chapters = []
    actchap = []
    MakeDirIfNotExists('/GPT')
    for entry in storyDict.values():
        if entry['Act'] not in acts:
            acts.append(entry['Act'])
            # actchap[entry['Act']] = {}
        if entry['Chapter'] not in chapters and entry['Written'] is True:
            chapters.append(entry['Chapter'])
            actchap.append({})
            Perspectives = entry["POV"]
            actchap[-1]["Scenes"] = []
            actchap[-1]["SceneLocation"] = []
            actchap[-1]["Chapter"] = entry['Chapter'];
            actchap[-1]["Act"] = entry['Act']
            actchap[-1]["Chapter Name"] = entry['ChapterName']
            scenenum = 0;
            for scene in entry['Body']:  
                scenenum += 1;
                actchap[-1]["Scenes"].append({"Perspective":Perspectives[scenenum-1],"Text":[""]})
                actchap[-1]["SceneLocation"].append(entry['Settings'])
                for line in scene:
                    actchap[-1]["Scenes"][-1]["Text"][-1] += line[1]
                    if line[2] == True:
                        actchap[-1]["Scenes"][-1]["Text"].append("")
                        
                        
    with open(os.getcwd() + f"/GPT/{storyDict[0]['Story']}_GPT.json", "w") as f:
        f.write(js.dumps(actchap,ensure_ascii=True,indent=indentLevel))  
    print(" > Created GPT copy.")
    with open(os.getcwd() + f"/GPT/{storyDict[0]['Story']}_GPT.json", "r", encoding="utf-8") as f:
        obj = js.load(f)
    out = GPT_Parse(obj, source_name="Paragate_GPT.json")
    with open(os.getcwd() +f"/GPT/{storyDict[0]['Story']}_GPT_index.json", "w", encoding="utf-8") as f:
        js.dump(out, f, ensure_ascii=False, indent=2)
    return
    

def SaveTableOfContents(manuscriptDict,indentLevel=None):
    '''! Generate a Table Of Contents file that will guide other programs
         in navigating the file structure.
         @param storyDict  Story dictionary (meta stuff doesn't matter here)
         @param indentLevel  The prettyprint indent level for export.'''
    MakeDirIfNotExists('/TOC')     
    TOCdict = {'Metadata':{},'ChapterList':[]}
    TOCdict['Metadata'] = manuscriptDict['Metadata']
    TOCdict['ChapterList'] = []    
    storyDict = manuscriptDict['Story']
    for entry in storyDict.values():
        ChapterEntry = {
            "Act"           : entry['Act'],
            "ActName"       : entry['ActName'],
            "Chapter"       : entry['Chapter'],
            "ChapterName"   : entry['ChapterName'],
            "ChapterNumber" : entry['ChapterNumber'],
            "Character"     : entry['POV'],
            "Summary"       : entry['Summary'],
            "Blurb"         : entry['Blurb'],
            "Written"       : entry['Written'],
            "Release"       : entry['NextPublish'],
            "Settings"      : entry['Settings'],
            "Location"      : f"/sectioned/{entry['Story']}/{entry['Act']}/{entry['Chapter']}.json"
            }
        TOCdict['ChapterList'].append(ChapterEntry)
    with open(os.getcwd() + '/TOC/' + f"TOC_{manuscriptDict['Story'][0]['Story']}.json", "w") as f:
        f.write(js.dumps(TOCdict,ensure_ascii=True,indent=indentLevel));  

# Standalone execution of this file.
if __name__ == "__main__":        
    debug = DebugLog(1)
    JS = ReadJSON('/source')
    MANUSCRIPT = InterpretJSON(JS,True)
    SaveMasterCopy(MANUSCRIPT,indentLevel=3)
    SaveSectionedCopy(MANUSCRIPT['Story'] ,indentLevel=3)
    SaveTableOfContents(MANUSCRIPT, indentLevel=3)
    SaveBasicCopy(MANUSCRIPT['Story'], indentLevel=3)
    #ProgressReport(MANUSCRIPT)
    
    
    