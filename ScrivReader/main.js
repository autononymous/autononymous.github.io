
    DATEKEY = "Tuesday, May 13, 2025"; // Start date from Autononymous release day on March 14, 2025.
    const tSTART = new Date("2025-03-14T00:00:00Z"); 
    const dBEGIN = 56; //Story release relative date.
    const dSTART = yeardate(tSTART);    
    const tNOW = new Date(); // Current date.
    const dNOW = yeardate(tNOW);

    DConsole("main.js",`Designated start yeardate is ${dSTART} (${tSTART.toDateString()}).`,false);
    DConsole("main.js",`Today's yeardate is ${dNOW} (${tNOW.toDateString()}).`,false);
    DConsole("main.js",`Today is ${dNOW-dSTART} days after start yeardate.`,true)

    const sTrans2       = 5; //--------------------------------------------------------------
    const sTransition   = .5; //percent
    const sHold         = .5; //percent
    const sOffset       = 0; //percent

// ==========================<{Changing Variables}>============================ //
    var jSTORY;

    var STORY = [];
    var INFO;
    var CurrentChapter;
    var MaximumChapter = 0;
    var PrologueChapters = 1; // Number of prologue chapters present in manuscript.
    var ScrollProgress = 0;
    var PageElementList = [];
    var Position = 0;
    var TOCchapterTARGET = "";

    var ShownCover = 1;

    ThisStoryTheme = "Default"
    LastStoryTheme = "Default"

    var CODY_Opacity    = 0.00;
    var KAT_Opacity     = 0.00;
    var TIE_Opacity     = 0.00;

    

// ==============================<{Functions}>======================== //

function Num2txt(number) {
    let prefix = "Chapter ";
    const lownum = ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Eleven","Twelve","Thirteen","Fourteen","Fifteen","Sixteen","Seventeen","Eighteen","Nineteen"];
    const highnum = ["Twenty","Thirty","Forty","Fifty","Sixty","Seventy","Eighty","Ninety"];
    if (number <= 0) {
        return "Prologue";
    } else if (number > 19) {
        const tens = Math.floor(number / 10);
        const ones = number % 10;
        return prefix + highnum[tens - 2] + (ones > 0 ? " " + lownum[ones] : "");        
    } else {
        return prefix + lownum[number];
    }
}

