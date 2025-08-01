
    const sTrans2       = 5; //--------------------------------------------------------------
    const sTransition   = .5; //percent
    const sHold         = .5; //percent
    const sOffset       = 0; //percent

    const RevLum = 50;

// ==========================<{Changing Variables}>============================ //
    
async function LoadAnnouncements() {
    eSTARTBOX.style.opacity="1";
    eANNOUNCE.innerHTML = `<div><h3 class="Announcements"> Announcements </h3></div>`;
    Object.entries(ANNOUNCE[ActiveStory]).reverse().forEach( ([timestamp,content]) => {
        eANNOUNCE.innerHTML += `<div> <p><strong><u>${timestamp}: </u></strong></p><p class="Announcements"> ${content}</p></div>`;
    })
}
async function DismissAnnouncements() {
    //this.outerHTML = "";
    //eINSTRUCT.style.opacity="1";
    eINSTRUCT.style.animation = '3.0s ease-in-out 1.0s forwards flashing';
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
function SaveState() {    
    localStorage.setItem(`AC_SETTINGS_${ActiveStory}`,JSON.stringify(SETTINGS))
    localStorage.setItem(`AC_PREFS_${ActiveStory}`,JSON.stringify(PREFS));
    DConsole("main.js > SaveState","User preference changes saved to internal storage.",false)
    DConsole("main.js > SaveState",`Bookmarked to Chapter ${PREFS.StartChapter}.`,true)
}
async function LoadPreferences() {
    let saveprefs = localStorage.getItem(`AC_PREFS_${ActiveStory}`);
    let savesettings = localStorage.getItem(`AC_SETTINGS_${ActiveStory}`);
    if (saveprefs && savesettings) {
        try {
            PREFS = JSON.parse(saveprefs);

            //console.error(PREFS.StartChapter)

            let VarChapter = parseFloat(SrcParams.get('chapter'));

            PREFS.StartChapter = ( isNaN(VarChapter) ) ? PREFS.StartChapter : VarChapter;
            PREFS.StartChapter = PREFS.StartChapter < 0 ?  0 : PREFS.StartChapter;// (PREFS.StartChapter > MaximumChapter ? MaximumChapter : PREFS.StartChapter);
            
            SETTINGS = JSON.parse(savesettings);

            Object.values(SETTINGS).forEach( setting  => {                
                ROOT.style.setProperty(setting.CSSname,setting.Options[setting.Setting]);
            });      

            
            CurrentChapter = STORY[VarChapter];

            //console.error(CurrentChapter);

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
    ROOT.style.setProperty("--MsgColorFrom",(newstate==0?"rgba(129, 129, 129, 0.8)":"rgba(215, 215, 215, 0.8)"));//"rgba(216, 216, 216, 0.8)"));
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
async function fetchText(location)
{
    try {
        const response = await fetch(location);
        if (!response.ok) {
            DConsole("initialize.js > fetchText","Error pulling text item.")
        }
        let result = await response.text();
        return result;
    } catch (error) {
        DConsole("initialize.js > fetchText","Error processing text item from URL.")
    }
}

async function fetchJSON() {
    // Check if we already have this saved locally first.
    /*
    let SavedContent = localStorage.getItem(`AC_SAVE_${ActiveStory}`);
    if(SavedContent != null) {
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
    */
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
        DConsole("main.js > fetchJSON","Error in fetch process.\n >"+error,false);
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
            let eRevisionNotes = (entry.AuthorNotes!="")?entry.AuthorNotes:undefined;/*((REVNOTES[ActiveStory][eID]==undefined)?undefined:REVNOTES[ActiveStory][eID]):entry.RevisionNotes;/**/
            let ePublishOn = entry.PublishOn;
            let eStatus = entry.Status;

            //console.warn(`For ${eID}:`,REVNOTES[ActiveStory][eID])

            ePerspective = ((entry.Perspective=="Mixed")||(entry.Perspective==""))?Story[i+1].Perspective:entry.Perspective;
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
                "Next":"",
                "Status":eStatus,
                "WordCount":0
            });
            STORY[STORY.length-1].BodyFormatted.push(`<h3 id="title_${entry.ChapterFull}" class="${ePerspective} Title">${eTitle}</h3>`);

            let PercentComplete = parseFloat(entry.PercentComplete)
            PercentComplete = isNaN(PercentComplete) ? 0 : PercentComplete < 0 ? 0 : PercentComplete > 100 ? 100 : Math.round(PercentComplete);
            STORY[STORY.length-1].BodyFormatted.push( (PermissionLevel <= 1) ? "" : `<div style="width:fit-content;position:relative;left:50%;transform:translateX(-50%);font-size:1.2em;border: 1px solid var(--TextColor); padding:8px; border-radius: 10px;"><span style="font-size:1.2em;color:var(--TextColor);font-family:var(--ActiveTitle);margin:20px;">Revision: </span><span class="DebugStatus DS-${entry.Status.replaceAll(" ","")}" style="font-size:1em; background-color: hsl(${Math.round((Math.pow(PercentComplete/100,3)) * 100 * (120/100))},${((PercentComplete!=0))*RevLum}%,50%);">${entry.Status.replaceAll("No Status","Unwritten")
                                                                                                                 .replaceAll("First Draft","First")
                                                                                                                 .replaceAll("Revised Draft","Second")
                                                                                                                 .replaceAll("Final Draft","Final")}</span> <span class="DebugStatus DS-${entry.Status.replaceAll(" ","")}" style="font-size:1em; background-color: hsl(${Math.round((Math.pow(PercentComplete/100,3)) * 100 * (120/100))},${((PercentComplete!=0))*RevLum}%,50%);">${PercentComplete}</span></div>`);
            STORY[STORY.length-1].BodyFormatted.push(`<h3 id="sub_${entry.ChapterFull}" class="${ePerspective} Subtitle">${prefix + eSubtitle + suffix}</h3>`);
            // If in developer mode, add commentary.
            if (PermissionLevel > 1 && eRevisionNotes != undefined) {
                STORY[STORY.length-1].BodyFormatted.push(`<div class="Default TextComment"><h3>Notes To The Editor:</h3><p>${eRevisionNotes}</p>`);
            }
            if (DoSettingTags) {
                let SecPerspective = (entry.Perspective == "Mixed" || entry.Perspective == "Both") ? Story[i+1].Perspective : entry.Perspective;
                let CharacterName = SOURCE.Shorthands.Names[SecPerspective]!=undefined ? SOURCE.Shorthands.Names[SecPerspective] : SecPerspective;
                let SettingTime = SOURCE.Shorthands.Timezones[SecPerspective]!=undefined ? entry.SettingInfo[SOURCE.Shorthands.Timezones[SecPerspective]] : entry.SettingInfo.ModernTime;
                let SettingDay = (entry.SettingInfo.StoryDay == "" || entry.SettingInfo.StoryDay == undefined || entry.SettingInfo.StoryDay == "Undefined") ? "" : "("+entry.SettingInfo.StoryDay+")";
                let SettingPlace = (entry.SettingInfo.Setting == undefined || entry.SettingInfo.Setting == "") ? entry.SettingInfo.Setting : entry.SettingInfo.Setting + "<br>" + SOURCE.Shorthands.GeneralSettings[SecPerspective];
                STORY[STORY.length-1].BodyFormatted.push(`<div class="SettingBox"><div class="SettingTag" style="font-family: var(--${SecPerspective}Title);"> <span id="SECPERSP">${CharacterName}</span><br><span>${SettingTime} ${SettingDay} </span><br><span>${SettingPlace}</span></div></div>`);
            } else {
                //STORY[STORY.length-1].BodyFormatted.push(`<br>`);
                STORY[STORY.length-1].BodyFormatted.push(`<br>${BONUS[ActiveStory].Dividers[entry.Perspective]}<br>`);
            }

            // Set 'next' and 'previous' chapters as circular objects
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
            
            try {
                document.getElementById('SECPERSP').innerHTML = SOURCE.Shorthands.Names[entry.Perspective];

            } catch (error) {
                //console.error("Unable to set perspective.")
            }

            let LineIndex = 1;
            let WritingMessage = false; // Generating message div.
            if(entry.ScenePart != 1) {
                if((entry.DoSceneNum=="True"||entry.DoSceneNum==undefined) && DoDivsForNumbers == false) {
                    STORY[STORY.length-1].BodyFormatted.push(`<h3 id="${entry.ChapterFull}.${entry.SceneFull}" class="${ePerspective} Section">${entry.ScenePart}</h3>`);
                } else {
                    STORY[STORY.length-1].BodyFormatted.push(`<br>${BONUS[ActiveStory].Dividers[entry.Perspective]}<br>`);
                }
            }
            
            eBody.forEach(passage => {
                STORY[STORY.length-1].WordCount += passage.split(" ").length - 1;
                //console.log(`Word Count for ${entry.ChapterFull}.${entry.ScenePart}: ${STORY[STORY.length-1].WordCount}`);
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
                        //if (passage.search("Titus") != -1) { console.warn(passage)}
                        if ((WritingMessage == false) || (WritingMessage == true && (passage.search("msgfromdate") != -1 || passage.search("msgtodate") != -1))) {
                            let msgsource = "";
                            Object.entries(MsgMatch).forEach( ([query,result]) => {
                                if(passage.search(query) != -1) {
                                    msgsource = result;
                                }
                            });
                            STORY[STORY.length-1].BodyFormatted.push(
                                `<p id="${entry.ChapterFull}.${entry.SceneFull}.${LineIndex++}" class="${ePerspective} from${msgsource} ${msgtype} ${writershand}" style="line-height: 1.25em;padding-left:20px;padding-right:20px;font-family: var(--MsgFont);text-align: left;">`
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

function ReturnStyleMatch( classes ) {
    result = "Default";
    THEMEINDEX[ActiveStory].forEach( style => {
        if (classes.includes(style)) {
            //console.log(style)
            result = style;
        }
    });
    return result;
}

function SetDefaultScroller() {
    Keyframes = 
    {
        "Text":[],
        "Background":[],
        "ProgressBar":[]
    };
    let Style = STYLES["Default"][PREFS.DisplayMode]
    MODES.forEach( mode  => {
        Keyframes[mode].push([-10,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], "Default", "Default"]);
        Keyframes[mode].push([110,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], "Default", "Default"]);
    });
}

function SetScrollerEvents(ThemeDivs=true) {

    let LastStyle = "Default";
    let ThisStyle = "Default";

    if(ThemeDivs) {
        let AllPageElements = ePAGE.childNodes;
        let StyleOptions = THEMEINDEX[ActiveStory];
        DConsole("main.js > SetScrollerEvents",`Detecting style changes matching { ${StyleOptions.join(",")} }.`,false);
        PageElements = Array.from(AllPageElements).filter( element => {
            let IsIncludedStyle = false;
            StyleOptions.forEach( style => {
                IsIncludedStyle = IsIncludedStyle || (element.className.split(" ").includes(style));
            });
            return IsIncludedStyle;
        });   

        LastStyle = "Default";//PageElements[0].className.split(" ")[0];
        ThisStyle = ReturnStyleMatch(PageElements[0].className.split(" "));

    }

    Keyframes = {
        "Text":[],
        "Background":[],
        "ProgressBar":[]
    };

    // Start on neutral theme.
    let Progress = 0;
    let Style = STYLES["Default"][PREFS.DisplayMode]
    DConsole("main.js > SetScrollerEvents",`\t${LastStyle} > ${ThisStyle} @ ${Math.round(Progress*100)/100}%.`,false);
    MODES.forEach( mode  => {
        Keyframes[mode].push([Progress,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], LastStyle+"", ThisStyle+""]);
        let last = STYLES[LastStyle][PREFS.DisplayMode][mode]
        let next = STYLES[ThisStyle][PREFS.DisplayMode][mode]
        Previous = [last[0],last[1],last[2],last[3]];
        Next = [next[0],next[1],next[2],next[3]];
        Event_Switch(Keyframes[mode],Progress,Previous,Next,4.00,0.00,2.00, LastStyle+"", ThisStyle+"");
    });

    let IsFirstElement = true;

    ScrollPosition(ePAGE,true,true)

    if(ThemeDivs) {

        for (let i=0; i<PageElements.length; i++) {
            element = PageElements[i];
            // Get previous style and current style.
            LastStyle = ThisStyle + "";
            let TheseStyles = element.className.split(" ");
            //console.debug(TheseStyles)
            ThisStyle = ReturnStyleMatch(TheseStyles);
            //console.debug(ThisStyle)

            if ( (ThisStyle != LastStyle) ) { //|| (IsFirstElement && (element.tagName == "P")) || (i == PageElements.length-5) ) {
                //console.log("Style change.",LastStyle,ThisStyle)
                IsFirstElement = false;
                let Progress = ItemPosition(element,false,true);
                //console.log(Progress)
                DConsole("main.js > SetScrollerEvents",`\t${LastStyle} > ${ThisStyle} @ ${Math.round(Progress*100)/100}%.`,false);
                MODES.forEach( mode  => {
                    let last = STYLES[LastStyle][PREFS.DisplayMode][mode]
                    let next = STYLES[ThisStyle][PREFS.DisplayMode][mode]
                    Previous = [last[0],last[1],last[2],last[3]];
                    Next = [next[0],next[1],next[2],next[3]];
                    Event_Switch(Keyframes[mode],Progress,Previous,Next,sTrans2,sHold,-0.5, LastStyle+"", ThisStyle+"");
                });
            }
        }
    }


    // End on neutral theme.
    Progress = 100;
    Style = STYLES["Default"][PREFS.DisplayMode]
    DConsole("main.js > SetScrollerEvents",`\t${LastStyle} > ${ThisStyle} @ ${Math.round(Progress*100)/100}%.`,false);
    ThisStyle = "Default";
    MODES.forEach( mode  => {
        let last = STYLES[LastStyle][PREFS.DisplayMode][mode]
        let next = STYLES[ThisStyle][PREFS.DisplayMode][mode]
        Previous = [last[0],last[1],last[2],last[3]];
        Next = [next[0],next[1],next[2],next[3]];
        Event_Switch(Keyframes[mode],Progress,Previous,Next,2.00,0.00,-2.00, LastStyle+"", ThisStyle+"");
        Keyframes[mode].push([Progress,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], LastStyle+"", ThisStyle+""]);
    });

    DConsole("main.js > SetScrollerEvents",PageElements,true,true);
   
    //--console.log(PageElementList);
    //--console.log(LastStyle)
    //--console.debug(Keyframes)
}
function HandleScrollerEvents() {
    let OverrideContent = CH_OVERRIDES[ActiveStory][CurrentChapter.ID];
    let IsOverride = !(OverrideContent == undefined);
    if (!IsOverride) {
        SetScrollerEvents(IsOverride);
        runScrollEvents();
    } else {
        SetDefaultScroller();
        runScrollEvents();
    }
    SetInfo();
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

    let RED = (LastElement[1]*Progress)+(NextElement[1]*(1-Progress));
    let GRN = (LastElement[2]*Progress)+(NextElement[2]*(1-Progress));
    let BLU = (LastElement[3]*Progress)+(NextElement[3]*(1-Progress));      
    let ALP = ((NextElement[5]=="Cody")*Progress)+((LastElement[6]=="Cody")*(1-Progress));    
        
    let FadeThresh = 0.93
    let StartEndPerc = Math.abs(Position-50)*2;
    let StartEndOff = StartEndPerc-(100*FadeThresh)
    let StartEndMul = StartEndOff<0 ? 1 : 1-(StartEndOff/(100-(100*FadeThresh)))

    let State1 = `${LastElement[5]}${LastElement[6]}`;
    let State2 = `${NextElement[5]}${NextElement[6]}`;

    CODY_Opacity = ((NextElement[5]=="Cody") * Progress)  + ((LastElement[6]=="Cody") * (1-Progress));
    KAT_Opacity = ((NextElement[5]=="Katiya") * Progress) + ((LastElement[6]=="Katiya") * (1-Progress));
    TIE_Opacity = ((NextElement[5]=="Titus") * Progress)  + ((LastElement[6]=="Titus") * (1-Progress));

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

        let FaviconLoc = STYLES[ThisStoryTheme].Favicon+".png";
        changeFavicon(FaviconLoc);

        if(ThisStoryTheme != LastStoryTheme) {
            DConsole("main.js > ChannelSet",`Transitioning from ${LastStoryTheme} to ${ThisStoryTheme}.`,false)
            DConsole("main.js > ChannelSet",`Favicon set to ${FaviconLoc}.`,true)
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
function TOChtmlCHAPTER(nChap,name,synopsis,pubdate,nDisplayed,percent,isnew,status,perc) {
    //console.info(`${nChap},${name},${synopsis},${pubdate},${nDisplayed},${percent},${isnew}`)
    ChapterIsActive = (nChap <= MaximumChapter);
    //console.info(MaximumChapter)
    let ChapterInteraction = ChapterIsActive?(`class="TOC ChapterRow activerow ${isnew?'newrow':''}"  onclick="CurrentChapter=STORY[${nChap-1}];PlaceOrOverlay(CurrentChapter);SaveState();ToggleTOC();"`):(`class="TOC ChapterRow inactiverow ${isnew?'newrow':''}"`);

    let PercentComplete = parseFloat(perc)
    PercentComplete = isNaN(PercentComplete) ? 0 : PercentComplete < 0 ? 0 : PercentComplete > 100 ? 100 : Math.round(PercentComplete);
            
    let WorkState = (PermissionLevel <= 1) ? "" : `<div class="DebugStatus DS-${status.replaceAll(" ","")}" style="background-color: hsl(${Math.round((Math.pow(PercentComplete/100,3)) * 100 * (120/100))},${((PercentComplete!=0))*RevLum}%,50%);">${status.replaceAll("No Status","Unwritten")
                                                                                                                 .replaceAll("First Draft","First")
                                                                                                                 .replaceAll("Revised Draft","Second")
                                                                                                                 .replaceAll("Final Draft","Final")} ${PercentComplete}</div>`;
    //console.warn(WorkState)
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
            ${WorkState}           
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
                document.getElementById(TOCchapterTARGET).innerHTML += TOChtmlCHAPTER(
                                                                            parcel.ChapterFull,
                                                                            parcel.GivenName,
                                                                            parcel.Synopsis,
                                                                            EntryDateStr,
                                                                            AdjustedIndex(parcel.ChapterFull),
                                                                            DatePercentage,
                                                                            ((today >= releaseday)&&(today <= (releaseday+7) )),
                                                                            parcel.Status,
                                                                            parcel.PercentComplete
                                                                        );
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

                if(PermissionLevel > 1) {

                }


                break;
        }
    });
    DConsole("main.js > BuildTOC",`Table Of Contents for ${ActiveStory} has been built.`,false);
    DConsole("main.js > BuildTOC",`Distribution of releases:\n\t      Old Releases  | ${statChapterTypes[0]}\n\t      New Releases  | ${statChapterTypes[1]}\n\t  Coming This Week  | ${statChapterTypes[2]}\n\t          Upcoming  | ${statChapterTypes[3]}`,false);
    DConsole("main.js > BuildTOC",`Release Day By Chapter:`,false);
    DConsole("main.js > BuildTOC",statReleaseDay,true,true);
}
function PlaceChapter(CHAPTER) {
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
        if(PermissionLevel >= 2) {     
            ePAGE.innerHTML += `<div class="Default ChapMeta">Author notes:<br>${CHAPTER.ID}&ensp;|&ensp;${CHAPTER.Status}&ensp;|&ensp;~${Math.round(CHAPTER.WordCount / 100) * 100} words&ensp;|&ensp;${Math.round(CHAPTER.WordCount/250*10)/10} mins</div>`;
        }
        } else {
        StartChapter = 1; ////////////////////////////
        ePAGE.innerHTML += "<br><br>Chapter is not active yet. Check back later."
    }
     DConsole("main.js > PlaceChapter",`Chapter ${CurrentChapter.ChapterNumber} "${CHAPTER.Title}" has been placed. \n Here are the contents of the CHAPTER object:`,false,false);
     DConsole("main.js > PlaceChapter",CHAPTER,true,true)
}

async function PlaceOrOverlay(CHAPTER) {
    let BONUS = "";
    let OverrideContent = CH_OVERRIDES[ActiveStory][CurrentChapter.ID];
    if(OverrideContent != undefined) {        
        StartChapter = CurrentChapter.ChapterNumber;
        PREFS.StartChapter = CurrentChapter.ChapterNumber-1;
        BONUS = await GetJSONFromSource(OverrideContent);
        ePAGE.innerHTML = `<div class="bonusitem">${BONUS.Content}</div>`
        isScrollerEventPage = false;       
        HandleScrollerEvents();
        SaveState();
    } else {
        PlaceChapter(CHAPTER);
        runScrollEvents();
    }    
    ROOT.style.setProperty("--SpecialOp",parseFloat(1*(OverrideContent!= undefined)));
}

function ScrollPosition(elem) {    
    let PageRect = ePAGE.getBoundingClientRect();
    let ItemRect = elem.getBoundingClientRect();
    let BodyRect = eWINDOW.getBoundingClientRect();
    
    let PageHeight = BodyRect.height - PageRect.height;
    let PositionHeight = ItemRect.top - BodyRect.top;
    
    let ScrollPos = Math.abs((PositionHeight/PageHeight)*100);
    ScrollPos = (ScrollPos>=100) ? 100 : ((ScrollPos<=0) ? 0: ScrollPos);
    
    return ScrollPos;
}

function ItemPosition(elem,signed=false,notify=false) {
    let PageRect = ePAGE.getBoundingClientRect();
    let ItemRect = elem.getBoundingClientRect();
    //let BodyRect = eWINDOW.getBoundingClientRect();
    //let BarRect = eBAR.getBoundingClientRect();

    let PageTop = PageRect.top;
    let PageBottom = PageRect.bottom;
    let ItemTop = ItemRect.top;
    //let ItemBottom = ItemRect.bottom;
    //let BodyTop = BodyRect.top;
    //let BodyBottom = BodyRect.bottom;
    //let BarTop = BarRect.top;
    //let BarBottom = BarRect.bottom;

    let Rel = ItemTop - PageTop
    let Perc = Rel / (PageBottom - PageTop);
    let ScrollPos = Math.round(Perc*100);
    
    /*
    if(notify){console.info(
  //      `${Math.round(PageTop)},\t${Math.round(PageBottom)}\n`,
  //      `${Math.round(ItemTop)},\t${Math.round(ItemBottom)}\n`,
  //      `${Math.round(BodyTop)},\t${Math.round(BodyBottom)}\n`,
 //       `${Math.round(BarTop)},\t${Math.round(BarBottom)}\n`,
        `${Math.round(Rel)},\t${Math.round(Perc*100)},\t${Math.round(ScrollPos)}\n`
    )};
    */

    //let PageHeight = BodyRect.height - PageRect.height;
    //let PositionHeight = ItemRect.top - BodyRect.top;
    /*
    let ScrollPos = signed ? ((PositionHeight/PageHeight)*100) : Math.abs((PositionHeight/PageHeight)*100)
    if(!signed) {ScrollPos = (ScrollPos>=100) ? 100 : ((ScrollPos<=0) ? 0: ScrollPos);}
    */
   
    /*if(notify){console.info(`For ${elem.id}:\nPage height is at:\n\t${Math.round(BodyRect.height)} - ${Math.round(PageRect.height)} = ${Math.round(PageHeight)}.\nPosition height is at:\n\t${Math.round(ItemRect.top)} - ${Math.round(BodyRect.top)} = ${Math.round(PositionHeight)}.\nScroll position is ${Math.round(ScrollPos)}`);}
    /**/
    return ScrollPos < 3 ? 3 : ScrollPos;
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
    ePROGRESS.style.width = `${Position}%`;  
    MODES.forEach( mode => {
        CHSET[mode] = ChannelSet(Keyframes[mode])
    })
    ApplyColors();
    
}

function zoomImage(elem) {
    isMapZoom = !isMapZoom;
    let x = 0;
    let y = 0;
    if (isMapZoom) {
        const rect = elem.getBoundingClientRect();
        x = (event.clientX - rect.left) / rect.width * 100;
        y = (event.clientY - rect.top) / rect.height * 100;
    }
    let xd = -x;
    let yd = 0;
    //console.log(`${isMapZoom}: Zooming image at ${xd}%, ${yd}%`);
    elem.style.transform = isMapZoom ? `translateX(${xd}%) translateY(${yd}%) scale(3)` : `translateX(-50%) translateY(0%) scale(1)`;
    elem.style.transition = "transform 0.5s ease-in-out";
    elem.style.zIndex = isMapZoom ? "9999" : "";
}

function ToggleInfoWindow() {
    InfoWindowState = !InfoWindowState;
    
    let BONUScontent = BONUS[ActiveStory];
    iMAPCONTENT.innerHTML = BONUScontent.Maps; // load only once.
    iEXTRAS.innerHTML = BONUScontent.Other;
    Object.entries(iMAPCONTENT.getElementsByClassName("map")).forEach( ([index,elem]) => {
        elem.setAttribute("onclick","zoomImage(this);")
    })
    Object.entries(iEXTRAS.getElementsByClassName("map")).forEach( ([index,elem]) => {
        elem.setAttribute("onclick","zoomImage(this);")
    })

    switch (InfoWindowState) {
    case true:
        eMAPINFO.style.top = "calc(var(--ControlHeight) - 30px)";
        //eMAPINFO.style.opacity = 1;
        eMAPINFO.style.pointerEvents = "all";
        //eMAPINFO.style.animation = ("1s ease-in-out 0.25s forwards fadein");
        break;
    case false:
        eMAPINFO.style.top = "100vh";
        //eMAPINFO.style.opacity = 0;
        eMAPINFO.style.pointerEvents = "none";
        //eMAPINFO.style.animation = ("1s ease-in-out 0.25s forwards fadeout");
    }   
    
}

/*!
 * Dynamically changing favicons with JavaScript
 * Works in all A-grade browsers except Safari and Internet Explorer
 * Demo: http://mathiasbynens.be/demo/dynamic-favicons
 */

// HTML5™, baby! http://mathiasbynens.be/notes/document-head
document.head = document.head || document.getElementsByTagName('head')[0];

function changeFavicon(src) {
 var link = document.createElement('link'),
     oldLink = document.getElementById('dynamic-favicon');
 link.id = 'dynamic-favicon';
 link.rel = 'shortcut icon';
 link.href = src;
 if (oldLink) {
  document.head.removeChild(oldLink);
 }
 document.head.appendChild(link);
}

async function setup() {
    jSTORY = await fetchJSON();//
    await LoadPreferences();//
    if (DoAnnouncements) { //
        DConsole("main.js > setup","Loading announcements.", true)//
        await LoadAnnouncements(); //
    } else {        //
        eSTARTBOX.outerHTML = "";//
        DConsole("main.js > setup","Skipping announcements.", true)//
    }//
    // Set current chapter.
    if ( !isNaN(parseFloat(SrcParams.get('startchapter'))) ) {
        CurrentChapter = STORY[parseFloat(SrcParams.get('startchapter'))];
        console.warn(`> Notice: Story "${ActiveStory}" set from search variables to Chapter ${CurrentChapter}.`)
    } else {
        CurrentChapter = STORY[PREFS.StartChapter];
    }    
    
    await PlaceOrOverlay(CurrentChapter);

    SetInfo();
    SetMessageState();
    await BuildTOC();
    SetViewerMode();    
}