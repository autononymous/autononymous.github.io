
// FUNDAMENTAL DATA LOCATIONS:

// Root location of all files...
const URL_ROOT = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/ScrivenerReader/";

const VersionLog = {
    "v1.00":"Reader alpha",
    "v2.00":"Reader beta",
    "v2.10":"Add version counter; fix story tag detection",
    "v2.20":"Bonus content window added.",
    "v2.23":"Minor fixes to new info window.",
    "v2.30":"Completion of Paragate introduction with theming.",
    "v2.31":"Capacity for custom scene numbering.",
    "v2.32":"Setting callouts option and custom -hr- dividers.",
    "v3.00":"New viewer with new retrieval process."
}

var isTOCshown = false;


// ----------------------------------------------- //
// Internal/Meta Functions
// ----------------------------------------------- //

function CLS() 
{
    localStorage.removeItem(`AC_SAVE`);
    localStorage.removeItem(`AC_SETTINGS`);
    localStorage.removeItem(`AC_PREFS`);
}

//
// DCONSOLE - Gathers data and prints for debug.
//    IN > title - Title of console entry.
//    IN > body - Line of text to print.
//    IN > flush - Print all saved to display.
//    IN > rawpush - Push raw item such as an object.
//
DebugItems = [];
function DConsole(title,body,flush=false,rawpush=false) 
{
    DebugItems.push([body,rawpush]);
    let DebugStr = "";
    let DebugItem = " ";
    if(flush == true) {
        DebugStr += `==================\nFrom ${title}:\n`;
        DebugItems.forEach ( ([message,method]) => {
            if(method) {
                DebugItem = message
            } else {
                DebugStr +=  `> ${message}\n`
            }            
        })
        console.debug(DebugStr,DebugItem);
        DebugItems = [];
    }    
}

// ----------------------------------------------- //
// File Receiving and Processing
// ----------------------------------------------- //

//
// GETFILE - Returns file from address.
//   IN > address - URL of file location, with extension.
//   OUT> Resulting text of file retrieved.
//
async function GetFile(address) 
{
    try {
        const response = await fetch(address)
        if(!response.ok) {
            //DConsole(`init.js > GetFile","Error pulling file from address.\n\t Address: ${address}`)
        }
        let data = await response.text();
        return data;
    } catch (error) {
        //DConsole(`init.js > GetFile","Error processing file.\n\t Error: ${error}`)
    }
}
//
// PARSEJSON - Parse text into a JSON object.
//    IN > text - Raw text to turn into JSON.
//    OUT> Resulting JSON file.
//
async function ParseJSON(text) 
{
    return JSON.parse(text.replaceAll(/(\r\n|\n|\r)/gm,''));
}
//
// GETJSON - Return file from address and parse into JSON.
//    IN > address - URL of file location, with extension.
//    OUT> Resulting JSON file.
//
async function GetJSON(address) 
{
    let text = await GetFile(address);
    return await ParseJSON(text);
}
//
// SAVELOCALDATA - Save preferences and settings to Local Storage.
//    IN > preferences - Optional direct argument.
//    IN > settings - Optional direct argument.
//
async function SaveLocalData(preferences,settings)
{
    if (preferences == undefined) preferences = PREFERENCES;
    localStorage.setItem('AC_PREFS',JSON.stringify(preferences));
    if (settings == undefined) settings = SETTINGS;
    localStorage.setItem('AC_SETTINGS',JSON.stringify(settings));
}
//
// RETRIEVELOCALDATA - Load preferences and settings from Local Storage. Otherwise, apply defaults.
//    IN > standard - Default settings.
//
async function RetrieveLocalData(standard)
{
    let preferences, settings = {};
    let Jpreferences = localStorage.getItem('AC_PREFS');
    if( Jpreferences == undefined ) {
        preferences = Object.assign( {}, standard.Preferences );        
    } else {
        try {
            preferences = JSON.parse(Jpreferences);
        } catch (error) {
            preferences = Object.assign( {}, standard.Preferences );
        }
    }
    let Jsettings = localStorage.getItem('AC_SETTINGS');
    if( Jsettings == undefined ) {
        settings = Object.assign( {}, standard.Settings );        
    } else {
        try {
            settings = JSON.parse(Jsettings);
        } catch (error) {
            settings = Object.assign( {}, standard.Settings );
        }
    }
    SaveLocalData(preferences,settings);
    return [preferences,settings]
}
//
// PARSESEARCHPARAMS - Convert search variables into a map of values.
//
function SearchMap(map, key, inputs, outputs) 
{
    let value = map.get(key);
    for(let i=0; i<inputs.length; i++ )
    {
        if (value == inputs[i])
        {
            return outputs[i];
        } 
    }
    return outputs[inputs.length];
}
async function ParseSearchParams()
{
    // Address of the current window
    let address = window.location.search;
    let parameterList = new URLSearchParams(address);
    let map = new Map()

    // Store every key value pair in the map
    parameterList.forEach((value,key) => {
        map.set(key,value);
    });
    
    // Active search parameters
    SearchParameters = 
    {
        "PermissionLevel" : SearchMap(map, 'mode', 
                                ["author",  "3","editor","2"],
                                [3,3,2,2,1]),
        "DoAnnouncements" : SearchMap(map, 'intro',
                                ["false","skip"],
                                [false,false,true]),
        "DoReset"         : SearchMap(map, 'reset',
                                ["true","reset","doreset"],
                                [true,true,true,false]),
        "Story"           : SearchMap(map, 'story',
                                ["Firebrand","firebrand","fb","FB","1","Paragate","paragate","pg","PG","2"],
                                ["Firebrand","Firebrand","Firebrand","Firebrand","Firebrand","Paragate","Paragate","Paragate","Paragate","Paragate","Firebrand"]),
        "ChapterNumber"   : isNaN(parseFloat(map.get("chapter"))) ? undefined : parseFloat(map.get("chapter"))
    }

    return SearchParameters
}