async function LoadAnnouncements() {
    eSTARTBOX.style.opacity="1";
    eANNOUNCE.innerHTML = `<div><h3 class="Announcements"> Announcements </h3></div>`;
    Object.entries(ANNOUNCE[ActiveStory]).reverse().forEach( ([timestamp,content]) => {
        eANNOUNCE.innerHTML += `<div> <p><strong><u>${timestamp}: </u></strong></p><p class="Announcements"> ${content}</p></div>`;
    })
}
async function DismissAnnouncements() {
    //this.outerHTML = "";
    eSTARTBOX.style.animation = '1.0s ease-in-out 0.5s forwards fadeout';
    eSTARTBOX.style.pointerEvents = "none";
}
function SetViewerMode() {
    let p_str = "";
    switch (PermissionLevel) {
    case 3:
        p_str = `
        <div class="PermBox">
            <h3> Author Mode </h3>
            <p> Or Cheater Mode, for very perceptive code monkeys that want to preview unfinished releases before they are available. </p>
        </div>`;
        break;
    case 2:
        p_str = `
        <div class="PermBox">
            <h3> Editor/Reviewer Mode </h3>
            <p> You have been given special access to all chapters of the manuscript. Some chapters contain my commentary on the chapter and my vision for the story. </p>
        </div>`;
        break;
    }
    eSTARTBOX.innerHTML += p_str; 
}
function yeardate(date) {
    const month = date.getMonth();
    var result = date.getDate();
    for (let i = 0 ; i < month ; i++) {
        result += new Date(date.getFullYear(),i+1,0).getDate();
    }
    result += (date.getFullYear()-2025)*365;
    return result;
}
function SaveState() {    
    localStorage.setItem(`AC_SETTINGS_${ActiveStory}`,JSON.stringify(SETTINGS))
    localStorage.setItem(`AC_PREFS_${ActiveStory}`,JSON.stringify(PREFS));
    DConsole("main.js > SaveState","User preference changes saved to internal storage.",true)
}
async function LoadPreferences() {
    let saveprefs = localStorage.getItem(`AC_PREFS_${ActiveStory}`);
    let savesettings = localStorage.getItem(`AC_SETTINGS_${ActiveStory}`);
    if (saveprefs && savesettings) {
        try {
            PREFS = JSON.parse(saveprefs);
            PREFS.StartChapter < 0 ? PREFS.StartChapter = 0 : PREFS.StartChapter;
            SETTINGS = JSON.parse(savesettings);

            Object.values(SETTINGS).forEach( setting  => {                
                ROOT.style.setProperty(setting.CSSname,setting.Options[setting.Setting]);
            });      

            CurrentChapter = STORY[PREFS.StartChapter];

            let newstate = (PREFS.DisplayMode=="Dark")?0:1;
            ROOT.style.setProperty("--IconState",`invert(${newstate})`)
   
            DConsole("main.js > LoadPreferences","User preferences successfully loaded from Local Storage.",true)
        } catch (error) {
            DConsole("main.js > LoadPreferences","Unable to load user PREFS from saved. \n << Error content: " + error + " >>",true)
            // Reset to default.
            PREFS = PreferencesDefault;
            SETTINGS = SettingsDefault;


        }
    } else {
        DConsole("main.js > LoadPreferences","Preferences have not been set yet.",true)
    }
}
function InvertIcons() {
    let newstate = (PREFS.DisplayMode=="Dark")?0:1;
    ROOT.style.setProperty("--IconState",`invert(${newstate})`)
    SetMessageState();
}
function SetMessageState() {
    let newstate = (PREFS.DisplayMode=="Dark")?0:1;
    ROOT.style.setProperty("--MsgColorTo",(newstate==0?"rgba(33, 138, 255, 0.8)":"rgba(33, 138, 255, 0.8)"));
    ROOT.style.setProperty("--MsgFontColorTo",(newstate==0?"white":"white"));
    ROOT.style.setProperty("--MsgColorFrom",(newstate==0?"rgba(129, 129, 129, 0.8)":"rgba(235, 235, 235, 0.8)"));//"rgba(216, 216, 216, 0.8)"));
    ROOT.style.setProperty("--MsgFontColorFrom",(newstate==0?"white":"black"));
}
function SetPreferences(property,increment) {
    let Params = SETTINGS[property];
    let range = [ 0 , Params.Options.length ];
    let current = Params.Setting;
    let queried = current + increment;

    if (queried >= range[0] && queried < range[1]) {
        Params.Setting = queried;
        PREFS[property] = Params.Options[queried];
        ROOT.style.setProperty(Params.CSSname,PREFS[property])
        DConsole("main.js > SetPreferences",`Parameter '${property}' is now set to ${PREFS[property]}.`)

        SaveState();

        SetScrollerEvents();
        runScrollEvents();

    } else {
        DConsole("main.js > SetPreferences",`NOTICE: Parameter setting for '${property}' is out of bounds [${range[0]},${range[1]}].`,true)
    }

}
async function fetchJSON() {
    // Check if we already have this saved locally first.
    let SavedContent = localStorage.getItem(`AC_SAVE_${ActiveStory}`);
    if(SavedContent) {
        try {
            let jSavedContent = JSON.parse(SavedContent.replaceAll(/(\r\n|\n|\r)/gm, ''));
            if (jSavedContent.Created == DATEKEY) {
                let result = ParseStory(jSavedContent);
                DConsole("main.js","Loaded existing text in local storage.\n",false);
                return result;
            }
        } catch (error) {
            DConsole("main.js","Error loading existing text in local storage.\n"+error+"\n",false);
        }
    }
    // If not, proceed to load.
    try {
        let sourcelocation = LOCATION.StoryRoot + LOCATION.StoryFile;
        const response = await fetch(sourcelocation);
        if (!response.ok) {
            DConsole("main.js","ERROR: Network response failure for story JSON.\n",false);
        }
        const data = await response.text();
        let jDATA = JSON.parse(data.replaceAll(/(\r\n|\n|\r)/gm, ''));
        let result = ParseStory(jDATA);
        localStorage.setItem(`AC_SAVE_${ActiveStory}`,JSON.stringify(jDATA))
        DConsole("main.js > fetchJSON",`Story "${ActiveStory}" successfully loaded.\n`,true);
        return result;
    } catch (error) {
        DConsole("main.js > fetchJSON","Error in fetch process.\n> At location: "+sourcelocation+"\n> "+error,false);
    }
    DConsole("main.js > fetchJSON","fetchJSON process completed.",true);
}
function ParseStory(data) {

    // Chapters need to be counted.
    let c = 0;

    // Release dates need to be calculated.
    let ThisDate = dSTART + 0;

    // Pull non-Manuscript data first.
    INFO = {
        "Author": data.Author,
        "Created":data.Created,
        "ShortName":data.Nickname,
        "FullName":data.Project,
        "TotalWords":data.WordCount
    };

    // Iteratively load the JSON export file into something more accessible.
    
    // Variables for last and next chapter data:
    //console.debug(data)

    let Story = Object.values(data.Manuscript);
    let eRelease = dSTART;
    let StoryPassageCounter = 0;
    MaximumChapter = 0;

    for (let i=0; i<Story.length; i++) {
        // Save story array to 'entry' for easier sightreading.
        let entry = Story[i];
        let ePerspective="";

        // Iterate for each entry of the singular JSON file.
        switch(entry.DocType) {
        case "Chapter":            
            let eTitle = (entry.ChapterOverride==""||entry.ChapterOverride==undefined)?Num2txt(entry.ChapterFull - PrologueChapters):entry.ChapterOverride;
            let eSubtitle = (entry.GivenName=="")?"":entry.GivenName;
            let eActNumber = entry.ActNum;
            let eChapterNumber = entry.ChapterFull;
            let eNextPub = parseFloat(entry.NextPublish);
            let eSynopsis = entry.Synopsis;
            let eID = (entry.VerboseOverride==undefined)?(entry.ActNum-1+"."+parseFloat(entry.ChapterFull-PrologueChapters)):entry.VerboseOverride;
            let eRevisionNotes = (entry.RevisionNotes!=true)?((REVNOTES[ActiveStory][eID]==undefined)?undefined:REVNOTES[ActiveStory][eID]):entry.RevisionNotes;
            let ePublishOn = entry.PublishOn;

            //console.warn(`For ${eID}:`,REVNOTES[ActiveStory][eID])

            ePerspective = ((entry.Perspective=="Mixed")||(entry.Perspective==""))?"Default":entry.Perspective;
            //console.error(entry.VerboseOverride)
            let prefix = STYLES[ePerspective].Prefix;
            let suffix = STYLES[ePerspective].Suffix;
            
            if (ePublishOn=="") {
                eRelease += eNextPub;
            } else {
                eRelease = parseFloat(ePublishOn);
            }
            
            if (eRelease <= dNOW || PermissionLevel >= 2) {
                MaximumChapter++;
            }

            // console.log(`${PermissionLevel} - For ${eID}, ${eRelease} vs. ${dNOW} so ${MaximumChapter}`)


            STORY.push(
            {
                "Title":eTitle,
                "Subtitle":eSubtitle,
                "Act":eActNumber,
                "ChapterNumber": eChapterNumber,
                "Synopsis":eSynopsis,
                "RevNotes":eRevisionNotes,
                "ID":eID,
                "Body":[],
                "BodyFormatted":[],
                "Release":eRelease,
                "Active":eRelease<=dNOW,
                "Perspective":ePerspective,
                "Previous":"",
                "Next":""
            });
            STORY[STORY.length-1].BodyFormatted.push(`<h3 id="title_${entry.ChapterFull}" class="${ePerspective} Title">${eTitle}</h3>`);
            STORY[STORY.length-1].BodyFormatted.push(`<h3 id="sub_${entry.ChapterFull}" class="${ePerspective} Subtitle">${prefix + eSubtitle + suffix}</h3>`);
            // If in developer mode, add commentary.
            if (PermissionLevel > 1 && eRevisionNotes != undefined) {
                STORY[STORY.length-1].BodyFormatted.push(`<div class="Default TextComment"><h3>Notes To The Editor:</h3><p>${eRevisionNotes}</p>`);
            }

            // Set 'next' and 'previous' chapters as circular objexts
            if (c==0) {
                STORY[STORY.length-1].Previous = STORY[STORY.length-1];
            } else if (c==STORY.length-1) {
                STORY[STORY.length-1].Previous = STORY[STORY.length-2];
                STORY[STORY.length-2].Next = STORY[STORY.length-1];
                STORY[STORY.length-1].Next = STORY[0];
            } else {
                STORY[STORY.length-1].Previous = STORY[STORY.length-2];
                STORY[STORY.length-2].Next = STORY[STORY.length-1];
            }

            c++;
            break;
        case "Scene":
            let eBody = entry.Body.replaceAll('<p>','\n').replaceAll('</p>','').split('\n');         
            ePerspective = ((entry.Perspective=="Mixed")||(entry.Perspective==""))?"Default":entry.Perspective;
            StoryPassageCounter += 1;

            let LineIndex = 1;
            let WritingMessage = false; // Generating message div.
            STORY[STORY.length-1].BodyFormatted.push(`<h3 id="${entry.ChapterFull}.${entry.SceneFull}" class="${ePerspective} Section">${entry.ScenePart}</h3>`);
            eBody.forEach(passage => {
                if (passage != "") {
                    STORY[STORY.length-1].Body.push(passage);
                    if ((passage.search("msg") != -1)) {
                        let msgtype = 
                            (passage.search("CodyHand") != -1) ? "CodyHand" :
                            (passage.search("KatiyaHand") != -1) ? "KatiyaHand" :
                            (passage.search("TitusHand") != -1) ? "TitusHand" :
                            (passage.search("msgfromdate") != -1) ? "msgfrom" :
                            (passage.search("msgfrom") != -1) ? "msgfrom" :
                            (passage.search("msgtodate") != -1) ? "msgto" :
                            (passage.search("msgto") != -1) ? "msgto" : "";

                        let writershand = "";
                        if (msgtype == "msgnote") {
                            writershand = `${ePerspective}Hand`;
                            passage = passage.replaceAll("msgnote",`${writershand} msgnote`);
                        }
                        if (passage.search("Titus") != -1) { console.warn(passage)}
                        if ((WritingMessage == false) || (WritingMessage == true && (passage.search("msgfromdate") != -1 || passage.search("msgtodate") != -1))) {
                            STORY[STORY.length-1].BodyFormatted.push(
                                `<p id="${entry.ChapterFull}.${entry.SceneFull}.${LineIndex++}" class="${ePerspective} ${msgtype} ${writershand}" style="line-height: 1.25em;padding-left:20px;padding-right:20px;">`
                                + passage
                            );                   
                            WritingMessage = true;
                        } else {
                            STORY[STORY.length-1].BodyFormatted[STORY[STORY.length-1].BodyFormatted.length-1] += '<br>' + (passage);
                        }
                    } else {
                        if(WritingMessage == true) {
                            WritingMessage = false;
                            STORY[STORY.length-1].BodyFormatted[STORY[STORY.length-1].BodyFormatted.length-1] += (`</p>`);
                        }
                        
                        STORY[STORY.length-1].BodyFormatted.push(
                            `<p id="${entry.ChapterFull}.${entry.SceneFull}.${LineIndex++}" class="${ePerspective}">`
                            + passage
                            + `</p>`
                    )   ;
                    }
                    
                }              
            });
            break;
        default:
            break;
        }
    }
    DConsole("initialize.js > ParseStory",`Story ${ActiveStory} has been successfully parsed.`,false)
    DConsole("initialize.js > ParseStory",`This story contains ${STORY[STORY.length-1].ChapterNumber} chapters and ${StoryPassageCounter} passages.`,false)
    return data;
}
function Event_Pulse( keyframe, progress, previous, next, transition, hold , offset , wasTheme, isTheme) {
    let pStart  = progress - (transition/2) - (hold/2) + offset;
    let pEnd    = progress + (transition/2) + (hold/2) + offset;

    // Initial node.
    keyframe.push([progress,previous[0],previous[1],previous[2],previous[3], wasTheme, isTheme]);
}
function Event_Switch( keyframe, progress, previous, next, transition, hold , offset , wasTheme, isTheme ) {
    // NOTE: 'hold' has no effect.
    let pStart  = progress - (transition/2) + offset;
    let pEnd    = progress + (transition/2) + offset;

    keyframe.push([pStart,previous[0],previous[1],previous[2],previous[3], wasTheme, isTheme]);
    keyframe.push([pEnd,next[0],next[1],next[2],next[3], wasTheme, isTheme]);


}
function SetScrollerEvents() {
    let PageElements = ePAGE.childNodes;
    let LastStyle = "Default";//PageElements[0].className.split(" ")[0];
    let ThisStyle = PageElements[0].className.split(" ")[0];

    Keyframes = {
        "Text":[],
        "Background":[],
        "ProgressBar":[]
    };

    // Start on neutral theme.
    let Progress = 0;
    let Style = STYLES["Default"][PREFS.DisplayMode]
    MODES.forEach( mode  => {
        Keyframes[mode].push([Progress,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], LastStyle+"", ThisStyle+""]);
        let last = STYLES[LastStyle][PREFS.DisplayMode][mode]
        let next = STYLES[ThisStyle][PREFS.DisplayMode][mode]
        Previous = [last[0],last[1],last[2],last[3]];
        Next = [next[0],next[1],next[2],next[3]];
        Event_Switch(Keyframes[mode],Progress,Previous,Next,4.00,0.00,2.00, LastStyle+"", ThisStyle+"");
    });

    let IsFirstElement = true;

    for (let i=0; i<PageElements.length; i++) {
        element = PageElements[i];
        // Get previous style and current style.
        LastStyle = ThisStyle + "";
        ThisStyle = element.className.split(" ")[0];

        if ( (ThisStyle != LastStyle) ) { //|| (IsFirstElement && (element.tagName == "P")) || (i == PageElements.length-5) ) {
            //console.log("Style change.",LastStyle,ThisStyle)
            IsFirstElement = false;
            let Progress = ScrollPosition(element);
            let Style = STYLES[ThisStyle][PREFS.DisplayMode];
            MODES.forEach( mode  => {
                let last = STYLES[LastStyle][PREFS.DisplayMode][mode]
                let next = STYLES[ThisStyle][PREFS.DisplayMode][mode]
                Previous = [last[0],last[1],last[2],last[3]];
                Next = [next[0],next[1],next[2],next[3]];
                Event_Switch(Keyframes[mode],Progress,Previous,Next,sTrans2,sHold,-0.5, LastStyle+"", ThisStyle+"");
            });
        }
    }



    // End on neutral theme.
    Progress = 100;
    Style = STYLES["Default"][PREFS.DisplayMode]
    ThisStyle = "Default";
    MODES.forEach( mode  => {
        let last = STYLES[LastStyle][PREFS.DisplayMode][mode]
        let next = STYLES[ThisStyle][PREFS.DisplayMode][mode]
        Previous = [last[0],last[1],last[2],last[3]];
        Next = [next[0],next[1],next[2],next[3]];
        Event_Switch(Keyframes[mode],Progress,Previous,Next,2.00,0.00,-2.00, LastStyle+"", ThisStyle+"");
        Keyframes[mode].push([Progress,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], LastStyle+"", ThisStyle+""]);
    });

   
    //--console.log(PageElementList);
    //--console.log(LastStyle)
    //--console.debug(Keyframes)
}
function ChannelSet(CHANNEL) {
    LastElement = CHANNEL[0];
    NextElement = CHANNEL[1];
    for (let i=0; i<CHANNEL.length-1; i++) {
        if (CHANNEL[i][0] < Position) {
            LastElement = Object.assign({}, CHANNEL[i]);
            NextElement = Object.assign({}, CHANNEL[i+1]);
        }
    }      
    let Progress = (NextElement[0]-Position)/(NextElement[0]-LastElement[0])
    
    /*
    console.debug(`
    Last Element: ${LastElement[0]},${LastElement[1]},${LastElement[2]},${LastElement[3]}\n
    Next Element: ${NextElement[0]},${NextElement[1]},${NextElement[2]},${NextElement[3]}\n
    Position: ${Position}\n
    Progress: ${Progress}
    `);
    */

    //console.log(LastElement,NextElement)

    /*
    console.info(`
    LAST:\t${LastElement[5]}\t${LastElement[6]}\n
    NEXT:\t${NextElement[5]}\t${NextElement[6]}\n
    ${Progress}
    `)
    */

    let RED = (LastElement[1]*Progress)+(NextElement[1]*(1-Progress));
    let GRN = (LastElement[2]*Progress)+(NextElement[2]*(1-Progress));
    let BLU = (LastElement[3]*Progress)+(NextElement[3]*(1-Progress));      
    let ALP = ((NextElement[5]=="Cody")*Progress)+((LastElement[6]=="Cody")*(1-Progress));    
        
    let FadeThresh = 0.93
    let StartEndPerc = Math.abs(Position-50)*2;
    let StartEndOff = StartEndPerc-(100*FadeThresh)
    let StartEndMul = StartEndOff<0 ? 1 : 1-(StartEndOff/(100-(100*FadeThresh)))

    //console.log(StartEndMul)

    //CODY_Opacity = ALP * StartEndMul;
    //KAT_Opacity = (1-ALP) * StartEndMul;

    let State1 = `${LastElement[5]}${LastElement[6]}`;
    let State2 = `${NextElement[5]}${NextElement[6]}`;

    CODY_Opacity = ((NextElement[5]=="Cody") * Progress)  + ((LastElement[6]=="Cody") * (1-Progress));
    KAT_Opacity = ((NextElement[5]=="Katiya") * Progress) + ((LastElement[6]=="Katiya") * (1-Progress));
    TIE_Opacity = ((NextElement[5]=="Titus") * Progress)  + ((LastElement[6]=="Titus") * (1-Progress));

    /*
    if( ((LastElement[6]=="Default") && (NextElement[6]=="Default")) || ((LastElement[5]=="Default") && (NextElement[5]=="Default"))) {
        CODY_Opacity = KAT_Opacity = 0;
    }
    */

    let IsStartOf = false;

    if((NextElement[5]=="Cody")&&(LastElement[6]=="Cody")) {
        ThisStoryTheme = "Cody";
    } else if ((NextElement[5]=="Katiya")&&(LastElement[6]=="Katiya")) {
        ThisStoryTheme = "Katiya";
    } else if ((NextElement[5]=="Titus")&&(LastElement[6]=="Titus")) {
        ThisStoryTheme = "Titus";
    } else {
        ThisStoryTheme = "Default";
    }
    
    if ((LastElement[6]=="Default")&&(NextElement[6]=="Default")) {
        ThisStoryTheme = LastElement[5];
        IsStartOf = true;
    } else if ((LastElement[5]=="Default")&&(NextElement[5]=="Default")) {
        ThisStoryTheme = NextElement[6];
        IsStartOf = true;
    }

    //console.log(ThisStoryTheme)

    if((ThisStoryTheme != LastStoryTheme) || IsStartOf) {

        if(ThisStoryTheme == "Cody") {
            ROOT.style.setProperty("--ActiveTitle","var(--CodyTitle)")
            ROOT.style.setProperty("--ActiveSub"  ,"var(--CodyText )")
            ROOT.style.setProperty("--ActiveSize" ,"1.1em")            
        } else if (ThisStoryTheme == "Katiya") {
            ROOT.style.setProperty("--ActiveTitle","var(--KatiyaTitle)")
            ROOT.style.setProperty("--ActiveSub"  ,"var(--KatiyaText )")
            ROOT.style.setProperty("--ActiveSize" ,"1.2em")
        } else if (ThisStoryTheme == "Titus") {
            ROOT.style.setProperty("--ActiveTitle","var(--TitusTitle)")
            ROOT.style.setProperty("--ActiveSub"  ,"var(--TitusText )")
            ROOT.style.setProperty("--ActiveSize" ,"1.2em")
        } else {

        }

        if(ThisStoryTheme != LastStoryTheme) {
            DConsole("main.js > ChannelSet",`Transitioning from ${LastStoryTheme} to ${ThisStoryTheme}.`,true)
        }
        
    }
    
    LastStoryTheme = ThisStoryTheme + "";


    return [RED,GRN,BLU,ALP];
}
function ToggleTOC() {
    isTOCshown = !isTOCshown    
    eFULL.style.top = (isTOCshown)?  '0'  :  '-110vh'  ;
    eFULL.style.animation = ("1s ease-in-out 0.25s forwards" + ((isTOCshown)?" slide-up ":" slide-down "));
    eTOC.style.animation = ("1s ease-in-out 0.25s forwards" + ((isTOCshown)?" fadein ":" fadeout "));
    eFULL.style.opacity = (isTOCshown)?  1  :  0  ;
    eTOC.style.opacity  = (isTOCshown)?  1  :  0  ;     
    eFULL.style.pointerEvents = (isTOCshown)?"none":"all";
       
}
function TOChtmlACT(nAct,name) {
    let result = `
    <div id="TOC-ACT${nAct}" class="TOC Act">
        <div id="TOC-ACT${nAct}-ROW" class="TOC ActRow">          
            ${name} 
        </div>
        <div class="ChapterSet" id="TOC-ACT${nAct}-CHAPTERS">
        </div>
    </div>
    `
    TOCchapterTARGET = `TOC-ACT${nAct}-CHAPTERS`;
    return result;
}
function TOChtmlCHAPTER(nChap,name,synopsis,pubdate,nDisplayed,percent,isnew) {
    //console.info(`${nChap},${name},${synopsis},${pubdate},${nDisplayed},${percent},${isnew}`)
    ChapterIsActive = (nChap <= MaximumChapter);
    //console.info(MaximumChapter)
    let ChapterInteraction = ChapterIsActive?(`class="TOC ChapterRow activerow ${isnew?'newrow':''}"  onclick="CurrentChapter=STORY[${nChap-1}];PlaceChapter(CurrentChapter);SaveState();ToggleTOC();"`):(`class="TOC ChapterRow inactiverow ${isnew?'newrow':''}"`);

    let result = `    
        <div id="TOC-CH${nChap}" ${ChapterInteraction}> 
            <div id="TOC-CH${nChap}-DATE" class="TOC ChapterDate">${pubdate}</div>
            <div class="TOCmarker" ${ChapterIsActive?'style="background-color: rgba(var(--ColorSecondary),1"':''}></div>
            <div id="TOC-CH${nChap}-STATE" class="ChapterState" style="height:${percent}%"></div>
            <div id="TOC-CH${nChap}-NUM" class="TOC ChapterNumber"><span>${('00'+nDisplayed).slice(-2)}</span></div>
            <div id="TOC-CH${nChap}-DESC" class="TOC ChapterDescription">
                <div id="TOC-CH${nChap}-NAME" class="TOC ChapterName">${name}</div>
                <div id="TOC-CH${nChap}-SYN" class="TOC ChapterSynopsis">${synopsis}</div>
            </div>            
        </div>
    `;
    return result;
}

