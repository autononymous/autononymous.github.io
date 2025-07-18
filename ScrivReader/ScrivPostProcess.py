import json as js
import os
from datetime import datetime, timedelta

import_path = "story/";
export_path = "story/process/"


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

def ScrPostProcess(filename):    
    with open(import_path + str(filename), 'r', encoding='utf-8') as file:
        content = file.read().replace('\n','');
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
                "Act":JS[i]["ActNum"],
                "ChapterNumber": JS[i]["ChapterFull"],
                "Synopsis":JS[i]["Synopsis"],
                "RevNotes":"",
                "ID":JS[i]["VerboseID"],
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
                "Act":JS[i]["ActNum"],
                "ChapterNumber": JS[i]["ChapterFull"],
                "Synopsis":JS[i]["Synopsis"],
                "ID":JS[i]["VerboseID"],
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