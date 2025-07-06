
const StyleSource   = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/FullReader/config.json";
const StorySource   = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/master/WebnovelReader/docs/PG05.json";

var STYLE;
var STORY;

function yeardate(date) {
    const month = date.getMonth();
    var result = date.getDate();
    for (let i = 0 ; i < month ; i++) {
        result += new Date(date.getFullYear(),i+1,0).getDate();
    }
    result += (date.getFullYear()-2025)*365;
    return result;
}

// Time-related variables
const tSTART = new Date("2025-03-14T00:00:00Z");
const dSTART = yeardate(tSTART);
const tNOW = new Date();
const dNOW = yeardate(tNOW);

// Defining current chapters
var ActiveChapters = 0;
var TotalChapters = 0;
var CurrentChapter = { Number:7, Content:"" };

// Definition of HTML locations by ID
const ROOT = document.querySelector(':root');
const eREADER = document.getElementById('iCONTENT');
const eHEAD = document.getElementsByTagName('head')[0];
const eSCRLBOX = document.getElementById('SCROLLBOX');

// Control Variables
var ScrollProgress = 0;

//==================={ Saving and Loading Functions }=====================//

function clearLocalStorage() {
    localStorage.removeItem('SW_SAVE');
    localStorage.removeItem('SW_SETTINGS');
    localStorage.removeItem('SW_PREFS');
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
async function main()
{
    STYLE = await GetJSONFromSource(StyleSource);
    GenerateStyles();
    STORY = await GetJSONFromSource(StorySource);
    STORY.Style = STYLE.Styles;
    ParseStory();
    CurrentChapter.Content = STORY.Chapters[CurrentChapter.Number];
    console.debug(CurrentChapter);
    PlaceChapter();
    eREADER.addEventListener('scroll',runScrollEvents);
}

function ComposeScene(raw,perspective) {
    let scene = raw.replaceAll('<p>','\n').replaceAll('</p>','').split('\n');
    let result = [];
    scene.forEach(line => {
        result.push([perspective, line])
    });
    return result;
}

function SetPreferences(property,increment) {
    let Params = STYLE.Settings[property];
    let range = [ 0 , Params.Options.length ];
    let current = Params.Setting;
    let queried = current + increment;

    if (queried >= range[0] && queried < range[1]) {
        Params.Setting = queried;
        STYLE.Preferences[property] = Params.Options[queried];
        ROOT.style.setProperty(Params.CSSname,STYLE.Preferences[property])
        console.info(` > Parameter '${property}' is now set to ${STYLE.Preferences[property]}.`)
    } else {
        console.warn(` > Parameter setting for '${property}' is out of bounds [${range[0]},${range[1]}].`)
    }
}
function InvertIcons() {
    let newstate = (STYLE.Preferences.DisplayMode=="Dark")?0:1;
    ROOT.style.setProperty("--InversionState",`invert(${newstate})`)
}

// | FUNCTION ParseStory
// |  PURPOSE To take the raw story JSON data and organize it into chapters.
// |  
function ParseStory() {   

    // Create an empty "Chapters" array inside STORY for the story content.
    STORY.Chapters = [];

    // Return the Manuscript as an array of entries.
    let Manuscript = Object.values(STORY.Manuscript);
    let eRelease = dSTART;
    let chapct = 0;
    let scenect = 0; // Fills in scene by incrementing. Clears in CHAPTER.

    for (let i=0; i<Manuscript.length; i++) 
    {
        let persp = Manuscript[i].Perspective
        persp = (persp == "Mixed" ? "Default" : persp)
        switch(Manuscript[i].DocType) 
        {
        case "Act":
            break;
        case "Chapter": 
            scenect = 1;
            if (Manuscript[i].PublishOn=="") 
            {
                eRelease += parseFloat(Manuscript[i].NextPublish);
            } else {
                eRelease = parseFloat(Manuscript[i].PublishOn);
            }

            STORY.Chapters.push(
            {
                "Title":Manuscript[i].AutoNameFull,
                "Subtitle":Manuscript[i].GivenName,
                "Act":Manuscript[i].ActNum,
                "ChapterNumber":Manuscript[i].ChapterFull,
                "Synopsis":Manuscript[i].Synopsis,
                "ID":(Manuscript[i].VerboseOverride==undefined)?(Manuscript[i].ActNum-1+"."+Manuscript[i].ChapterFull):Manuscript[i].VerboseOverride,
                "Body":[],
                "Release":eRelease,
                "Active":eRelease<=dNOW,
                "Perspective":Manuscript[i].Perspective,
                "ChapterStyle":STORY.Style[Manuscript[i].Perspective],
                "Previous":"",
                "Next":""
            });

            STORY.Chapters[STORY.Chapters.length-1].Body.push([[persp,`<h3 id="title_${Manuscript[i].ChapterFull}" class="${Manuscript[i].Perspective}Header HEADER">${Manuscript[i].AutoNameFull}</h3>`]]);
            STORY.Chapters[STORY.Chapters.length-1].Body.push([[persp,`<h3 id="sub_${Manuscript[i].ChapterFull}" class="${Manuscript[i].Perspective}Header SUBHEADER">${Manuscript[i].GivenName}</h3>`]]);
    
            if(eRelease <= dNOW) {
                ActiveChapters++;
            }
            TotalChapters++;
            break;
        case "Scene":
            if(eRelease <= dNOW) {
                STORY.Chapters[STORY.Chapters.length-1].Body.push([[persp,`<h3 id="sec_${scenect}" class="${persp}Section SECTION">${STORY.Style[persp].Prefix} ${scenect++} ${STORY.Style[persp].Suffix}</h3>`]]);
                STORY.Chapters[STORY.Chapters.length-1].Body.push(ComposeScene(Manuscript[i].Body,persp));
            }
            break;
        default:
            break;
        }
    }
    for (let i=0; i<STORY.Chapters.length; i++) {
        STORY.Chapters[i].Previous = ( STORY.Chapters[i-1]==undefined ) ? STORY.Chapters[STORY.Chapters.length-1] : STORY.Chapters[i-1];
        STORY.Chapters[i].Next     = ( STORY.Chapters[i+1]==undefined ) ? STORY.Chapters[0] : STORY.Chapters[i+1];
    }    

    console.debug(`Content contains ${TotalChapters} total chapters and ${ActiveChapters} active chapters.`)
}
function PlaceChapter() {
    console.debug(CurrentChapter.Content.Body)
    eSCRLBOX.innerHTML = "";
    let newHTML = ""
    CurrentChapter.Content.Body.forEach(scene => {
        scene.forEach( paragraph => {
            if(paragraph[1] != "") {      
                console.log("pg",paragraph)      
                newHTML += `<div class="${paragraph[0]}">`;
                if(paragraph[1][0] == '<') {                
                    newHTML += `${paragraph[1]}`;
                } else {
                    newHTML += `<p class="${paragraph[0]}Body BODY">${paragraph[1]}</p>`;                    
                }            
                newHTML += `</div>`;
            }
        });
    });
    eSCRLBOX.innerHTML = newHTML;
}
function GenerateStyles() {
    var StyleHTML = document.getElementById("ConfigStyles");
    Object.keys(STYLE.Styles).forEach( Name => {
        let Content = STYLE.Styles[Name];
        StyleHTML.innerHTML +=
`
h3.${Name}Header {
    font-family: ${Content.Header.Font};
    font-weight: ${Content.Header.Weight};
}
h3.${Name}Section {
    font-family: ${Content.Section.Font};
    font-weight: ${Content.Section.Weight};
}
p.${Name}Body {
    font-family: ${Content.Body.Font};
    font-weight: ${Content.Body.Weight};
}
`
    });
    document.head.appendChild(StyleHTML);
}

function runScrollEvents() {
    let ContentRect = document.getElementById('SCROLLBOX').getBoundingClientRect();
    let HeightOffset = eREADER.getBoundingClientRect()
    //console.warn(HeightOffset.y,HeightOffset.height,ContentRect.height,ContentRect.y)
    ScrollProgress = -(ContentRect.y-HeightOffset.y)/(ContentRect.height-HeightOffset.height);
    ScrollProgress = (ScrollProgress > 1) ? 1 : (ScrollProgress < 0) ? 0 : ScrollProgress;
}