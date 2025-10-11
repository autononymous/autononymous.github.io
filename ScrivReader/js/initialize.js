// Global Variables from Initialization
// --File Name
// --Directory containing all files
    var ScrivReaderSOURCE = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/ScrivReader/";
// -- 

// Initialization Variables
    var DebugItems = [];
    var ActiveStory = "";
    var SrcParams = null;
    var LOCATION;
    var PermissionLevel = 1;
    var isTOCshown = false;
    var DoAnnouncements = true;
    var SOURCE;

    const DoSettingTags = false;
    const DoDivsForNumbers = true;

// Main Variables
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

    var InfoWindowState = false;
    var isMapZoom = false;

    var ShownCover = 1;

    ThisStoryTheme = "Default"
    LastStoryTheme = "Default"

    var CODY_Opacity    = 0.00;
    var KAT_Opacity     = 0.00;
    var TIE_Opacity     = 0.00;

    var isScrollerEventPage = false;
   

const VersionLog = {
    "v1.00":"Reader alpha",
    "v2.00":"Reader beta",
    "v2.10":"Add version counter; fix story tag detection",
    "v2.20":"Bonus content window added.",
    "v2.23":"Minor fixes to new info window.",
    "v2.30":"Completion of Paragate introduction with theming.",
    "v2.31":"Capacity for custom scene numbering.",
    "v2.32":"Setting callouts option and custom -hr- dividers.",
    "v2.40":"More debug information for author and reviewer.",
    "v3.00":"Major changes to structure of Paragate."
}

