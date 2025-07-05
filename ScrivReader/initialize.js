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

const StyleSource   = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/FullReader/config.json";
const StorySource   = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/master/WebnovelReader/docs/PG05.json";

var MODES = ['Background','Text','ProgressBar'];
    var jSTYLES = `{ 
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
        }}`;
    var STYLES = ParseJSON(jSTYLES);

    var PreferencesDefault = {
        "StartChapter":1,
        "DisplayMode":"Light",
        "FontSize":"1.5em",
        "LineHeight":"1.5em",
        "Margins": "5vw"
    }
    var Preferences = PreferencesDefault;
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
    var Settings = SettingsDefault;

    ROOT.style.setProperty("--TextSize",Preferences.FontSize);
    ROOT.style.setProperty("--TextLineHeight",Preferences.LineHeight);
    ROOT.style.setProperty("--TextMargin",Preferences.Margins);
    
    var CHSET = {
        "Text":[],
        "Background":[],
        "ProgressBar":[]
    };   

    var Keyframes = {
        "Text":[],
        "Background":[],
        "ProgressBar":[]
    };

    var NewAnnouncements = {};
    var RevisionNotesList = {};

async function GetCustomParameters() {
    jSOURCE = await GetJSONFromSource('StoryConfig.json');
    SOURCE = ParseJSON(jSOURCE);
}

GetCustomParameters();