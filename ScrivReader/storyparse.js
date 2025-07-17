
var PrologueChapters = 1; // Number of prologue chapters present in manuscript.
var STORY = [];

// Message correlations.
const MsgMatch = {
    "Miguel":"Miguel",
    "Cody":"Cody",
    "Kei":"Kei",
    "SAKURA":"Kei",
    "DUNSMO":"Cody",
    "BROD":"Reed",
    "Katiya":"Katiya"
}

async function fetchJSON(ForLoc) {

    try {
        let sourcelocation = ForLoc.StoryRoot + ForLoc.StoryFile;
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
            let eRevisionNotes = (entry.RevisionNotes!=true)?((REVNOTES[ActiveStory][eID]==undefined)?undefined:REVNOTES[ActiveStory][eID]):entry.RevisionNotes;
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
                "Story":ActiveStory,
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