// ----------------------------------------------- //
// Time Handling
// ----------------------------------------------- //

class YearDate 
{
    dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    //
    // DATEYEAR - Return date from YEARDATE.
    //    IN > address - URL of file location, with extension.
    //    OUT> Resulting JSON file.
    //
    get_dateyear(ydate) 
    {
        const year = 2025 + Math.floor(ydate / 365);
        let dayOfYear = ydate % 365;
        if (dayOfYear === 0) dayOfYear = 1;
        const date = new Date(year, 0, dayOfYear);
        
        const dayName = dayNames[date.getDay()];
        const mm = String(date.getMonth() + 1).padStart(2, '0');
        const dd = String(date.getDate()).padStart(2, '0');
        let MMDD = `${mm}/${dd}`;//`${dayName} ${mm}/${dd}`;
        return MMDD;
    }
    //
    // YEARDATE - Return yeardate from a date.
    //    IN > address - URL of file location, with extension.
    //    OUT> Resulting JSON file.
    //
    get_yeardate(date) 
    {
        const month = date.getMonth();
        var result = date.getDate();
        for (let i = 0 ; i < month ; i++) {
            result += new Date(date.getFullYear(),i+1,0).getDate();
        }
        result += (date.getFullYear()-2025)*365;
        return result;
    }
    constructor(day,month,year=2025) {
        if (year === 0) year = 1;
        if(year < 1000) year += 2000;
        if (month==undefined) {
        // Given yeardate, return other date info
            this.ydate      = day;
            this.year       = year + Math.floor(year / 365);
            this.date       = new Date(year, 0, day);
            this.month      = this.date.getMonth();
            this.day        = this.date.getDay();
        } else {
        // Given day, month, year, return yeardate
            if (month > 12) month = 12;
            this.date       = new Date(year, month-1, day);
            this.year       = year;
            this.month      = month;
            this.day        = day;
            this.ydate      = day;
            for (let i = 0 ; i < month ; i++) {
                this.ydate += new Date(this.date.getFullYear(),i+1,0).getDate();
            }
        }
        this.string = {
            "mm"    : String(this.date.getMonth() + 1).padStart(2, '0'),
            "dd"    : String(this.date.getDate()).padStart(2, '0'),
            "YY"    : String(this.year).slice(-2),   
            "YYYY"  : String(this.year),
            "day"   : this.dayNames[this.date.getDay()]
        }
        this.now = this.get_yeardate(new Date());
        this.since = this.now - this.ydate;
    }
}

// ----------------------------------------------- //
// Formatting Data
// ----------------------------------------------- //

