import json as js
import os
from datetime import datetime, timedelta
import sys
import glob
import time

import_path = "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/ScrivReader/story/";
export_path = "C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/ScrivReader/story/process/"


OnesNames = ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen","Twenty"]
TensNames = ["err","err","Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"]

def PushChapter(data,storyname):
    storypath = export_path + str(storyname) + '/'
    newpath = storypath + str(data['Act']) + '/'
    try:
        os.mkdir(storypath)      
    except FileExistsError:
        pass
    try:        
        os.mkdir(newpath)        
    except FileExistsError:
        pass
    with open(newpath + '/' + str(data['ChapterNumber']) + ".JSON", "w") as f:
        f.write(js.dumps(data));
    
def DateYear(num):
    base_date = datetime(2025, 1, 1)
    target_date = base_date + timedelta(days=int(num))
    return [target_date.strftime("%m"), target_date.strftime("%d"), target_date.strftime("%Y"), str(target_date)]

def MasterTOC(storynames):
    unsorted = [];
    for i in range(len(storynames)):
        with open(export_path + str(storynames[i]) + "/TOC.JSON", 'r', encoding='utf-8') as file:
            content = file.read().replace('\n','');
            loaded = js.loads(content)
            for key, value in loaded.items():
                #print(key, value)
                unsorted.append(value)
    unsorted.sort(key=lambda rls: rls["Release"])
    with open(export_path + "MasterTOC.JSON", "w") as f:
        f.write(js.dumps(unsorted));
            

