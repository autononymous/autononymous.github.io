const StyleSource   = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/ScrivReader/";
var DebugItems = [];
var fname = "initialize.js";
var ActiveStory = "";
var SrcParams = [];

function clearLocalStorage() {
    localStorage.removeItem(`AC_SAVE_${StoryMode}`);
    localStorage.removeItem(`AC_SETTINGS_${StoryMode}`);
    localStorage.removeItem(`AC_PREFS_${StoryMode}`);
}

function DConsole(title,body,flush=false) {
    DebugItems.push(body);
    let DebugStr = "";
    if(flush == true) {
        DebugStr += `From ${title}:\n`;        
        DebugItems.forEach ( message => {
            DebugStr +=  `> ${message}\n`
        })
        console.debug(DebugStr);
        DebugItems = [];
    }
    
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

async function GetJSONFromSource(location)
{
    try {
        const response = await fetch(location);
        if (!response.ok) {
            console.error("Error pulling JSON item.")
        }
        let data = await response.text();
        let result = JSON.parse(data.replaceAll(/(\r\n|\n|\r)/gm, ''));
        //console.debug("Fetched JSON item.")
        return result;
    } catch (error) {
        console.error("Error processing JSON item from URL.")
    }
}
function ParseJSON(source) {
    return JSON.parse(source.replaceAll(/(\r\n|\n|\r)/gm, ''));
}

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
            "CoverImage":"",
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
            "StoryFile":"",
            "StoryName":"ScrivStory",
            "CoverImage":"",
            "WallImage":""
        }
    }

async function GetCustomParams() 
{
    SOURCE = await GetJSONFromSource(StyleSource + "/StoryConfig.json");

    STYLES = SOURCE.Styles; DConsole(fname,"Loaded styles from JSON.");
    PREFS = SOURCE.Preferences; DConsole(fname,"Loaded preferences from JSON.");
    SETTINGS = SOURCE.Settings; DConsole(fname,"Loaded settings from JSON.");
    ANNOUNCE = SOURCE.Announcements; DConsole(fname,"Loaded announcements from JSON.");
    REVNOTES = SOURCE.RevisionNotes; DConsole(fname,"Loaded revision notes from JSON.");
    LOCATIONS = SOURCE.Locations; DConsole(fname,"Loaded revision notes from JSON.",true);
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

    PermissionLevel = 1;
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

    ActiveStory = LOCATIONS[SrcParams.get('story')]
    
    console.log(ActiveStory)
    /*
    SourceROOT  = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/master/WebnovelReader/"
    var StoryName = "";
    var isTOCshown = false;
    let FILEname = "";
    switch (StoryMode) {
    case "1"||"Firebrand":
        FILEname = "/docs/FB04.json";
        StoryName = "Firebrand";
        eBOOKCOVER.src = STYLES.Titus.CoverImage;
        ROOT.style.setProperty('--CoverGradient','var(--CoverFirebrand)')
        break;   
    case "2"||"Paragate": 
    default:
        FILEname = "/docs/PG05.json";
        StoryName = "Paragate";
        eBOOKCOVER.src = STYLES.Cody.CoverImage;
        ROOT.style.setProperty('--CoverGradient','var(--CoverParagate)')
        break;
    }
    */
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


var PermissionLevel = 1;
initialization();