//
// NUM2TXT - Return a word representation of a number.
//    IN > Number.
//    OUT> String representation.
//
function Num2txt(number) 
{
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
function InvertIcons() {
    let newstate = (PREFERENCES.DisplayMode=="Dark")?0:1;
    ROOT.style.setProperty("--IconState",`invert(${newstate})`)
    SetMessageState();
}
function SetMessageState() {
    let newstate = (PREFERENCES.DisplayMode=="Dark")?0:1;
    ROOT.style.setProperty("--MsgColorTo",(newstate==0?"rgba(33, 138, 255, 0.8)":"rgba(33, 138, 255, 0.8)"));
    ROOT.style.setProperty("--MsgFontColorTo",(newstate==0?"white":"white"));
    ROOT.style.setProperty("--MsgColorFrom",(newstate==0?"rgba(129, 129, 129, 0.8)":"rgba(215, 215, 215, 0.8)"));//"rgba(216, 216, 216, 0.8)"));
    ROOT.style.setProperty("--MsgFontColorFrom",(newstate==0?"white":"black"));
}
// ----------------------------------------------- //
// Loading In Chapters
// ----------------------------------------------- //
function SetInfo(chapter) {
    eDATA.innerHTML = 
          "<h4 class='InfoTitle'>" + PARAMS.Story + " " + chapter.ID + "</h4><p class='InfoSub'>"
        + chapter.Title + "<br>"
        + chapter.Subtitle + "</p>"
        ; 
}
async function PullChapter(num) {
    // Retrieve the story TOC item with all the chapters.
    let StoryEntry = Object.values(TOC_STORY[PARAMS.Story]['toc']);
    let StoryURL = TOC_STORY[PARAMS.Story]['loc']
    let StoryChapter = StoryEntry[num];
    if(StoryChapter == undefined) StoryChapter = StoryEntry[0];    
    return await GetJSON(StoryURL + StoryChapter.Act + '/' + StoryChapter.ChapterNumber + '.JSON')
}
async function PlaceChapter(chapter) {
    //console.log(chapter)
    let IsFirstScene= true;
    let SceneNum = 0;

    ePAGE.innerHTML = "";
    ePAGE.innerHTML += `<h3 id="title_${chapter.ChapterNumber}" class="${chapter.Perspective} Title">${chapter.Title}</h3>`;
    ePAGE.innerHTML +=`<h3 id="sub_${chapter.ChapterNumber}" class="${chapter.Perspective} Subtitle">${CONFIG.Styles[chapter.Perspective].Prefix + chapter.Subtitle + CONFIG.Styles[chapter.Perspective].Suffix}</h3><br>`;

    if (parseFloat(PARAMS.PermissionLevel) > 1 && (chapter.RevNotes != undefined && chapter.RevNotes != "")) {
        ePAGE.innerHTML +=`<div class="Default TextComment"><h3>Notes To The Editor:</h3><p>${chapter.RevNotes}</p>`;
    }

    chapter.BodyFormatted.forEach( scene => { 
        let Spacer = CONFIG.Styles[chapter.Perspective].Spacer
        if(!IsFirstScene) ePAGE.innerHTML += (Spacer == "") ? 
            `<h3 id="${chapter.ChapterNumber}.${SceneNum++}" class="${chapter.Perspective} Section">${SceneNum}</h3>` : 
            `<img class="hrdiv" src="${Spacer}"/>`;
            IsFirstScene = false;
        scene.forEach( line => {
            ePAGE.innerHTML += line.replaceAll('<p>',`<p class="${chapter.Perspective}">`);
        }); 
    });
    eWINDOW.scrollTop = 0;
    SetScrollerEvents();
}
async function AdvanceChapter(increment) {
    let current_num = ACTIVE_CHAPTER.ChapterNumber - 1;
    if (current_num == undefined || isNaN(current_num)) current_num = 0;
    let query_num = current_num + increment;
    console.log(query_num)
    if(Object.entries(TOC_STORY[PARAMS.Story]['toc']).length >= query_num && query_num >= 0) {
        ACTIVE_CHAPTER = await PlaceOrOverlay(query_num);
    } else {
        return
    }
    return
    }
async function PlaceOrOverlay(num) {
    let BONUS = "";
    let chapter = await PullChapter(num);
    let OverrideContent = CONFIG.ChapterOverrides[PARAMS.Story][chapter.ID];
    if(OverrideContent != undefined) {     
        PREFERENCES.StartChapter = CurrentChapter.ChapterNumber-1;
        BONUS = await GetJSON(OverrideContent);
        ePAGE.innerHTML = `<div class="bonusitem">${BONUS.Content}</div>`
        isScrollerEventPage = false;       
        HandleScrollerEvents(chapter);
        SaveLocalData();
    } else {
        await PlaceChapter(chapter);
        runScrollEvents();
    }    
    ROOT.style.setProperty("--SpecialOp",parseFloat(1*(OverrideContent!= undefined)));
    ACTIVE_CHAPTER = chapter;
    SetInfo(chapter)
    return chapter;
}
async function LoadInChapter(num) {
    ePAGE.innerHTML = "";
    let chapter = await PullChapter(num);
    await PlaceChapter(chapter);
    SetInfo(chapter);  
    PREFERENCES.StartChapter = chapter.ChapterNumber-1;
    SaveLocalData();
    await HandleScrollerEvents(chapter);
    return chapter
}

// ----------------------------------------------- //
// Handling Announcements
// ----------------------------------------------- //
async function LoadAnnouncements(story) {
    eSTARTBOX.style.opacity="1";
    eANNOUNCE.innerHTML = `<div><h3 class="Announcements"> Announcements </h3></div>`;
    Object.entries(CONFIG.Announcements[story]).reverse().forEach( ([timestamp,content]) => {
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

// ----------------------------------------------- //
// Building Table of Contents
// ----------------------------------------------- //
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
function TOChtmlCHAPTER(nChap,name,synopsis,pubdate,nDisplayed,percent,isnew,active) {
    //console.info(MaximumChapter)
    let ChapterInteraction = active?(`class="TOC ChapterRow activerow ${isnew?'newrow':''}"  onclick="PlaceOrOverlay(${nChap-1});ToggleTOC();"`):(`class="TOC ChapterRow inactiverow ${isnew?'newrow':''}"`);

    let result = `    
        <div id="TOC-CH${nChap}" ${ChapterInteraction}> 
            <div id="TOC-CH${nChap}-DATE" class="TOC ChapterDate">${pubdate}</div>
            <div class="TOCmarker" ${active?'style="background-color: rgba(var(--ColorSecondary),1"':''}></div>
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
function AdjustedIndex(index,intro_chapters=0) {
    return (index < intro_chapters) ? 0 : index-intro_chapters;
}
async function BuildTOC() {
    //console.debug("Building the Table Of Contents...");
    eTOC.innerHTML = ''; //TOC clear ------------------------// 

    let today = dSTART.now;
    let startday = dSTART.ydate;
    let releaseday = dCHAPTER.date;
    let lastrelease = releaseday + 0;

    //console.log(`${today}, ${startday}, ${releaseday}`)
    let ChapterMaxNumberT = 0;

    let lastAct = -1;
    let toc = TOC_STORY[PARAMS.Story]['toc'];

    Object.entries(toc).forEach( ([index,chapter]) => {
        if(lastAct != chapter.Act) eTOC.innerHTML += TOChtmlACT(
                                chapter.Act,
                                `Act ${chapter.Act}`
                            );
        lastAct = chapter.Act;
        releaseday = new YearDate(chapter.Release).ydate
        let DatePercentage = (today - startday) / (releaseday - startday);
        DatePercentage = (DatePercentage > 1) ? 1 : (DatePercentage < 0) ? 0 : DatePercentage;
        eTOC.innerHTML += TOChtmlCHAPTER(
                                chapter.ChapterNumber,
                                chapter.Subtitle,
                                chapter.Synopsis,
                                `${chapter.ReleaseDate[0]}/${chapter.ReleaseDate[1]}`,
                                AdjustedIndex(
                                    chapter.ChapterNumber,
                                    CONFIG.Parameters[PARAMS.Story].PrologueChapters
                                ),
                                DatePercentage,
                                ((today >= releaseday)&&(today <= (releaseday+7) )),
                                chapter.Active
                            );

        let VertBar = document.getElementById(`TOC-CH${chapter.ChapterNumber}-STATE`)

        //console.log(`Release #${ChapterMaxNumberT}\n  starts ${startday},\n  now is ${today},\n  ends ${releaseday}\n  percentage ${DatePercentage}.`)
        
        VertBar.style.height = `${DatePercentage * 100}%`;
        VertBar.style.top = `
        ${((-0.5) - ((1-DatePercentage)/2))*100}%`;
        
        startday = releaseday + 0;
        lastrelease = releaseday + 0;
    });
}

// ----------------------------------------------- //
// Handling Information Window
// ----------------------------------------------- //
//
// Functional Variables:
/**/ var isMapZoom = false;
/**/ var InfoWindowState = false;
// Functions:

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
    
    let BONUS = CONFIG.Bonus[PARAMS.Story];
    iMAPCONTENT.innerHTML = BONUS.Maps; // load only once.
    iEXTRAS.innerHTML = BONUS.Other;
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

// ----------------------------------------------- //
// Handling Scrolling Events
// ----------------------------------------------- //
//
// Functional Variables:
/**/ var CHSET = 
        {
            "Text":[],
            "Background":[],
            "ProgressBar":[]
        };   
/**/ var Keyframes = 
    {
        "Text":[],
        "Background":[],
        "ProgressBar":[]
    };
/**/ var MODES = 
    [   'Background',
        'Text',
        'ProgressBar'
    ];
    

/**/ ThisStoryTheme = "Default";
/**/ LastStoryTheme = "Default";
// Functions:
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
    CONFIG.ThemeIndex[PARAMS.Story].forEach( style => {
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
    let Style = CONFIG.Styles["Default"][PREFERENCES.DisplayMode]
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
        //console.log(AllPageElements)
        let StyleOptions = CONFIG.ThemeIndex[PARAMS.Story];
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
    let Style = CONFIG.Styles["Default"][PREFERENCES.DisplayMode]
    DConsole("main.js > SetScrollerEvents",`\t${LastStyle} > ${ThisStyle} @ ${Math.round(Progress*100)/100}%.`,false);
    MODES.forEach( mode  => {
        Keyframes[mode].push([Progress,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], LastStyle+"", ThisStyle+""]);
        let last = CONFIG.Styles[LastStyle][PREFERENCES.DisplayMode][mode]
        let next = CONFIG.Styles[ThisStyle][PREFERENCES.DisplayMode][mode]
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
                    let last = CONFIG.Styles[LastStyle][PREFERENCES.DisplayMode][mode]
                    let next = CONFIG.Styles[ThisStyle][PREFERENCES.DisplayMode][mode]
                    Previous = [last[0],last[1],last[2],last[3]];
                    Next = [next[0],next[1],next[2],next[3]];
                    Event_Switch(Keyframes[mode],Progress,Previous,Next,sTrans2,sHold,-0.5, LastStyle+"", ThisStyle+"");
                });
            }
        }
    }


    // End on neutral theme.
    Progress = 100;
    Style = CONFIG.Styles["Default"][PREFERENCES.DisplayMode]
    DConsole("main.js > SetScrollerEvents",`\t${LastStyle} > ${ThisStyle} @ ${Math.round(Progress*100)/100}%.`,false);
    ThisStyle = "Default";
    MODES.forEach( mode  => {
        let last = CONFIG.Styles[LastStyle][PREFERENCES.DisplayMode][mode]
        let next = CONFIG.Styles[ThisStyle][PREFERENCES.DisplayMode][mode]
        Previous = [last[0],last[1],last[2],last[3]];
        Next = [next[0],next[1],next[2],next[3]];
        Event_Switch(Keyframes[mode],Progress,Previous,Next,2.00,0.00,-2.00, LastStyle+"", ThisStyle+"");
        Keyframes[mode].push([Progress,Style[mode][0],Style[mode][1],Style[mode][2],Style[mode][3], LastStyle+"", ThisStyle+""]);
    });

    //DConsole("main.js > SetScrollerEvents",PageElements,true,true);
   
    //--console.log(PageElementList);
    //--console.log(LastStyle)
    //--console.debug(Keyframes)
}
async function HandleScrollerEvents(chapter) {
    let OverrideContent = CONFIG.ChapterOverrides[PARAMS.Story][chapter.ID];
    let IsOverride = !(OverrideContent == undefined);
    if (!IsOverride) {
        SetScrollerEvents(IsOverride);
        runScrollEvents();
    } else {
        SetDefaultScroller();
        runScrollEvents();
    }
    SetInfo(chapter);
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

        if(ThisStoryTheme != LastStoryTheme) {
            DConsole("main.js > ChannelSet",`Transitioning from ${LastStoryTheme} to ${ThisStoryTheme}.`,true)
        }
        
    }
    
    LastStoryTheme = ThisStoryTheme + "";


    return [RED,GRN,BLU,ALP];
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

    let PageTop = PageRect.top;
    let PageBottom = PageRect.bottom;
    let ItemTop = ItemRect.top;

    let Rel = ItemTop - PageTop
    let Perc = Rel / (PageBottom - PageTop);
    let ScrollPos = Math.round(Perc*100);

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
    console.log(CHSET)
}
function runScrollEvents() {
    Position = ScrollPosition(ePAGE);
    ePROGRESS.style.width = `${Position}%`;  
    MODES.forEach( mode => {
        CHSET[mode] = ChannelSet(Keyframes[mode])
    })
    ApplyColors();    
}

// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- //
// Main Initialization Code
// =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- //

var STORY_LIST,TOC_STORY,TOC_MASTER,CONFIG,PREFERENCES,SETTINGS,PARAMS,ACTIVE_CHAPTER;
var dSTART,dCHAPTER;
async function init() 
{
    dSTART = new YearDate(14,3,25);
    
    // Get the master table of contents.
    TOC_MASTER = await GetJSON(`${URL_ROOT}/story/process/MasterTOC.JSON`);    
    // Return a list of all existing stories from master TOC.
    STORY_LIST = [];
    TOC_MASTER.forEach(entry => {
        if( !STORY_LIST.includes(entry.Story)) 
        {
            STORY_LIST.push(entry.Story);
        }
    });
    // Return a dictionary of TOCs for each story.
    TOC_STORY = {};
    for (let i=0; i<STORY_LIST.length; i++) {
        let storyname = STORY_LIST[i]
        let location =  `${URL_ROOT}/story/process/${storyname}/`;
        let storyTOC = await GetJSON(`${URL_ROOT}/story/process/${storyname}/TOC.JSON`);
        TOC_STORY[storyname] = {};
        TOC_STORY[storyname]['toc'] = storyTOC;
        TOC_STORY[storyname]['loc'] = location;
    }

    // Retrieve configuration parameters.
    CONFIG = await GetJSON(`${URL_ROOT}/config.json`);

    // Retrieve preferences and settings if in Local Storage, otherwise apply defaults.
    let local = await RetrieveLocalData(CONFIG);
    PREFERENCES = local[0];
    SETTINGS = local[1];
    ROOT.style.setProperty("--TextSize",PREFERENCES.FontSize);
    ROOT.style.setProperty("--TextLineHeight",PREFERENCES.LineHeight);
    ROOT.style.setProperty("--TextMargin",PREFERENCES.Margins); 

    // Retrieve the first chapter to be read, depending on URL params and previous data.
    PARAMS = await ParseSearchParams();
    if (PARAMS.ChapterNumber != undefined) PREFERENCES.StartChapter = PARAMS.ChapterNumber;
    ACTIVE_CHAPTER = await PlaceOrOverlay(PREFERENCES.StartChapter);

    dCHAPTER = new YearDate(ACTIVE_CHAPTER.Release);

    // If announcements are active, load announcements.
    if (PARAMS.DoAnnouncements) { 
        DConsole("main.js > setup","Loading announcements.", true)
        await LoadAnnouncements(PARAMS.Story); 
    } else {        
        eSTARTBOX.outerHTML = "";
        DConsole("main.js > setup","Skipping announcements.", true)
    }
    
    ROOT.style.setProperty("--IconState",`invert(${PREFERENCES.DisplayMode})`)

    HandleScrollerEvents(ACTIVE_CHAPTER);
    SetScrollerEvents();
    runScrollEvents();

    await BuildTOC();

    console.log(STORY_LIST,TOC_STORY,TOC_MASTER,CONFIG,PREFERENCES,SETTINGS,PARAMS)
    return
}