function pad(num, size) {
    var s = "000000000" + num;
    return s.substr(s.length-size);
}
function AdjustedIndex(index) {
    return (index < 2)?0:index-PrologueChapters;
}
async function BuildTOC() {
    //console.debug("Building the Table Of Contents...");
    eTOC.innerHTML = ''; //TOC clear ------------------------//    
    let RelDate = tSTART;

    let today = parseFloat(yeardate(tNOW));
    let startday = parseFloat(yeardate(tSTART));
    let releaseday = parseFloat(yeardate(tSTART));
    let lastrelease = releaseday + 0;

    //console.log(`${today}, ${startday}, ${releaseday}`)
    let ChapterMaxNumberT = 0;
      
    let ActCtr = 0;  

    let statChapterTypes = [0,0,0,0];
    let statReleaseDay = [];

    jSTORY.Manuscript.forEach( parcel => {
        let pType = parcel.DocType;
        let pAct = parcel.ActNum;
        let pChapter = parcel.ChapterFull;
        let pScene = parcel.SceneFull;   
        
        let ChapterIsActive = true;

        let DatePercentage = 1;    
        
        //console.warn(`${pType},${pAct},${pChapter},${pScene}`)

        switch (pType) {
            case "Act":
                ActCtr++;
                //console.log("Act "+ActCtr)
                eTOC.innerHTML += TOChtmlACT(ActCtr,parcel.DocName);
                break;
            case "Chapter":
                //console.info(`${today} ... ${releaseday}`)
                let NextPush = parcel.NextPublish==undefined?7:parcel.NextPublish;
                if (parcel.PublishOn==""){
                    releaseday += parseFloat(NextPush);
                } else {
                    releaseday = parseFloat(parcel.PublishOn);
                    NextPush = releaseday - lastrelease;
                }
                statReleaseDay.push([parcel.ChapterFull+0,releaseday+0,parcel.GivenName+""]);

                //console.debug(NextPush)
                
                ChapterMaxNumberT++;
                RelDate = new Date(Date.parse(RelDate) + (86400000*parseFloat(NextPush)));
                let EntryDateStr = `${pad(RelDate.getMonth()+1,2)}/${pad(RelDate.getDate(),2)}`// /${RelDate.getFullYear().toString().slice(2,4)}`
                //console.warn(EntryDateStr)
                document.getElementById(TOCchapterTARGET).innerHTML += TOChtmlCHAPTER(parcel.ChapterFull,parcel.GivenName,parcel.Synopsis,EntryDateStr,AdjustedIndex(parcel.ChapterFull),DatePercentage,
                ((today >= releaseday)&&(today <= (releaseday+7) )) )
                // Calculating height of date progress bar:                  

                if (today >= releaseday) {
                    DatePercentage = 1;
                } else if (today <= startday) {
                    DatePercentage = 0;
                } else {
                    DatePercentage = (today - startday) / (releaseday - startday);
                }

                // Statistics for nerds.
                let DaysBetween = today - releaseday
                if(DaysBetween > 7) {
                    statChapterTypes[0] += 1; // Out for a while.
                } else if (DaysBetween >= 0) {
                    statChapterTypes[1] += 1; // Released within a week.
                } else if (DaysBetween >= -7) {
                    statChapterTypes[2] += 1; // Coming this week.
                } else {
                    statChapterTypes[3] += 1; // Not here yet.
                }

                let VertBar = document.getElementById(`TOC-CH${parcel.ChapterFull}-STATE`)

                //console.log(`Release #${ChapterMaxNumberT}\n  starts ${startday},\n  now is ${today},\n  ends ${releaseday}\n  percentage ${DatePercentage}.`)
                
                VertBar.style.height = `${DatePercentage * 100}%`;
                VertBar.style.top = `
                ${((-0.5) - ((1-DatePercentage)/2))*100}%`;
                
                startday = releaseday + 0;
                lastrelease = releaseday + 0;
                break;
        }
    });
    DConsole("main.js > BuildTOC",`Table Of Contents for ${ActiveStory} has been built.`,false);
    DConsole("main.js > BuildTOC",`Distribution of releases:\n\t      Old Releases  | ${statChapterTypes[0]}\n\t      New Releases  | ${statChapterTypes[1]}\n\t  Coming This Week  | ${statChapterTypes[2]}\n\t          Upcoming  | ${statChapterTypes[3]}`,false);
    DConsole("main.js > BuildTOC",`Release Day By Chapter:`,false);
    DConsole("main.js > BuildTOC",statReleaseDay,true,true);
}
function PlaceChapter(CHAPTER) {
    console.log(CurrentChapter)
    StartChapter = CurrentChapter.ChapterNumber;
    // NOTE: Chapter number is (1) ahead of indexing. 
    ePAGE.innerHTML = "";
    //console.log(CHAPTER.Active)
    if( CHAPTER.Active || PermissionLevel >= 2) {
        CHAPTER.BodyFormatted.forEach( Line => {
            ePAGE.innerHTML += Line;
        }) 
        //ePAGE.innerHTML += `<div class="EndSpacer"></div>`;
        eWINDOW.scrollTop = 0;
        PREFS.StartChapter = CurrentChapter.ChapterNumber-1;
        SetScrollerEvents();    
        SetInfo();        
    } else {
        ePAGE.innerHTML += "Chapter is not active yet. Check back later."
    }
     DConsole("main.js > PlaceChapter",`Chapter ${CurrentChapter.ChapterNumber} "${CHAPTER.Title}" has been placed. \n Here are the contents of the CHAPTER object:`,false,false);
     DConsole("main.js > PlaceChapter",CHAPTER,true,true)
}

