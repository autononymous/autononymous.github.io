
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

var isTOCshown = true;


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
    console.log(chapter)
    chapter.BodyFormatted.forEach( scene => { scene.forEach( line => {
        ePAGE.innerHTML += line.replaceAll('<p>',`<p class="${chapter.Perspective}">`);
    }); });
}
async function LoadInChapter(num) {
    let chapter = await PullChapter(num);
    await PlaceChapter(chapter);
    SetInfo(chapter);  
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
function TOChtmlCHAPTER(nChap,name,synopsis,pubdate,nDisplayed,percent,isnew) {
    //console.info(`${nChap},${name},${synopsis},${pubdate},${nDisplayed},${percent},${isnew}`)
    ChapterIsActive = (nChap <= MaximumChapter);
    //console.info(MaximumChapter)
    let ChapterInteraction = ChapterIsActive?(`class="TOC ChapterRow activerow ${isnew?'newrow':''}"  onclick="CurrentChapter=STORY[${nChap-1}];PlaceOrOverlay(CurrentChapter);SaveState();ToggleTOC();"`):(`class="TOC ChapterRow inactiverow ${isnew?'newrow':''}"`);

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

    let RelDate = dSTART.date;
    let today = dSTART.now;
    let startday = dSTART.ydate;
    let releaseday = dCHAPTER.date;
    let lastrelease = releaseday + 0;

    //console.log(`${today}, ${startday}, ${releaseday}`)
    let ChapterMaxNumberT = 0;
      
    let ActCtr = 0;  

    let statChapterTypes = [0,0,0,0];
    let statReleaseDay = [];

    Object.entries(TOC_STORY[PARAMS.Story]['toc']).forEach( ([index,chapter]) => {

    });

    /*
    
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
    /**/
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
    ACTIVE_CHAPTER = await LoadInChapter(PREFERENCES.StartChapter);

    dCHAPTER = new YearDate(ACTIVE_CHAPTER.Release)

    // If announcements are active, load announcements.
    if (PARAMS.DoAnnouncements) { 
        DConsole("main.js > setup","Loading announcements.", true)
        await LoadAnnouncements(PARAMS.Story); 
    } else {        
        eSTARTBOX.outerHTML = "";
        DConsole("main.js > setup","Skipping announcements.", true)
    }

    await BuildTOC();

    console.log(STORY_LIST,TOC_STORY,TOC_MASTER,CONFIG,PREFERENCES,SETTINGS,PARAMS)
    return
}