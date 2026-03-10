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
from novel_gpt_exports import SaveGPTExports
import numpy as np
from matplotlib import pyplot as plt
import NarrativeKinematics_ADTHS_patched as NK
import pandas as pd

from pathlib import Path

import warnings
warnings.filterwarnings("ignore")

import build_pdfs

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
# Canonical project folders used by the export pipeline.
DATA_DIR = PROJECT_ROOT / "data"
BUILD_DIR = PROJECT_ROOT / "build"


def _project_path(path_like: str | Path) -> Path:
    """Resolve a relative project path (supports '/foo' and 'foo')."""
    p = Path(path_like)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / str(path_like).lstrip("/\\")


def _write_json(path: Path, obj, indent: int | None = None, ensure_ascii: bool = True) -> None:
    """Write JSON with parent-directory creation in one call."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(js.dumps(obj, ensure_ascii=ensure_ascii, indent=indent))

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

def QueryPath(relpath=None, extension=None) -> str | None:
    '''! Search for file path. If path string is a file, validate.
         If it is a directory, check existence and return latest file.
         If neither arguments are specified, return latest file from same ROOT
         directory this program is in.
         @param relpath    String describing relative file/directory location
                           to ROOT. Defaults to ROOT.
         @param extension  The file extension. Defaults to any latest file.'''
    ext = '*' if extension is None else str(extension).strip('.').lower()
    base = _project_path(relpath) if relpath else PROJECT_ROOT

    if base.is_file():
        debug.append('Queried path is to a FILE.','INFO',pri=2)
        return str(base).replace("\\", "/")

    if not base.is_dir():
        debug.append('Issue with relpath. Using ROOT directory.','WARN',pri=2)
        base = PROJECT_ROOT
    else:
        debug.append('Queried path is to a DIRECTORY.','INFO',pri=2)

    if ext == '*':
        candidates = [p for p in base.iterdir() if p.is_file()]
    else:
        candidates = [p for p in base.iterdir() if p.is_file() and p.suffix.lower() == f'.{ext}']

    if not candidates:
        debug.append('No files exist in directory.','ERROR',pri=2)
        return None

    latest = max(candidates, key=lambda p: p.stat().st_ctime)
    latest_shortname = f"~/{latest.parent.name}/{latest.name}"
    debug.append(f'Most recent file retrieved at {latest_shortname}','INFO',pri=2)
    return str(latest).replace("\\", "/")

def ReadJSON(path=None):
    '''! Interpret a JSON file, if encoded correctly.'''
    # Clarify the file path.
    filepath = QueryPath(path,'JSON')
    # If no file path, do not proceed and return empty dictionary.
    if filepath is None:
        debug.append('Unable to retrieve JSON file.','ERROR')
        return {}
    # Open and read the file.
    print(f"Actions taken on filename {filepath}.")
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
        pass
        # print(CS) #todo
        
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
                #print(STORY[ThisChapter-1])
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
            ChapterData['NK_Params'] = []   # Narrative Kinematics parameters for later
            ChapterData['Written'] = False
            ChapterData['Settings'] = [];
            DefaultStorySetting = entry['SettingInfo'];
            ChapterData['WCs'] = []
        if entry['DocType'] == 'Scene':
            ChapterData['Story'] = entry['StoryName']
            ChapterData['History'] = {"Created":entry['CreatedDate'],"Modified":entry['ModifiedDate']}
            ChapterData['Act'] = int(entry['ActNum'])
            ChapterData['ActName'] = ThisActName
            ChapterData['NK_Params'].append([])
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
            ChapterData['Written'] = ChapterData['Written'] or (len(entry['Body']) > 10)
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
            
            PubDateLog += f"\n\t\t> SCENE 0{ChapterData['Scenes']} - {ChapterData['WCs'][-1]} WORDS - { 'Written' if ChapterData['Written'] else 'Not Written'} - SETTING: {ChapterData['Settings'][-1]['Area']}, {ChapterData['Settings'][-1]['Region']} - {ChapterData['Settings'][-1]['Location']}" #" \n {ChapterData['Settings'][-1]}"
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
        WrittenChaps = (WrittenChaps + 1) if entry > 1800 else WrittenChaps
    for entry in WordCounts['Scene']:
        WrittenScenes = (WrittenScenes + 1) if entry > 150 else WrittenScenes
    WritChapNum = np.linspace(1,WrittenChaps,WrittenChaps)
    WritSceneNum =  np.linspace(1,WrittenScenes,WrittenScenes)
    slopeC = (WritChapNum.dot(WordCounts["SumChap"][0:WrittenChaps])) / (WritChapNum.dot(WritChapNum))
    slopeS = (WritSceneNum.dot(WordCounts["SumScene"][0:WrittenScenes])) / (WritSceneNum.dot(WritSceneNum))
    infostring = f" > WC/Scene: {int(slopeS*1000)}\n > WC/Chap:  {int(slopeC*1000)}\n > Scenes: {WrittenScenes} of {int(SceneNum[-1])} ({np.round(WrittenScenes/SceneNum[-1]*100,1)}%)\n > Chaps:  {WrittenChaps+1} of {int(ChapNum[-1])}  ({np.round(WrittenChaps/ChapNum[-1]*100,1)}%)\n > Estimated {int(slopeC*ChapNum[-1])}k by Ch {int(ChapNum[-1])}."
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

def AppendStoryData(MANUSCRIPT, verbose=True): # @todo
    STORY = MANUSCRIPT['Story']         
    META = MANUSCRIPT['Metadata']
    storyname = STORY[1]["Story"]
    path_meta = Path("../..") / "data" / "storymeta" / f"Meta_{storyname}.xlsx"
    newdat = pd.read_excel(
        path_meta.resolve(),
        sheet_name  = "index"
    )
    newdat = newdat.dropna(subset=["ID"])
    nk_dict = newdat.set_index('ID').to_dict(orient="index")
    if verbose: print(f" [INFO] AppendStoryData  > Appending dataset from {path_meta} for {storyname}.");
    if verbose: print(f" [INFO] AppendStoryData  > There are {len(nk_dict)} entries.")
    for chindex, entry in STORY.items():
        relative_id = f"{entry['Act']}.{entry['Chapter']}"
        scenenum = 0;
        for nk_entry in entry['NK_Params']:
            scenenum += 1
            scene_id = f"{relative_id}.{scenenum}"
            try:
                STORY[chindex]['NK_Params'][scenenum-1] = nk_dict[scene_id]    
            except:
                if verbose: print(f" [WARN] AppendStoryData  > {scene_id} not in dataset.");
            finally:
                if verbose: print(js.dumps(STORY[chindex]['NK_Params'][scenenum-1],indent=3))    
    return MANUSCRIPT

def MakeDirIfNotExists(path):
    '''! Handle creating/selecting directories.'''
    target = _project_path(path)
    if not target.is_dir():
        debug.append('Output folder did not exist. Created new folder.','WARN',pri=2)
        target.mkdir(parents=True, exist_ok=True)
    else:
        debug.append('Output folder exists.','INFO',pri=2)

def SaveMasterCopy(manuscriptDict,indentLevel=None):
    '''! Save the full, reformatted JSON content.
    @param manuscript  Manuscript dictionary for full export.
    @param indentLevel  The prettyprint indent level for export.'''
    storyDict = manuscriptDict['Story']
    story_name = str(storyDict[0]['Story'])

    # Keep both a timestamped snapshot and a latest rolling file.
    now = datetime.now().strftime("%Y%m%d_%H%M")
    out_dir = DATA_DIR / "output" / story_name
    _write_json(out_dir / f"MC_{now}.json", manuscriptDict, indent=indentLevel, ensure_ascii=True)
    _write_json(out_dir / "MC_Latest.json", manuscriptDict, indent=indentLevel, ensure_ascii=True)
    
def SaveSectionedCopy(storyDict,indentLevel=None):
    '''! Separate into JSON files separated by chapter in directories labeled
         by act.
         @param storyDict  Story dictionary (meta stuff doesn't matter here)
         @param indentLevel  The prettyprint indent level for export.'''
    acts = []
    chapters = []
    actchap = {}

    story_name = str(storyDict[0]['Story'])
    base_dir = DATA_DIR / "sectioned" / story_name
    base_dir.mkdir(parents=True, exist_ok=True)

    # Build an act -> chapter list from written chapters.
    for entry in storyDict.values():
        if entry['Act'] not in acts:
            acts.append(entry['Act'])
            actchap[entry['Act']] = []
        if entry['Chapter'] not in chapters and entry['Written'] is True:
            chapters.append(entry['Chapter'])
            actchap[entry['Act']].append(entry['Chapter'])

    print(chapters)
    # Render one standalone HTML file per chapter for downstream PDF conversion.
    for act, chapterlist in actchap.items():
        act_dir = base_dir / str(act)
        act_dir.mkdir(parents=True, exist_ok=True)
        for chapter in chapterlist:
            _write_json(act_dir / f"{chapter}.json", storyDict[chapter-1]['Body'], indent=indentLevel, ensure_ascii=True)

def SaveBasicCopy(storyDict, indentLevel=None):
    acts = []
    chapters = []
    actchap = []
    MakeDirIfNotExists('/data/GPT')
    for entry in storyDict.values():
        if entry['Act'] not in acts:
            acts.append(entry['Act'])
        if entry['Chapter'] not in chapters and entry['Written'] is True:
            chapters.append(entry['Chapter'])
            actchap.append({})
            Perspectives = entry["POV"]
            actchap[-1]["Scenes"] = []
            actchap[-1]["SceneLocation"] = []
            actchap[-1]["Chapter"] = entry['Chapter']
            actchap[-1]["Act"] = entry['Act']
            actchap[-1]["Chapter Name"] = entry['ChapterName']
            scenenum = 0
            for scene in entry['Body']:
                scenenum += 1
                actchap[-1]["Scenes"].append({"Perspective": Perspectives[scenenum-1], "Text": [""]})
                actchap[-1]["SceneLocation"].append(entry['Settings'])
                for line in scene:
                    actchap[-1]["Scenes"][-1]["Text"][-1] += line[1]
                    if line[2] is True:
                        actchap[-1]["Scenes"][-1]["Text"].append("")

    gpt_path = DATA_DIR / "GPT" / f"{storyDict[0]['Story']}_GPT.json"
    _write_json(gpt_path, actchap, indent=indentLevel, ensure_ascii=True)
    print(" > Created GPT copy.")

    with gpt_path.open("r", encoding="utf-8") as f:
        obj = js.load(f)

    out = GPT_Parse(obj, source_name="Paragate_GPT.json")
    _write_json(DATA_DIR / "GPT" / f"{storyDict[0]['Story']}_GPT_index.json", out, indent=2, ensure_ascii=False)
    return
    
def SaveHTMLforPDF(manuscriptDict):
    MakeDirIfNotExists('/build/pdf')
    
    acts = []
    chapters = []
    actchap = {}
    
    demoHTMLbody = '<html><head><style>' + build_pdfs._DEFAULT_PRINT_CSS + '</style></head>'
    storyname = manuscriptDict[1]["Story"]
    MakeDirIfNotExists(f'/build/pdf/{storyname}')
    for entry in manuscriptDict.values():
        if entry['Act'] not in acts:
            acts.append(entry['Act'])
            actchap[entry['Act']] = []
        if entry['Chapter'] not in chapters and entry['Written'] is True:
            chapters.append(entry['Chapter'])
            actchap[entry['Act']].append(entry['Chapter'])
    # Render one standalone HTML file per chapter for downstream PDF conversion.
    for act, chapterlist in actchap.items():
        for chapter in chapterlist:
            numname = GetNumberName(chapter)
            charname = manuscriptDict[chapter-1]['POV'][0]
            # Build a quick scene anchor rail for intra-chapter jumps.
            idstring = "•"
            scnum = 0
            for idname in manuscriptDict[chapter-1]['IDs']:
                scnum += 1;
                idstring += "&ensp;<a href='#" + str(idname) + "'>" + str(act) + "." + str(chapter) + "." + str(scnum) + "</a>&ensp;•";
            idstring += " "
            HTMLbody = f'''
<div class="StoryHeader">
<img class="Namesake" src="../../design/Paragate_logo_inv.png" alt="Story Header">
<img class="AuthorName" src="../../design/sgname_inv.png" alt="by SavantGuarde">
</div>

<div class="Header{storyname}">
<h1 class="PDF_CTitle Title{charname}"> Chapter {numname} </h1>
<p style="font-size:20px;margin:0;line-spacing:0.5em;transform:translateY(-10%);font-weight:800;"> {idstring} </p>
<h2 class="PDF_CSub Sub{charname}"> {manuscriptDict[chapter-1]['ChapterName']} </h2>
</div>
'''
            # Order:    [1] CLASS  
            #           [2] LINE TEXT 
            #           [3] isEOL (end of <p>)
            #           [4] do PB instead of </p> if isEOL
            #           [5] Raw HTML?
            thisScene = 0;
            wasEOL = True;
            wasItalic = False;
            for scene in manuscriptDict[chapter-1]['Body']:      
                thisScene += 1;
                charname = manuscriptDict[chapter-1]['POV'][thisScene-1]
                HTMLbody += f'''
                <div class="Scene{manuscriptDict[chapter-1]['POV'][thisScene-1]}">
                <h3 class="PDF_Snum" id={manuscriptDict[chapter-1]['IDs'][thisScene-1]}> <span class="PDF_Snum">&hairsp;0&hairsp;&hairsp;{thisScene}&hairsp;</span> </h3>
                <h4 class="Sname{charname}"><img style="height:60px;filter:invert(1);" src="../../icons/logo-{charname}.png">&ensp;<span style="border-top: 1px solid black;border-bottom: 1px solid black;position:absolute;transform:translateY(72%) translateX(10px);font-size:16px;text-transform: uppercase;letter-spacing: 0.1em;">&ensp;{charname}&ensp;</span></h4>'''
                # Reconstruct paragraph/italic flow from tokenized line metadata.
                for lineclass, line, isEOL, doPB, isRawHTML in scene:
                    if lineclass == "EndOfScene":
                        HTMLbody += "</div>"
                    else:
                        # Handle if was end of line first.
                        if wasEOL:
                            HTMLbody += f'<p class="{lineclass}">'   
                            wasEOL = False
                        # Handle text.
                        isItalic = (lineclass == 'Internal' or lineclass == 'Emphasis')                                   
                        # If newly italic
                        if not wasItalic and isItalic:
                            wasItalic = True
                            HTMLbody += '<em>'
                        # If currently italic
                        if wasItalic and isItalic:
                            pass
                        # If no longer italic
                        if (wasItalic and not isItalic) or (isItalic and isEOL):
                            wasItalic = False
                            HTMLbody += '</em>'
                        HTMLbody += f'{line}'
                        # Handle if is end of line last.
                        if isEOL:
                            wasEOL = True           
                            isEOL = False
                            if doPB:
                                HTMLbody += '<br>\n'
                            else:
                                HTMLbody += '</p>\n'
                            
                        
            if chapter == 1:   
                demoHTMLbody += HTMLbody + "</body></html>"
                #print(HTMLbody)
            with open(str(PROJECT_ROOT) + f"/build/pdf/{storyname}/{chapter}.html", "w") as f:
                f.write(HTMLbody)   
    with open(str(PROJECT_ROOT) + f"/build/pdf/{storyname}/_DEMO.html", "w") as f:
        f.write(demoHTMLbody)   
        
def SavePDF(storyname):
    """
    Runs after SaveHTMLforPDF(...). Converts ./build/pdf/<storyname>/*.html -> ./build/pdf/<storyname>/_PDF/*.pdf
    """
    pdf_root = Path(str(PROJECT_ROOT)) / "build" / "pdf"
    if not pdf_root.exists():
        raise FileNotFoundError(f"PDF root folder not found: {pdf_root}")

    # Pick the most recently modified story folder under ./build/pdf/
    story_dirs = [p for p in pdf_root.iterdir() if p.is_dir()]
    if not story_dirs:
        raise FileNotFoundError(f"No story folders found under: {pdf_root}")

    story_dir = max(story_dirs, key=lambda p: p.stat().st_mtime)
    out_dir = story_dir / "_PDF"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Optional: if you have a real print stylesheet, drop it here and it will be used.
    # Otherwise the generator uses a sane default.
    css_candidate_1 = story_dir / "print.css"
    css_candidate_2 = Path(str(PROJECT_ROOT)) / "print.css"
    css_path = None
    if css_candidate_1.exists():
        css_path = css_candidate_1
    elif css_candidate_2.exists():
        css_path = css_candidate_2

    written = build_pdfs.build_pdfs_from_html_dir(
        html_dir=story_dir,
        out_dir=out_dir,
        paper="Letter",
        css_path=css_path,
        include_page_numbers=True,
        header_information=f"{storyname} by Savant-Guarde"
    )

    print(f" > Wrote {len(written)} PDFs to {out_dir}")

def SaveTableOfContents(manuscriptDict,indentLevel=None):
    '''! Generate a Table Of Contents file that will guide other programs
         in navigating the file structure.
         @param storyDict  Story dictionary (meta stuff doesn't matter here)
         @param indentLevel  The prettyprint indent level for export.'''
    MakeDirIfNotExists('/data/TOC')
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
            "Location"      : f"/data/sectioned/{entry['Story']}/{entry['Act']}/{entry['Chapter']}.json"
            }
        TOCdict['ChapterList'].append(ChapterEntry)

    # TOC always points to sectioned chapter payloads for the web reader.
    _write_json(DATA_DIR / "TOC" / f"TOC_{manuscriptDict['Story'][0]['Story']}.json", TOCdict, indent=indentLevel, ensure_ascii=True)


# Standalone execution of this file.
    
if __name__ == "__main__":
    # End-to-end export pipeline: parse source -> build artifacts -> optional NK diagnosis

    debug = DebugLog(1)
    JS = ReadJSON('/data/source')
    MANUSCRIPT = InterpretJSON(JS,True)
    MANUSCRIPT = AppendStoryData(MANUSCRIPT)   
    
    SaveMasterCopy(MANUSCRIPT,indentLevel=3)
    print(" >>> Saving Master Copy.")
    SaveSectionedCopy(MANUSCRIPT['Story'] ,indentLevel=3)
    print(" >>> Saving Sectioned Copy.")
    SaveTableOfContents(MANUSCRIPT, indentLevel=3)
    print(" >>> Saving Table Of Contents.")
    SaveBasicCopy(MANUSCRIPT['Story'], indentLevel=3)
    print(" >>> Saving Basic Copy.")
    SaveGPTExports(MANUSCRIPT, JS, indentLevel=3)
    print(" >>> Saving GPT-optimized JSON files.")
    MakeDirIfNotExists("/build/nk_output")
    storyname = MANUSCRIPT['Story'][0]['Story']
    print(" >>> Interpreting Narrative Kinematic data for Action, Drama, Theme.")
    nk = NK.StoryNK(
        Manuscript=MANUSCRIPT['Story'],
        doReport=False,
        story_name          = storyname,
        outdir              = str(PROJECT_ROOT / "build" / "nk_output"),
        factor_mode         = "last",          # or "mean"
        steady_window=9,
        mass_window=7,
        prominence_window=5,
        gravity_weights=(0.35, 0.35, 0.30),
        cut_risk_weights=None,
        compression_weights=(0.22, 0.23, 0.22, 0.23, 0.10),
        indispensability_weights=(0.32, 0.20, 0.30, 0.18),
        # moe versus ero
        connotative_weights=(0.85, 0.15),
        total_energy_weights=(0.60, 0.40),
        coupling=0.60,
        conversion_window=9,
        peak_annotate_count=10,
        field_distribution_bins=14,
    )    
    print(" >>> Proceeding to save PDFs.")
    SaveHTMLforPDF(MANUSCRIPT['Story'])    
    print(" >>> Organized HTML.")
    SavePDF(str(MANUSCRIPT['Story'][1]["Story"]).replace("Paragate","Knightfall & Daybreak"))
    print(" >>> Saved companion PDFs.")      
    
    #model = "gpt-5-mini" #"gpt-5.4"
    Mlow = "gpt-5-mini";
    Mhigh = "gpt-5.4";
    api_key = os.environ.get("OPENAI_API_KEY")
    common_instruction = """
    This manuscript is currently in its first / generative revision.
    The intended process is:
    1) generative revision,
    2) narrative revision, where the largest structural and conceptual changes occur,
    3) final polishing revision.
    
    Analyze the manuscript accordingly. Do not mistake first-draft roughness for conceptual failure.
    Prioritize identifying:
    - what the story is trying to be,
    - where it is already working,
    - where it is structurally weak,
    - what is compressible,
    - what is indispensable,
    - and what kinds of revision would most improve the next draft.
    
    Use the Narrative Kinematics framework in a practical way, not as empty math decoration.
    Interpret the fields as follows:
    - Action = external motion, resistance, danger, pace, consequential change
    - Drama = emotional pressure, vulnerability, relational consequence, irreversibility, centrality
    - Theme = premise pressure and convergence, not philosophical prestige or whether the premise is “good”
    - Heart = attachment, yearning, belonging, habitat desire, emotional habitation, “I want to stay here”
    - Sensuality = bodily / erotic / somatic charge
    - Magnitude = signed premise alignment from anti-truth to truth
    
    When judging weak regions, distinguish between:
    - Compression Opportunity
    - Structural Indispensability
    
    Do not assume that low-action or lower-theme scenes are disposable if they are carrying real Heart, relationship capital, atmosphere, or later payoff setup.
    Likewise, do not excuse structurally inert material merely because it is pleasant.
    
    Treat the report as a revision instrument.
    Be concrete, but avoid fake precision.
    Prefer identifying:
    - what should be trimmed,
    - what should be merged,
    - what should be escalated,
    - what should be protected,
    - and what must later convert into payoff.
    """
    
    extra_instruction = {
        "Paragate":
            common_instruction + """
    Paragate is a dual-protagonist “double novel” built on mirrored and reflective scene structures between Cody and Katiya.
    Be sensitive to drag caused by repeated equal-and-opposite beats, especially where mirrored design does not produce enough escalation, contrast, or payoff.
    However, do not over-penalize slower relationship or habitation material if it is carrying substantial Heart, chemistry, attachment, or mutual-world fascination.
    
    The central premise pressure is not merely the portal gimmick.
    The real premise concerns:
    - mutual escape versus chosen commitment,
    - courage versus avoidance,
    - owning one’s own world and circumstances,
    - and love that does not erase separate obligations or collapse two lives into one refuge.
    
    The worlds must remain separate in the final meaning of the story.
    Do not treat the portal as the ultimate solution.
    When evaluating Magnitude, negative values should generally correspond to avoidance, mutual escape, or evasion of responsibility; positive values should generally correspond to courage, responsibility, chosen commitment, and ownership of one’s own life.
    
    When diagnosing weak sections, pay special attention to:
    - whether Heart is carrying scenes that are structurally quieter,
    - whether mirrored beats are truly progressive rather than repetitive,
    - whether relationship capital is later converted into denotative payoff,
    - and whether the story’s identity arrives too late or is already latent in earlier material.
    
    The final Titus bonus chapter is a short promotional add-on and should be treated separately from the main structural diagnosis of Paragate.
    """,
    
        "Firebrand":
            common_instruction + """
    Firebrand was written before the second novel and has not yet been released.
    The chapters from 'Rolling Downhill' onward are unfinished and are expected to be rewritten with a stronger ending.
    Do not over-commit to the exact surface structure of the unfinished ending corridor; diagnose its function, failure mode, and intended payoff more than its current line-level execution.
    
    The core premise pressure of Firebrand concerns:
    - the temptation to rewrite reality indefinitely,
    - perfection versus acceptance,
    - control versus limitation,
    - the burden of trying to save everyone,
    - and learning what 'enough' means in a finite life.
    
    When evaluating Magnitude, negative values should generally correspond to perfectionism, refusal of limitation, compulsive revision of reality, or anti-truth control; positive values should generally correspond to acceptance, chosen finite love, responsibility inside limitation, and enoughness.
    
    Be especially attentive to:
    - whether Theme is inflated merely because the story is premise-rich,
    - whether Drama is genuinely earned rather than constantly maxed,
    - whether the time-revision mechanics deepen the story or merely intensify it,
    - and whether the ending corridor cashes the premise instead of only escalating pain.
    
    Because this manuscript has many scenes with high thematic and emotional charge, be disciplined about identifying which peaks are truly indispensable and which are redundant intensifications of the same beat.
    """,
    
        "Goldenfur":
            common_instruction + """
    Goldenfur is in a very preliminary state.
    Treat the analysis as early-stage developmental diagnosis rather than fine-grained revision judgment.
    Focus on:
    - identifying the emerging premise,
    - spotting what kind of story it wants to become,
    - locating promising structural and emotional anchors,
    - and distinguishing underdeveloped potential from actual failure.
    
    At this stage, protect conceptual possibilities and avoid overfitting rigid conclusions to provisional material.
    """
    }
        
    report_style_instruction = """
    Write the report in a practical developmental-editor voice.
    Be direct, specific, and useful.
    Do not flatter the manuscript. Be fair, and praise what is unique or might warrant it, but do not confuse promise with execution.
    
    Priorities:
    - diagnose what is working,
    - diagnose what is weak,
    - explain why,
    - and propose what kind of revision would help.
    
    Do not write as though the metrics are infallible.
    Use the Narrative Kinematics outputs as evidence, not as a substitute for judgment.
    
    When making claims:
    - distinguish between structural weakness, connotative strength, and true deadness,
    - distinguish compression opportunity from structural dispensability,
    - distinguish repeated intensity from real escalation,
    - and distinguish premise pressure from premise prestige.
    
    Prefer language like:
    - "this section appears to..."
    - "this chapter is likely carrying..."
    - "the corridor seems to under-convert..."
    - "this beat may be compressible if..."
    rather than pretending to possess absolute certainty.
    
    Do not overuse theoretical jargon.
    Translate the metrics into plain narrative meaning.
    
    The report should generally answer:
    1) Where does the story truly come alive?
    2) Where does it drag, and why?
    3) What is carrying the weaker sections, if anything?
    4) What appears compressible?
    5) What appears indispensable?
    6) What setup is not yet converting into payoff?
    7) What should the next revision prioritize?
    
    When discussing peaks:
    - explain what makes them peaks,
    - whether they are structurally earned,
    - and whether they are denotative, connotative, or both.
    
    When discussing weak sections:
    - do not call them bad just because they are quiet,
    - only criticize quietness when it is unproductive,
    - and do not excuse inertness merely because a section is pleasant.
    
    When discussing Heart and Sensuality:
    - do not moralize,
    - do not become snide,
    - and do not reduce emotional or erotic appeal to contempt.
    Treat connotative yield as real narrative function, even when it is not literary prestige.
    
    Avoid fake line-edit precision unless the source resolution truly supports it.
    If the data is chapter-level, do not pretend to know exact sentence-level surgery.
    
    The report should be organized around revision usefulness, not just description.
    Prefer:
    - strongest regions,
    - weakest regions,
    - conversion failures,
    - compression candidates,
    - indispensable material,
    - and revision priorities.
    
    End with a short actionable summary of what the next draft should do.
    """
    
    # Narrative Kinematics report
    print(" >>> Exporting Narrative Kinematics report and data.")
    answer = input(" >>? Run LLM diagnosis?\n    [0] No Report\n    [1] No Assessment\n    [2] Low (GPT-5 mini)\n    [3] High (GPT-5.4)\n\n  > ")
    [justExit, doDiagnose, model] = [False,True,Mlow] if answer == "2" else [False,True,Mhigh] if answer == "3" else [False,False,Mlow] if answer == "1" else [True,False,Mlow]
    print(f"Diagnosis is {doDiagnose}.")
    if not justExit:
        if doDiagnose and not api_key:
            print(" !!! WARNING: No API key detected.")
        else:
            print(f"using API key {api_key[0:20]}...")
            paths = nk.export_html_report_bundle(
                str(PROJECT_ROOT / "build" / "nk_output"),
                include_llm_diagnosis=doDiagnose,
                extra_instruction=extra_instruction[storyname] + "\n\n" + report_style_instruction,
                model=model    
            )
            
            print(paths["pdf_report"])
            print(paths.get("diagnosis_json"))