def ScrPostProcess(filename):    
    # Wait until the file exists before opening
    timeout = 10  # seconds
    waited = 0
    while not os.path.exists(filename) and waited < timeout:
        time.sleep(0.5)
        waited += 0.5
        print(" . ");
    if not os.path.exists(filename):
        print(f'ERROR: File "{filename}" not found after waiting.')
        return
    try:        
        print("> Trying fullname path for " + str(filename) + ".")
        with open(filename, 'r', encoding='ISO-8859-1') as file:
            content = file.read().replace('\n','');
        print('Filename '+str(filename)+' was direct path.')
            
    except Exception as error:  
        try:
            print("> Error was: \n" + str(error) +"\n\n> Trying shorthand path.")
            with open(import_path + str(filename), 'r', encoding='ISO-8859-1') as file:
                content = file.read().replace('\n','');
            print('Filename '+str(filename)+' was shortened path.')
        except Exception as error:
            print('> Unable to resolve path "'+str(filename)+'".\n Error is: ' + str(error) + "\n\n")
            return
    
    loaded = js.loads(content)
    JS = loaded["Manuscript"];
    
    nEntries = len(JS);
    ReleaseYearDay = 0;
    
    ChapDict = {};
    TOCentry = {};
    TOCdict = {};
    StoryName = "";
    
    infoCountChapter = 0;
    infoCountScene = 0;
    
    ThisType = "";
    WasType = "";
    
    for i in range(nEntries):        
        ThisType = JS[i]["DocType"]
        if (ThisType == "Act"):
            if (WasType == "Scene"): # This means Chapter Scene collection is over.
                StoryName = JS[i]["StoryName"]
                PushChapter(ChapDict,StoryName);
                TOCdict.update({JS[i-1]["ChapterFull"]:TOCentry})
            pass
        elif (ThisType == "Chapter"):
            if (WasType == "Scene"): # This means Chapter Scene collection is over.
                StoryName = JS[i]["StoryName"]
                PushChapter(ChapDict,StoryName);
                TOCdict.update({JS[i-1]["ChapterFull"]:TOCentry})
                
            TensName = TensNames[int((int(JS[i]["ChapterFull"])  - int(JS[i]["ChapterFull"]) % 10)/10)]
            OnesName = OnesNames[int(JS[i]["ChapterFull"]) % 10]
            
            IsActive = datetime.strptime(DateYear(ReleaseYearDay)[3],'%Y-%m-%d %H:%M:%S') <= datetime.now()
            ChapterFullName = OnesNames[int(JS[i]["ChapterFull"])] if int(JS[i]["ChapterFull"]) <= 20 else (TensName + "-" + OnesName if OnesName != "Zero" else TensName)
            ReleaseYearDay = (int(JS[i]["NextPublish"]) + ReleaseYearDay) if (JS[i]["PublishOn"] == "") else int(JS[i]["PublishOn"])
            infoCountChapter = JS[i]["ChapterFull"];
            
            ChapDict = {
                "Story":JS[i]["StoryName"],
                "Title":"Chapter " + ChapterFullName,
                "Subtitle":JS[i]["GivenName"],
                "Act":int(JS[i]["ActNum"])-1,
                "ChapterNumber": JS[i]["ChapterFull"],
                "Synopsis":JS[i]["Synopsis"],
                "RevNotes":"",
                "ID":str(int(JS[i]["ActNum"])-1) + "." + str(JS[i]["ChapterFull"]),
                "Body":[],
                "BodyFormatted":[],
                "Release":ReleaseYearDay,
                "ReleaseDate":DateYear(ReleaseYearDay),
                "Active":IsActive,
                "Perspective": JS[i]["Perspective"] if ((JS[i]["Perspective"] != "Mixed") and (JS[i]["Perspective"] != "")) else JS[i-1]["Perspective"],
                "Status":JS[i]["Status"],
                "WordCount":0,
                "Summary" : JS[i]["Summary"]
            }
            TOCentry = {
                "Story":JS[i]["StoryName"],
                "Title":"Chapter " + ChapterFullName,
                "Subtitle":JS[i]["GivenName"],
                "Act":int(JS[i]["ActNum"])-1,                
                "ChapterNumber": JS[i]["ChapterFull"],
                "Synopsis":JS[i]["Synopsis"],
                "ID":str(int(JS[i]["ActNum"])-1) + "." + str(JS[i]["ChapterFull"]),
                "Release":ReleaseYearDay,
                "ReleaseDate":DateYear(ReleaseYearDay),
                "Active":IsActive,
                "Perspective": JS[i]["Perspective"] if ((JS[i]["Perspective"] != "Mixed") and (JS[i]["Perspective"] != "")) else JS[i-1]["Perspective"],
                "Status":JS[i]["Status"],
                "Summary" : JS[i]["Summary"]
            }
            
        elif (ThisType == "Scene"):
            ChapDict["Body"].append(JS[i]["Body"]);
            infoCountScene += 1;
            
        WasType = ThisType;
    PushChapter(ChapDict,StoryName);
    
    with open(export_path + str(StoryName) + "/TOC.JSON", "w") as f:
        f.write(js.dumps(TOCdict));    
    
    print('> Scrivener-exported story "' + str(StoryName) + '" has been post-processed.\n  |\tEntries:\t'+ str(i) + "\n  |\tChapters:\t" + str(infoCountChapter) + "\n  |\tScenes: \t" + str(infoCountScene) + "\n> There are an average of " + str(round(infoCountScene/infoCountChapter,2)) + " scenes per chapter.")
    
    
def GetFolders(arg):
    result = []
    for item in arg:
        if not ("." in item):
            result.append(item)
    return result

def LogProcess(string):
    print(string);
    with open(import_path + "log.txt", "a") as f:
        f.write("\n" + string);  
    
#LogProcess("\n========" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "========\n")

if __name__ == "__main__":
    try:
        arg_FileIn = sys.argv[1]
        try:
            LogProcess("> Running from "+ str(sys.argv[2]) + ".")
        except:
            LogProcess("> Running from undeclared process.")
        LogProcess("FILEIN ARGS:\n" + str(arg_FileIn));
        LogProcess('> Accepted argument "' + arg_FileIn +'".')
        ScrPostProcess(arg_FileIn)
    except:        
        LogProcess('> No arguments presented in command line.')
        list_of_files = glob.glob(import_path+'/*.json')
        latest_file = max(list_of_files, key=os.path.getctime).replace("\\","/")       
        LogProcess("LATESTFILE ARGS:\n" + str(latest_file));
        ScrPostProcess(latest_file) 
     
LogProcess('> Compiling existing files into Master Table Of Contents...');   
StoryFolders = GetFolders(os.listdir('C:/Users/rkiss/OneDrive/Documents/GitHub/autononymous.github.io/ScrivReader/story/process'))
MasterTOC(StoryFolders);

LogProcess("> Completed for "+str(StoryFolders)+".")