function dateyear(ydate) {
    const year = 2025 + Math.floor(ydate / 365);
    let dayOfYear = ydate % 365;
    if (dayOfYear === 0) dayOfYear = 1;
    const date = new Date(year, 0, dayOfYear);
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const dayName = dayNames[date.getDay()];
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    let MMDD = `${mm}/${dd}`;//`${dayName} ${mm}/${dd}`;
    return MMDD;
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
DATEKEY = "Tuesday, May 13, 2025"; // Start date from Autononymous release day on March 14, 2025.
const tSTART = new Date("2025-03-14T00:00:00Z"); 
const dBEGIN = 56; //Story release relative date.
const dSTART = yeardate(tSTART);    
const tNOW = new Date(); // Current date.
const dNOW = yeardate(tNOW);

DConsole("main.js",`Designated start yeardate is ${dSTART} (${tSTART.toDateString()}).`,false);
DConsole("main.js",`Today's yeardate is ${dNOW} (${tNOW.toDateString()}).`,false);
DConsole("main.js",`Today is ${dNOW-dSTART} days after start yeardate.`,true)

function clearLocalStorage() {
    localStorage.removeItem(`AC_SAVE_${StoryMode}`);
    localStorage.removeItem(`AC_SETTINGS_${StoryMode}`);
    localStorage.removeItem(`AC_PREFS_${StoryMode}`);
}

function DConsole(title,body,flush=false,rawpush=false) {
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

async function GetJSONFromSource(location)
{
    try {
        const response = await fetch(location);
        if (!response.ok) {
            DConsole("initialize.js > GetJSONFromSource","Error pulling JSON item.")
        }
        let data = await response.text();
        let result = JSON.parse(data.replaceAll(/(\r\n|\n|\r)/gm, ''));
        //console.debug("Fetched JSON item.")
        return result;
    } catch (error) {
        DConsole("initialize.js > GetJSONFromSource","Error processing JSON item from URL.")
    }
}
function ParseJSON(source) {
    return JSON.parse(source.replaceAll(/(\r\n|\n|\r)/gm, ''));
}

var CH_OVERRIDES = {};

var BONUS = {};

var THEMEINDEX = {
    "Firebrand":  [ "Titus" ],
    "Paragate":   [ "Katiya" , "Cody" ]
};

var MODES = ['Background','Text','ProgressBar'];
var STYLES = { 
    "Default":
    {
        "Light":
        {
            "Background":[240,240,240,1],
            "Text": [18 ,18 ,18 ,1],
            "ProgressBar": [18 ,18 ,18 ,1]
        },
        "Dark":
        {
            "Background":[18 ,18 ,18 ,1],
            "Text": [240,240,240,1],
            "ProgressBar":[240,240,240,1]
        },
        "Prefix":" ~ ",
        "Suffix":" ~ ",
        "WallImage":""
    }};

var PreferencesDefault = {
    "StartChapter":1,
    "DisplayMode":"Light",
    "FontSize":"1.5em",
    "LineHeight":"1.5em",
    "Margins": "5vw"
}
var PREFS = PreferencesDefault;
var SettingsDefault = {
    "FontSize":{
        "Setting":3,
        "Options":["0.9em","1.1em","1.3em","1.5em","1.7em","1.9em","2.1em"],
        "CSSname":"--TextSize"
    },
    "LineHeight":{
        "Setting":3,
        "Options":["0.9em","1.1em","1.3em","1.5em","1.7em","1.9em","2.1em"],
        "CSSname":"--TextLineHeight"
    },
    "Margins":{
        "Setting":1,
        "Options":["5vw","10vw","15vw"],
        "CSSname":"--TextMargin"
    }
}
var SETTINGS = SettingsDefault;

ROOT.style.setProperty("--TextSize",PREFS.FontSize);
ROOT.style.setProperty("--TextLineHeight",PREFS.LineHeight);
ROOT.style.setProperty("--TextMargin",PREFS.Margins);

var CHSET = 
{
    "Text":[],
    "Background":[],
    "ProgressBar":[]
};   

var Keyframes = 
{
    "Text":[],
    "Background":[],
    "ProgressBar":[]
};

var ANNOUNCE = {};
var REVNOTES = {};

var LOCATIONS = 
{
    "Default":
    {
        "StoryRoot":"",
        "StoryFile":"",
        "StoryName":"ScrivStory",
        "CoverImage":""
    }
}

async function GetCustomParams() 
{
    SOURCE = await GetJSONFromSource(ScrivReaderSOURCE + "/StoryConfig.json");

    THEMEINDEX = SOURCE.ThemeIndex; DConsole("initialize.js > GetCustomParams","Loaded theme indices from JSON.");
    Object.entries(THEMEINDEX).forEach( ([themeName, themeStyles]) => {
        if (!themeStyles.includes("Default")) {
            themeStyles.push("Default");
        }
    })
    BONUS = SOURCE.Bonus; DConsole("initialize.js > GetCustomParams","Loaded bonus window content from JSON.");
    STYLES = SOURCE.Styles; DConsole("initialize.js > GetCustomParams","Loaded styles from JSON.");
    PREFS = SOURCE.Preferences; DConsole("initialize.js > GetCustomParams","Loaded preferences from JSON.");
    SETTINGS = SOURCE.Settings; DConsole("initialize.js > GetCustomParams","Loaded settings from JSON.");
    ANNOUNCE = SOURCE.Announcements; DConsole("initialize.js > GetCustomParams","Loaded announcements from JSON.");
    REVNOTES = SOURCE.RevisionNotes; DConsole("initialize.js > GetCustomParams","Loaded revision notes from JSON.");
    LOCATIONS = SOURCE.Locations; DConsole("initialize.js > GetCustomParams","Loaded locations from JSON.",false);
    CH_OVERRIDES = SOURCE.ChapterOverrides; DConsole("initialize.js > GetCustomParams","Loaded special chapter overrides from JSON.",true);

    if( SrcParams != null ) {
        switch (SrcParams.get('story')) {
            case 1:
            case "firebrand":
            case "Firebrand":
                ActiveStory = "Firebrand";
                break;
            case 2:
            case "paragate":
            case "Paragate":
                ActiveStory = "Paragate";
                break;
            default:
                ActiveStory = "Firebrand";
                break;                    
        }
    } else {
        ActiveStory = "Firebrand"
    }

    DConsole("initialize.js > GetCustomParams",`Selected story is ${ActiveStory}. Pulling data from file ${LOCATIONS[ActiveStory].StoryFile} ...`,true);

    LOCATION = (LOCATIONS[ActiveStory] == undefined) ? Object.entries(LOCATIONS)[0] : LOCATIONS[ActiveStory] ;   
    ActiveStory = LOCATION.StoryName;
    if( INITMODE == "READER")
    {
        eBOOKCOVER.src = LOCATION.CoverImage;
    }
    Object.keys(STYLES).forEach( charstyle => {
        ROOT.style.setProperty(`url(--Wall${charstyle})`, STYLES[charstyle].WallImage);
    })
    ROOT.style.setProperty('--CoverGradient',`var(--Cover${ActiveStory})`)
}
async function ParseSearchParams() 
{
    getParameters = () => {        
        // Address of the current window
        address = window.location.search                
        parameterList = new URLSearchParams(address)    // Returns a URLSearchParams object instance
        let map = new Map()                             // Created a map which holds key value pairs

        // Storing every key value pair in the map
        parameterList.forEach((value, key) => {
            map.set(key, value)
        })

        // Returning the map of GET parameters
        return map
    }
    SrcParams = getParameters();

    PermissionLevel = 0;
    switch (SrcParams.get('mode')) {
    case "author":
    case "3":
        PermissionLevel = 3;
        break;
    case "editor":
    case "2":
        PermissionLevel = 2;
        break;
    default:
        break;
    }    

    switch (SrcParams.get('docover')) {
    case "0":
    case "false":
    case false:
        DoAnnouncements = false;
        break;
    default:
        break;
    }

    if (SrcParams.get('reset')=="DoReset") {
        clearLocalStorage();
        console.warn(`Notice: Local storage was reset for ${StoryName}.`)
    }
}

async function initialization() {
    await ParseSearchParams();
    await GetCustomParams();
    ROOT.style.setProperty("--TextSize",PREFS.FontSize);
    ROOT.style.setProperty("--TextLineHeight",PREFS.LineHeight);
    ROOT.style.setProperty("--TextMargin",PREFS.Margins); 
}