async function setup() {

    jSTORY = await fetchJSON();
    await LoadPreferences();
    if (DoAnnouncements) { 
        DConsole("main.js > setup","Loading announcements.", true)
        await LoadAnnouncements(); 
    } else {        
        eSTARTBOX.outerHTML = "";
        DConsole("main.js > setup","Skipping announcements.", true)
    }
    // Set current chapter.
    if ( !isNaN(parseFloat(SrcParams.get('startchapter'))) ) {
        CurrentChapter = STORY[parseFloat(SrcParams.get('startchapter'))];
        console.warn(`> Notice: Story "${ActiveStory}" set from search variables to Chapter ${CurrentChapter}.`)
    } else {
        CurrentChapter = STORY[PREFS.StartChapter];
    }    
    PlaceChapter(CurrentChapter);
    runScrollEvents();
    SetInfo();
    SetMessageState();
    await BuildTOC();
    SetViewerMode();    
}
function ScrollPosition(elem) {
    let PageRect = ePAGE.getBoundingClientRect();
    let ItemRect = elem.getBoundingClientRect();
    let BodyRect = eWINDOW.getBoundingClientRect();

    let PageHeight = PageRect.height - BodyRect.height;
    let PositionHeight = ItemRect.top - BodyRect.top;
    let ScrollPos = Math.abs(((PositionHeight/PageHeight)*100))
    ScrollPos = (ScrollPos>=100)?
                        100:
                        ((ScrollPos<=0)?
                            0:
                            ScrollPos);

    /*
    console.debug(`
    Page height is at ${PageRect.height} - ${BodyRect.height} = ${PageHeight}.
    Position height is at ${ItemRect.top} - ${BodyRect.top} = ${PositionHeight}.
    `);
    */
    return ScrollPos;
}
function ApplyColors() {

    ROOT.style.setProperty("--TextColor",`rgba(${CHSET["Text"][0]},${CHSET["Text"][1]},${CHSET["Text"][2]},${1})`);
    ROOT.style.setProperty("--BackgroundColor",`rgba(${CHSET["Background"][0]},${CHSET["Background"][1]},${CHSET["Background"][2]},${1})`);
    ROOT.style.setProperty("--BarColor",`rgba(${CHSET["ProgressBar"][0]},${CHSET["ProgressBar"][1]},${CHSET["ProgressBar"][2]},${1})`);
    ROOT.style.setProperty("--HoverColor",`rgba(${CHSET["ProgressBar"][0]},${CHSET["ProgressBar"][1]},${CHSET["ProgressBar"][2]},${0.1})`);
    ROOT.style.setProperty("--TOCbackground",`rgba(${CHSET["ProgressBar"][0]},${CHSET["ProgressBar"][1]},${CHSET["ProgressBar"][2]},${0.03})`);
    ROOT.style.setProperty("--CodyOp",CODY_Opacity); /*CHSET["Background"][3]);/**/
    ROOT.style.setProperty("--KatiyaOp",KAT_Opacity); /*1-CHSET["Background"][3]);/**/
    ROOT.style.setProperty("--TitusOp",TIE_Opacity); /*1-CHSET["Background"][3]);/**/
    //console.log(CHSET["Background"][3])
}
function SetInfo() {
    eDATA.innerHTML = 
          "<h4 class='InfoTitle'>" + ActiveStory + " " + CurrentChapter.ID + "</h4><p class='InfoSub'>"
        + CurrentChapter.Title + "<br>"
        + CurrentChapter.Subtitle + "</p>"
        ; 
}
function runScrollEvents() {
    Position = ScrollPosition(ePAGE);
    //console.log(ScrollProgress);
    ePROGRESS.style.width = `${Position}%`;   

    MODES.forEach( mode => {
        CHSET[mode] = ChannelSet(Keyframes[mode])
    })

    ApplyColors();
    
    //console.log(CHSET["Background"][3]) /**-*/
    
}
