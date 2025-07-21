
// FUNDAMENTAL DATA LOCATIONS:

// Root location of all files...
const URL_ROOT = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/ScrivenerReader/";






// ----------------------------------------------- //
// Internal/Meta Functions
// ----------------------------------------------- //

function CLS() 
{
    localStorage.removeItem(`AC_SAVE_${StoryMode}`);
    localStorage.removeItem(`AC_SETTINGS_${StoryMode}`);
    localStorage.removeItem(`AC_PREFS_${StoryMode}`);
}

//
// DCONSOLE - Gathers data and prints for debug.
//    IN > title - Title of console entry.
//    IN > body - Line of text to print.
//    IN > flush - Print all saved to display.
//    IN > rawpush - Push raw item such as an object.
//
class DebugConsole
{
    DebugItems = [];
    
    DConsole(title,body,flush=false,rawpush=false) 
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
    constructor(){
        pass
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
// Gathering Data From Defined Sources
// ----------------------------------------------- //


var STORY_LIST,TOC_STORY,TOC_MASTER,CONFIG;
async function init() 
{
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

    CONFIG = await GetJSON(`${URL_ROOT}/config.JSON`);


    return
}

// Release date of Autononymous website.
const dSTART = new YearDate(14,3,25);
init();

console.log(STORY_LIST,TOC_STORY,TOC_MASTER,CONFIG)

