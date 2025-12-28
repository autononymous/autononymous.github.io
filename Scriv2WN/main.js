"use strict";
// Future Michael:
// I spent a lot of time commenting this shit so you don't have to do 
// it a third time. I even used that Undertale font you like. Just 
// modify what exists.
// - Michael
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
//
//  ████▄  ▄████▄ ██████ ▄████▄   ██  ██ ▄████▄ ███  ██ ████▄  ██     ██ ███  ██  ▄████  
//  ██  ██ ██▄▄██   ██   ██▄▄██   ██████ ██▄▄██ ██ ▀▄██ ██  ██ ██     ██ ██ ▀▄██ ██  ▄▄▄ 
//  ████▀  ██  ██   ██   ██  ██   ██  ██ ██  ██ ██   ██ ████▀  ██████ ██ ██   ██  ▀███▀  
//  
class StoryExtrasWindow {
    constructor(storyName, rootURL, containerID) {
        this.Story = null;
        this.Container = null;
        this.rootURL = "";
        this.Content = "";
        this.Announcements = null;
        this.AnnounceContainer = null;
        this.AnnounceJSON = null;
        this.CoverContainer = null;
        this.Story = storyName;
        this.rootURL = rootURL;
        this.Container = document.getElementById(containerID);
        this.AnnounceContainer = document.getElementById('ANNOUNCE');
        this.CoverContainer = document.getElementById('BCOVER');
        if (!this.Container) {
            console.warn("StoryExtrasWindow.constructor\n", `Container element with ID "${containerID}" not found.`);
        }
        if (!this.AnnounceContainer) {
            console.warn("StoryExtrasWindow.constructor\n", `Announcement container not found.`);
        }
        if (!this.CoverContainer) {
            console.warn("StoryExtrasWindow.constructor\n", `Cover container not found.`);
        }
    }
    static initialize(storyName, rootURL, containerID) {
        return __awaiter(this, void 0, void 0, function* () {
            return new StoryExtrasWindow(storyName, rootURL, containerID);
        });
    }
    loadInExtras() {
        return __awaiter(this, arguments, void 0, function* (filePath = null) {
            if (!(yield this.loadContent(filePath))) {
                console.error("StoryExtrasWindow.loadInExtras\n", `Error loading content.`);
            }
        });
    }
    loadContent() {
        return __awaiter(this, arguments, void 0, function* (filePath = null) {
            try {
                let url = "";
                if (filePath == null) {
                    url = `${this.rootURL}/extra/extras_${this.Story}.html`;
                }
                else {
                    url = `${this.rootURL}/${filePath}`;
                }
                const response = yield fetch(url);
                if (!response.ok) {
                    console.error("StoryExtrasWindow.loadContent\n", `Error fetching content from ${url}.`);
                    return false;
                }
                this.Content = yield response.text();
                console.log("StoryExtrasWindow.loadContent\n", `Content loaded from ${url}.`);
                return true;
            }
            catch (error) {
                console.error("StoryExtrasWindow.loadContent\n", `Failed to load content: ${error}`);
                return false;
            }
        });
    }
    parseAnnouncements() {
        return __awaiter(this, void 0, void 0, function* () {
            let HTMLannounce = "";
            if (!this.AnnounceJSON) {
                console.error("StoryExtrasWindow.parseAnnouncements\n", `AnnounceJSON does not exist.`);
            }
            else {
                let storyAnnounce = this.AnnounceJSON[`${this.Story}`];
                let announceByDate = {};
                Object.entries(storyAnnounce).reverse().forEach(([k, v]) => {
                    let announceday = (() => {
                        const key = String(k);
                        const dt = new Date(key);
                        if (isNaN(dt.getTime()))
                            return key;
                        return new Intl.DateTimeFormat('en-us', { month: '2-digit', day: '2-digit', year: '2-digit' }).format(dt);
                    })();
                    let announceTitle = v['title'] ? v['title'] : "";
                    HTMLannounce += `<div class="Announcement">`
                        + `<div class="AnnounceHead">`
                        + `<span class="adate">${announceday}</span>&emsp;<span class="atitle">${announceTitle}</span>`
                        + `</div>`
                        + `<div class="AnnounceBody">`;
                    (v['content']).forEach((line) => {
                        HTMLannounce += `<p class="aline">${line ? line : ""}</p>`;
                    });
                    HTMLannounce += `</div>`
                        + `</div>`;
                });
            }
            return HTMLannounce;
        });
    }
    loadAnnouncements() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                let url = `${this.rootURL}/Announcements.json`;
                const response = yield fetch(url);
                if (!response.ok) {
                    console.error("StoryExtrasWindow.loadContent\n", `Error fetching announcements from ${url}.`);
                    return false;
                }
                this.AnnounceJSON = yield response.json();
                this.Announcements = yield this.parseAnnouncements();
                console.log("StoryExtrasWindow.loadContent\n", `Announcements loaded from ${url}.`, this.Announcements);
                return true;
            }
            catch (error) {
                console.error("StoryExtrasWindow.loadContent\n", `Failed to load announcements: ${error}`);
                return false;
            }
        });
    }
    deployContent() {
        let resultingState = false;
        if (!this.Container) {
            console.warn("StoryExtrasWindow.deployContent\n", "Container element not found.");
        }
        if (!this.Content) {
            console.warn("StoryExtrasWindow.deployContent\n", "No content loaded.");
        }
        if (this.Container && this.Content) {
            this.Container.innerHTML = this.Content;
            resultingState = true;
        }
        if (this.AnnounceContainer) {
            this.AnnounceContainer.innerHTML = this.Announcements;
            this.AnnounceContainer.outerHTML = `<div class="EXwindow" id="EXwindow">`
                + `<div class="TEX_HEAD" id="EXextras">${this.Story} Announcements</div>`
                + `</div>`
                + this.AnnounceContainer.outerHTML;
        }
        else {
            console.error('No announcements.');
        }
        if (this.CoverContainer) {
            let story = "";
            if (this.Story == 'Paragate') {
                story = "PG";
            }
            else if (this.Story == 'Firebrand') {
                story = "FBC";
            }
            this.CoverContainer.innerHTML = `<img
                src="https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN/design/cover-${story}.jpg"
                alt="${this.Story} cover"
                loading="lazy"
                style="display:block;width:min(70%,820px);height:auto;position:relative;left:50%;transform:translateX(-50%);border:2px solid var(--TextColor);box-shadow:0px 0px 10px black;border-radius:6px;"
            >
            <br>`;
        }
        return resultingState;
    }
    deploy(filePath) {
        return __awaiter(this, void 0, void 0, function* () {
            const loaded = yield this.loadContent(filePath);
            if (!loaded)
                return false;
            return this.deployContent();
        });
    }
}
class ControlBar {
    constructor(LocalStorage, DataCard) {
        this.ThemeState = false;
        this.DoJustify = false;
        this.FontSize = {
            "Setting": 3,
            "Options": ["0.9em", "1.1em", "1.3em", "1.5em", "1.7em", "1.9em", "2.1em"],
            "CSSname": "--TextSize"
        };
        this.LineHeight = {
            "Setting": 3,
            "Options": ["0.9em", "1.1em", "1.3em", "1.5em", "1.7em", "1.9em", "2.1em"],
            "CSSname": "--TextLineHeight"
        };
        this.Margins = {
            "Setting": 1,
            "Options": ["5vw", "10vw", "15vw"],
            "CSSname": "--TextMargin"
        };
        this.LocalStorage = LocalStorage;
        this.DataCard = DataCard;
        this.eLineDown = document.getElementById('ICON-LINEDN');
        this.eLineUp = document.getElementById('ICON-LINEUP');
        this.eFontSizeDown = document.getElementById('ICON-FONTUP');
        this.eFontSizeUp = document.getElementById('ICON-FONTUP');
        this.eThemeToggle = document.getElementById('ICON-THEME');
        this.GetAndSet(DataCard, false);
    }
    setter(change, setting) {
        change = Math.round(change);
        change = change >= 1 ? 1 : change <= -1 ? -1 : 0;
        let n_Options = setting.Options.length - 1;
        let newSetting = setting.Setting + change;
        newSetting = newSetting > n_Options ? 0 : newSetting < 0 ? n_Options : newSetting;
        setting.Setting = newSetting;
    }
    setFontSize(change, doReport = true) {
        this.setter(change, this.FontSize);
        ROOT.style.setProperty(this.FontSize.CSSname, this.FontSize.Options[this.FontSize.Setting]);
        this.LocalStorage.Local.fontsetting = this.FontSize.Setting;
        this.LocalStorage.SaveLocalStorage();
        if (doReport) {
            console.log("ControlBar.setFontSize\n", `Parameter ${this.FontSize.CSSname} set to option ${this.FontSize.Setting}, ${this.FontSize.Options[this.FontSize.Setting]}. Local Storage also set to ${this.LocalStorage.Local.fontsetting}.`);
        }
    }
    setLineHeight(change, doReport = true) {
        this.setter(change, this.LineHeight);
        ROOT.style.setProperty(this.LineHeight.CSSname, this.LineHeight.Options[this.LineHeight.Setting]);
        this.LocalStorage.Local.linesetting = this.LineHeight.Setting;
        this.LocalStorage.SaveLocalStorage();
        if (doReport) {
            console.log("ControlBar.setLineHeight\n", `Parameter ${this.LineHeight.CSSname} set to option ${this.LineHeight.Setting}, ${this.LineHeight.Options[this.LineHeight.Setting]}. Local Storage also set to ${this.LocalStorage.Local.linesetting}.`);
        }
    }
    setTheme(datacard, doReport = true) {
        this.ThemeState = !this.ThemeState;
        datacard.toggleNightMode(this.ThemeState, false);
        this.LocalStorage.Local.themesetting = this.ThemeState;
        this.LocalStorage.SaveLocalStorage();
        if (doReport) {
            console.log("ControlBar.setTheme\n", `Night mode is now ${this.ThemeState ? "on/dark" : "off/light"}. Local Storage also set to ${this.LocalStorage.Local.themesetting ? "on" : "off"}.`);
        }
    }
    setJustify(state, doReport = true) {
        this.LocalStorage.Local.dojustify = state;
        this.DoJustify = this.LocalStorage.Local.dojustify;
        this.LocalStorage.SaveLocalStorage();
        ROOT.style.setProperty('--TextAlignment', `${state ? 'Justify' : 'Left'}`);
        if (doReport) {
            console.log("ControlBar.setJustify\n", `Body text alignment is now ${this.DoJustify ? 'Justify' : 'Left'}. Local Storage also set to ${this.LocalStorage.Local.dojustify ? 'Justify' : 'Left'}.`);
        }
    }
    GetAndSet(datacard, doReport = true) {
        this.FontSize.Setting = this.LocalStorage.Local.fontsetting;
        this.LineHeight.Setting = this.LocalStorage.Local.linesetting;
        this.ThemeState = this.LocalStorage.Local.themesetting;
        this.DoJustify = this.LocalStorage.Local.dojustify;
        ROOT.style.setProperty(this.FontSize.CSSname, this.FontSize.Options[this.FontSize.Setting]);
        ROOT.style.setProperty(this.LineHeight.CSSname, this.LineHeight.Options[this.LineHeight.Setting]);
        this.setJustify(this.DoJustify);
        datacard.toggleNightMode(this.ThemeState, false);
    }
}
class LocalStorageAndSrcVars {
    constructor(storyName) {
        //  Search variables take priority over Local Storage.
        this.Parameters = null;
        this.Map = null;
        this.Binder = null;
        this.requestedChapter = null;
        this.hasSearchVars = false;
        this.hasLocalStorage = false;
        this.default = {
            "chapter": 1,
            "permlevel": 0,
            "fontsetting": 3,
            "linesetting": 3,
            "themesetting": true,
            "dojustify": true
        };
        this.Local = Object.assign(this.default);
        this.Map = this.PollSrcVars();
        this.storyName = storyName;
        this.SaveName = `SG_Bookmark_${this.storyName}`;
        let localprefs = localStorage.getItem(this.SaveName);
        if (localprefs) {
            try {
                // Try retrieving preferences from Local Storage.
                // The system initialized with a new copy of the settings.
                this.RetrievedData = JSON.parse(localprefs);
                // If local saved data contains settings, overwrite the copy data.
                Object.entries(this.RetrievedData).forEach(([k, v]) => {
                    if (Object.prototype.hasOwnProperty.call(this.Local, k)) {
                        this.Local[k] = v;
                        //console.info("LSASV.constructor\n", `Restored "${k}" from saved prefs.`);
                    }
                });
                this.hasLocalStorage = true;
                // If there are search variables, these take preference over existing Local Storage settings.
                if (this.ParseSrcVars()) {
                    console.info("LSASV.ParseSrcVars\n", `Setting chapter to ${this.requestedChapter} from search parameter variables in ${this.SaveName}.`);
                    this.Local.chapter = this.requestedChapter;
                    localStorage.setItem(this.SaveName, JSON.stringify(this.Local));
                }
            }
            catch (error) {
                // If there's an error, create a new instance.
                console.error("LSASV.ParseSrcVars\n", `Issue reading LocalStorage save. Creating new save as "${this.SaveName}".`, error);
                localStorage.setItem(this.SaveName, JSON.stringify(this.default));
                let get = localStorage.getItem(this.SaveName);
                this.Local = JSON.parse(get);
            }
        }
        else {
            console.info("LSASV.ParseSrcVars\n", `LocalStorage save does not exist yet. Creating new save as "${this.SaveName}".`);
            localStorage.setItem(this.SaveName, JSON.stringify(this.default));
            let get = localStorage.getItem(this.SaveName);
            this.Local = JSON.parse(get);
        }
        this.StatusReport();
    }
    static initialize(storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            return new LocalStorageAndSrcVars(storyName);
        });
    }
    SaveLocalStorage() {
        localStorage.setItem(this.SaveName, JSON.stringify(this.Local));
        console.log("LSASV.ParseSrcVars\n", "Saved local storage:", this.Local);
    }
    SetSavedChapter(chapter) {
        this.Local.chapter = chapter;
        console.debug("LSASV.SetSavedChapter\n", `Last position saved as ${chapter}.`, this.Local);
        this.SaveLocalStorage();
    }
    PollSrcVars(doReport = true) {
        let address = window.location.search;
        this.Parameters = new URLSearchParams(address);
        let map = new Map();
        this.Parameters.forEach((value, key) => {
            map.set(key, value);
        });
        if (doReport && map.size != 0) {
            //console.debug(`Variables are present in search bar:`,map)
        }
        return map;
    }
    AttachBinder(binder) {
        this.Binder = binder;
        this.Binder.Permissions = this.Local.permlevel;
    }
    ParseSrcVars(doReport = true) {
        if (this.Map == null) {
            console.error("LSASV.ParseSrcVars\n", "Unable to parse: not retrieved yet.");
            return false;
        }
        let doPermissions = false;
        switch (this.Map.get("mode")) {
            case "author":
            case "Author":
                this.Local.permlevel = 2;
                console.debug("LSASV.ParseSrcVars\n", `AUTHOR level set from srcvars at L${this.Local.permlevel}.`);
                doPermissions = true;
                this.hasSearchVars = true;
                break;
            case "editor":
            case "Editor":
            case "Reviewer":
            case "reviewer":
                this.Local.permlevel = 1;
                console.debug("LSASV.ParseSrcVars\n", `REVIEWER level set from srcvars at L${this.Local.permlevel}.`);
                doPermissions = true;
                this.hasSearchVars = true;
                break;
            default:
                break;
        }
        switch (this.Map.get("story")) {
            case "paragate":
            case "Paragate":
            case "2":
                this.storyName = "Paragate";
                console.debug("LSASV.ParseSrcVars\n", "Loading Paragate.");
                this.hasSearchVars = true;
                break;
            case "firebrand":
            case "Firebrand":
            case "1":
                this.storyName = "Firebrand";
                console.debug("LSASV.ParseSrcVars\n", "Loading Firebrand.");
                this.hasSearchVars = true;
                break;
            default:
                this.storyName = "Paragate";
                console.debug("LSASV.ParseSrcVars\n", "No story specified. Loading Paragate as default.");
                break;
        }
        //if (doPermissions) {
        //    BIND.HandlePermissions(true)
        //}
        let doURLchap = isNaN(Number(this.Map.get("chapter")));
        if (!doURLchap) {
            this.requestedChapter = Math.round(Number(this.Map.get("chapter")));
            console.info("LSASV.ParseSrcVars\n", `Chapter specified in URL as ${this.requestedChapter}.`);
            this.hasSearchVars = true;
            return true;
        }
        return false;
    }
    StatusReport() {
        console.info('----==== REPORT FOR LOCAL STORAGE AND SEARCH VARS ====----\n'
            + `\t > Settings retrieved from search? . . . ${this.hasSearchVars}\n`
            + `\t > Variables in Local Storage? . . . . . ${this.hasLocalStorage}\n`
            + `\t > Story to load?  . . . . . . . . . . . ${this.storyName}\n`
            + `Current settings are:\n`, this.Local, `\n\nParameters in search bar:`, this.Parameters);
    }
}
this;
class ChapterDataCard {
    //public eEXTRAHEAD: HTMLElement;
    currentChapter() {
        return this.Data.TOC.Chapter;
    }
    setBinder(binder) {
        // Set the ChapterBinder location: ChapterDataCard is created first.
        this.Binder = binder;
    }
    setThemeDriver(themeDriver) {
        // Set the ThemeDriver location: ChapterDataCard is created first.
        this.ThemeDriver = themeDriver;
    }
    Update(chapterNumber, doReport = false) {
        if (this.Binder == null) {
            console.warn("ChapterDataCard.Update\n", "No ChapterBinder paired to DataCard. Cannot update data.");
            return;
        }
        this.Data.TOC = this.Binder.TOC[chapterNumber - 1];
        this.Data.META = this.Binder.source.list.Metadata;
        // Notify ThemeDriver of chapter change for scroll break recalculation.
        if (this.ThemeDriver != null) {
            this.ThemeDriver.getScrollBreaks();
        }
        if (doReport) {
            console.log(`
            ChapterDataCard.Update Report for ${this.Data.TOC.ChapterNumber}:
            Title: "${this.Data.TOC.ChapterName}"
            Act: ${this.Data.TOC.Act} - "${this.Data.TOC.ActName}"
            Location: ${this.Data.TOC.Location}
            POV for each Scene: [ ${this.Data.TOC.Character} ]
            Summary: "${this.Data.TOC.Summary}"
            Reader Summary: "${this.Data.TOC.Blurb}"
            Written? ${this.Data.TOC.Written}
            `);
        }
        this.updateTOCinfo();
        this.updateDataBar();
        return;
    }
    constructor(StoryName) {
        //  The class ChapterDataCard is an actively-updated class variable that holds 
        //  all relevant information on the current chapter loaded into the Canvas.
        //
        //  ARGUMENTS:
        //    > StoryString - Name of the story as written in Config files and Scrivener export.
        //  
        //  IMPORTANT ELEMENTS:
        //    > Story - Name of story.
        //    > Data - Data structure for current chapter.
        //        .TOC - Chapter information for this specific chapter.
        //            .Act - Current act number.
        //            .ActName - Name of act, e.g. "ACT II"
        //            .Blurb - Spoiler-free description for interest of reader.
        //            .Chapter - Chapter number as NUMBER.
        //            .ChapterName - Name of the chapter.
        //            .ChapterNumber - Chapter number as WORDNUMBER e.g. "Thirty-Two"
        //            .Character[scene_number] - What character POV each scene is.
        //            .Location - Where the scene takes place.
        //            .Summary - Full summary for debug (for author).
        //            .Written - Is it written? BOOLEAN.
        //        .META - Information about entire story.
        //            .ActCount - Total act count.
        //            .ChapterCount - Total chapter count.
        //            .SceneCount - Total scene count.
        //            .Summary - String containing a report on the exported manuscript from Scrivener.
        //            .WrittenCount - Number of written scenes.
        //            .UnwrittenCount - Number of unwritten scenes.
        //
        //  METHODS :
        //    > setBinder
        //        - Pair a ChapterBinder object with the Data Card.
        //    > setThemeDriver 
        //        - Pair a ThemeDriver object with the Data Card.
        //    > Update
        //        - Given a new pulled chapter, update the Data Card. **This depends on ChapterBinder().**
        //
        this.Story = null; // Story name.
        this.Data = { TOC: null, META: null }; // Data structure for current chapter data.
        this.Binder = null; // Pointer to the ChapterBinder object.
        this.ThemeDriver = null; // Pointer to the ThemeDriver object.
        this.NightMode = false; // Is Night Mode active?
        this.CurrentVoice = null;
        this.Story = StoryName;
        this.eTOC_ID = document.getElementById('TTC_ID');
        this.eTOC_NAME = document.getElementById('TTC_name');
        this.eTOC_BLURB = document.getElementById('TTC_blurb');
        //this.eEXTRAHEAD = document.getElementById('EXhead') as HTMLElement;
    }
    updateTOCinfo() {
        let actRoman = { 0: "Prologue", 1: "Act I", 2: "Act II", 3: "Act III", 4: "Act IV" };
        let actnum = Number(this.Data.TOC.Act);
        this.eTOC_ID.innerHTML = `${actRoman[actnum]}, Chapter ${this.Data.TOC.ChapterNumber}`;
        let ChapterView = this.Data.TOC.Character[0];
        this.Data.TOC.Character.forEach((element) => { ChapterView = ChapterView == element ? ChapterView : "Mixed"; console.log(element); });
        this.eTOC_NAME.innerHTML = `${ChapterView} &mdash; <em>${this.Data.TOC.ChapterName}</em>`;
        this.eTOC_BLURB.innerHTML = `<p>"${this.Data.TOC.Blurb}"</p>`;
        //this.eEXTRAHEAD.innerHTML = `${this.Story} Extras`
    }
    toggleNightMode(newState = null, doReport = true) {
        if (newState != null) {
            this.NightMode = newState;
        }
        else {
            this.NightMode = !this.NightMode;
        }
        ROOT.style.setProperty("--IconState", `invert(${Number(!this.NightMode)})`);
        ROOT.style.setProperty("--IconReverse", `invert(${Number(!this.NightMode)})`);
        ROOT.style.setProperty("--BooleanColor", `${this.NightMode ? "white" : "black"}`);
        console.log("ChapterDataCard.toggleNightMode\n", `Night mode is now ${this.NightMode ? "on" : "off"}.`);
        return this.NightMode;
    }
    updateDataBar() {
        eIDCHAPTER.innerHTML = `<span>Chapter ${this.Data.TOC.ChapterNumber}</span>`;
        eIDNAME.innerHTML = `<span>${this.Data.TOC.ChapterName}</span>`;
    }
    lookingAt(LookingAt) {
        // Return if perspective changes, and update active speaker.
        let progress = LookingAt.position;
        let voice = LookingAt.voice;
        let changeEvent = false;
        if (this.CurrentVoice != voice) {
            this.CurrentVoice = voice;
            console.log("ChapterDataCard.lookingAt\n", `Narrative voice is now ${this.CurrentVoice}. Transitioned at ${progress}%.`);
            changeEvent = true;
        }
        return changeEvent;
    }
}
class StoryConfig {
    constructor(cfg, storyName) {
        this.config = cfg;
        this.storyName = storyName;
        this.themes = (this.getAllPossibleThemes());
        return;
    }
    doesThemeExist(characterName, ignoreDefault = false) {
        if (this.themes.includes(characterName) && (!(characterName == "Default" && ignoreDefault))) {
            return true;
        }
        else {
            console.warn("StoryConfig.doesThemeExist\n", `Character ${characterName} is not a theme name, so it is not a POV character.`);
            return false;
        }
    }
    getAllPossibleThemes() {
        return Object.keys(this.config.Styles);
    }
    ThemesInStory() {
        return this.config.ThemeIndex[this.storyName];
    }
    getFullName(characterName) {
        if (!this.doesThemeExist(characterName)) {
            return ["Bobson Dugnutt", "Sleve McDichael", "Anatoli Smorin", "Onson Sweemey", "Tony Smehrik", "Scott Dorque", "Darryl Archideld"][Number((Math.random() * 7).toFixed(0))];
        }
        return this.config["Shorthands"]["Names"][characterName];
    }
    getCharacterStyle(characterName, item) {
        if (!this.doesThemeExist(characterName)) {
            return false;
        }
        else if (!this.config["Styles"][characterName].contains(item)) {
            console.warn("StoryConfig.getCharacterStyle\n", `${item} is not a theme object.`);
            return false;
        }
        return this.config["Styles"][characterName][item];
    }
    static initialize(rootURL, storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * This is the access point for creating a StoryConfig instance.
             * @param rootURL Base URL for fetching resources.
             * StoryConfig.json should be in the root directory.
             * @return Manuscript instance with fetched data.
             */
            const response = yield fetch(`${rootURL}/StoryConfig.json`);
            if (!response.ok) {
                console.error("StoryConfig.initialize\n", "Error fetching config from URL.");
            }
            else {
                console.debug("StoryConfig.initialize\n", `Successfully fetched config from URL at ${rootURL}/StoryConfig.json.`);
            }
            this.data = yield response.json();
            return new StoryConfig(this.data, storyName);
        });
    }
}
class Manuscript {
    constructor(rootURL, storyName, script) {
        /**
         *  @param rootURL Base URL for fetching resources.
         *  @param storyName Name of the story to fetch.
         *  @param script Full unparsed script data.
         */
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.script = script;
    }
    static initialize(rootURL, storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * This is the access point for creating a Manuscript instance.
             * @param rootURL Base URL for fetching resources.
             * @param storyName Name of the story to fetch.
             * @return Manuscript instance with fetched data.
             */
            let sourceURL = `${rootURL}/output/${storyName}/MC_Latest.json`;
            const response = yield fetch(sourceURL);
            if (!response.ok) {
                console.error("Manuscript.initialize\n", "Error fetching manuscript from URL.");
            }
            else {
                console.log("Manuscript.initialize\n", `Successfully fetched manuscript from URL at ${rootURL}/MC_Latest.json.`);
            }
            this.data = yield response.json();
            return new Manuscript(rootURL, storyName, this.data);
        });
    }
}
class TableOfContents {
    constructor(toc) {
        // States of slide panels.
        this.TOCstate = false;
        this.EXTRAstate = false;
        this.CTRLstate = false;
        this.MAPstate = false;
        /**
         * @param toc Full Table Of Contents data.
         */
        this.list = toc;
        this.ToggleDisplay(this.TOCstate);
        this.ToggleInfo(this.EXTRAstate);
        this.ToggleControls(this.CTRLstate);
        this.ToggleMap(this.MAPstate);
        this.TOClocation = document.getElementById("TOCwindow");
        this.DeployTOC();
    }
    static initialize(sourceURL, storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * This is the access point for creating a TableOfContents instance.
             * @param sourceURL URL to fetch the TOC JSON from.
             * @return TableOfContents instance with fetched data.
             */
            const response = yield fetch(sourceURL);
            if (!response.ok) {
                console.error("TableOfContents.initialize\n", "Error fetching manuscript from URL.");
            }
            else {
                console.log("TableOfContents.initialize\n", `Successfully fetched manuscript from URL at ${sourceURL}.`);
            }
            this.data = yield response.json();
            // ....and now initialization of the Table Of Contents panel.
            ROOT.style.setProperty("--TitleImageTOC", `url(../design/${storyName}_logo.png)`);
            ROOT.style.setProperty("--WallImageTOC", `url()`);
            return new TableOfContents(this.data);
        });
    }
    ToggleDisplay(setState = null) {
        if (this.isToggleOkay('TOC')) {
            if (setState == null) {
                this.TOCstate = !this.TOCstate;
            }
            else {
                this.TOCstate = setState;
            }
            console.log("TableOfContents.ToggleDisplay\n", `Table Of Contents is now ${this.TOCstate ? "shown" : "hidden"}.`);
            // Changing width of TOC? Set --TOCWIDTH in contentstyles.css
            ROOT.style.setProperty("--READER_TOCOFFSET", this.TOCstate ? "var(--TOCWIDTH)" : "0px");
        }
    }
    ToggleInfo(setState = null) {
        if (this.isToggleOkay('EXTRA')) {
            if (setState == null) {
                this.EXTRAstate = !this.EXTRAstate;
            }
            else {
                this.EXTRAstate = setState;
            }
            console.log("TableOfContents.ToggleInfo\n", `Special Window is now ${this.EXTRAstate ? "shown" : "hidden"}.`);
            // Changing width of TOC? Set --TOCWIDTH in contentstyles.css
            ROOT.style.setProperty("--READER_EXTRAOFFSET", this.EXTRAstate ? "calc( -1 * var(--EXTRAWIDTH))" : "0px");
        }
    }
    ToggleControls(setState = null) {
        if (this.isToggleOkay('CTRL')) {
            if (setState == null) {
                this.CTRLstate = !this.CTRLstate;
            }
            else {
                this.CTRLstate = setState;
            }
            console.log("TableOfContents.ToggleControls\n", `Special Window is now ${this.CTRLstate ? "shown" : "hidden"}.`);
            // Changing width of TOC? Set --TOCWIDTH in contentstyles.css
            ROOT.style.setProperty("--READER_CTRLOFFSET", this.CTRLstate ? "var(--CTRLWIDTH)" : "0px");
        }
    }
    ToggleMap(setState = null) {
        if (this.isToggleOkay('MAP')) {
            if (setState == null) {
                this.MAPstate = !this.MAPstate;
            }
            else {
                this.MAPstate = setState;
            }
            console.log("TableOfContents.ToggleControls\n", `Special Window is now ${this.MAPstate ? "shown" : "hidden"}.`);
            // Changing width of TOC? Set --TOCWIDTH in contentstyles.css
            ROOT.style.setProperty("--READER_MAPOFFSET", this.MAPstate ? "var(--MAPWIDTH)" : "0px");
        }
    }
    isToggleOkay(mode) {
        let okToDeploy = true;
        let requested = "";
        if ((this.TOCstate) && (mode != "TOC")) {
            okToDeploy = false;
            requested = "TOC";
        }
        if ((this.EXTRAstate) && (mode != "EXTRA")) {
            okToDeploy = false;
            requested = "EXTRA";
        }
        if ((this.CTRLstate) && (mode != "CTRL")) {
            okToDeploy = false;
            requested = "CTRL";
        }
        if ((this.MAPstate) && (mode != "MAP")) {
            okToDeploy = false;
            requested = "MAP";
        }
        if (!okToDeploy) {
            console.error("TableOfContents.isToggleOkay\n", `Unable to activate ${mode} while ${requested} is active.`);
        }
        return okToDeploy;
    }
    DeployTOC() {
        let chapters = this.list.ChapterList;
        let lastAct = 0;
        let TOChtml = "";
        chapters.forEach((chapter) => {
            // Creating act headers
            if (chapter.Act != lastAct) {
                TOChtml += `<div class="TOC-act" id="TOC-A${chapter.Act}">${chapter.ActName}</div>`;
                lastAct = chapter.Act;
            }
            // Creating act entries
            //console.warn(chapter)
            let relID = `${chapter.Act}.${chapter.Chapter}`;
            TOChtml += `            
            <div id="T.${relID}" class="TOC-chapcontainer" onclick="BIND.DeployOnPage(${chapter.Chapter},DEPLOY);SRC.SaveLocalStorage()">
                <div id="num.${relID}" class="TOC-num">${String(chapter.Chapter).padStart(2, '0')}</div>
                <div id="name.${relID}" class="TOC-name">${chapter.ChapterName}</div>
                <div id="blurb.${relID}" class="TOC-blurb">${chapter.Blurb}</div>
                <div id="date.${relID}" class="TOC-date">${chapter.Release}</div>
            </div>`;
        });
        this.TOClocation.innerHTML = TOChtml;
    }
}
//  ▄█████ ██  ██ ▄████▄ █████▄ ██████ ██████ █████▄  ▄█████ 
//  ██     ██████ ██▄▄██ ██▄▄█▀   ██   ██▄▄   ██▄▄██▄ ▀▀▀▄▄▄ 
//  ▀█████ ██  ██ ██  ██ ██       ██   ██▄▄▄▄ ██   ██ █████▀ 
class ChapterBinder {
    LockUp() {
        // Add locked messages.
        this.TOC.forEach((chapter) => {
            let relID = `T.${chapter.Act}.${chapter.Chapter}`;
            if (!chapter.AccessGranted) {
                let elem = document.getElementById(relID);
                elem.style.pointerEvents = 'none';
                elem.childNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        node.classList.add("lockedEntry");
                    }
                });
                elem.innerHTML += `<div class="lockedSel">${chapter.DaysUntil.toFixed(0)}</div>`;
            }
        });
    }
    ToggleStarterTags(setstate = null) {
        if (setstate == null) {
            this.SHOW_STARTER_TAGS = !this.SHOW_STARTER_TAGS;
        }
        else {
            this.SHOW_STARTER_TAGS = setstate;
        }
        ;
        this.DeployOnPage('', DEPLOY);
        //@TODO save into Local Storage the state of this.
        return;
    }
    HandlePermissions(doReport = true) {
        this.ChapterBounds = { active: [], whitelist: [], full: [] };
        // This is where access list is assembled. ***********ACCESS***************
        let lastRelease;
        let today = new Date();
        this.TOC.forEach((chapter) => {
            chapter["AccessGranted"] = false;
            if (chapter.Release) {
                const [month, day, year] = chapter.Release.split('/').map(Number);
                lastRelease = new Date(2000 + year, month - 1, day);
                if ((lastRelease.getTime() > today.getTime()) && (chapter.Chapter != 1)) {
                    //console.log(`Chapter ${chapter.Chapter} not ready by ${lastRelease}`)  
                }
                else {
                    //console.log(`Chapter ${chapter.Chapter} ready for ${lastRelease}`)   
                    this.ChapterBounds.whitelist.push(chapter.Chapter);
                }
            }
            chapter["DaysUntil"] = ((lastRelease.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
            this.ChapterBounds.full.push(chapter.Chapter);
        });
        //console.error(this.source)
        // No hack please!!!
        switch (this.Permissions) {
            case 2: // Admin.
                console.info("ChapterBinder.HandlePermissions\n", "Permissions at ADMIN level.");
                this.ChapterBounds.active = this.ChapterBounds.full;
                break;
            case 1: // Reviewer.
                console.info("ChapterBinder.HandlePermissions\n", "Permissions at REVIEWER level.");
                this.ChapterBounds.active = this.ChapterBounds.full;
                break;
            default: // Base user.
                console.info("ChapterBinder.HandlePermissions\n", "Permissions at GUEST level.");
                this.ChapterBounds.active = this.ChapterBounds.whitelist;
                break;
        }
        this.ChapterBounds.active.forEach((chapnum) => {
            // recall: chapnum vs chapter indexing
            this.TOC[chapnum - 1]["AccessGranted"] = true;
        });
        if (doReport) {
            console.info(`----==== USER ACCESS REPORT (ChapterBinder) ====----\n`
                + ` > Today is ${today.getUTCDate()}.\n`
                + ` > Access level is ${["GUEST", "REVIEWER", "ADMIN"][this.Permissions]} (${this.Permissions}).\n`
                + ` > User has access to: \n`, this.ChapterBounds.active);
        }
    }
    constructor(rootURL, storyName, prgmConfig, source, permissions = 0, dataCard, elementID = "", doDeployment = 1, doReport = true, IncludeSettingTags) {
        this.rootURL = "";
        this.storyName = "";
        this.SessionBinder = {};
        this.Permissions = 0;
        this.lastMessenger = "Anon";
        this.CURRENT_SCENE = [0, 0, 0, 0];
        this.LAST_SCENE = [0, 0, 0, 0];
        this.doSpecificName = false;
        this.MsgMatch = {
            "Miguel": "Miguel",
            "Cody": "Cody",
            "Kei": "Kei",
            "SAKURA": "Kei",
            "DUNSMO": "Cody",
            "BROD": "Reed",
            "Kat": "Katiya",
            "Alan": "Alan",
            "Reed": "Reed"
        };
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.source = source;
        this.TOC = source.list.ChapterList;
        this.Permissions = permissions;
        this.DataCard = dataCard;
        this.Config = prgmConfig;
        this.SHOW_STARTER_TAGS = IncludeSettingTags;
        // Establish accessible chapters per user criterion.
        this.ChapterBounds = { active: [], whitelist: [], full: [] };
        this.HandlePermissions();
        // Link the DataCard back to this binder.
        this.DataCard.setBinder(this);
        // Deploy a chapter on build.
        if (doDeployment != 0) {
            let openingChapter = doDeployment < 1 ? 1 : this.ChapterBounds.active.includes(doDeployment) ? doDeployment : 1;
            console.log("ChapterBinder.initialize\n", "Deploying initial chapter to DataCard.");
            this.DeployOnPage(openingChapter, elementID);
        }
        return;
    }
    static initialize(rootURL_1, storyName_1, prgmConfig_1) {
        return __awaiter(this, arguments, void 0, function* (rootURL, storyName, prgmConfig, permissions = 0, dataCard, elementID = "", doDeployment = 1, IncludeSettingTags = false) {
            let sourceURL = `${rootURL}/TOC/TOC_${storyName}.json`;
            let source = yield TableOfContents.initialize(sourceURL, storyName);
            return new ChapterBinder(rootURL, storyName, prgmConfig, source, permissions, dataCard, elementID, doDeployment, false, IncludeSettingTags);
        });
    }
    doWhitelist(requestedChapter) {
        if (!this.ChapterBounds.active.includes(requestedChapter)) {
            console.warn("ChapterBinder.pullRequest\n", `Requested chapter is out of bounds of access for permission level ${this.Permissions}.`);
            return false;
        }
        return true;
    }
    pullRequest(requestedChapter) {
        return __awaiter(this, void 0, void 0, function* () {
            //  Handles a chapter pull request, fetching and caching the chapter if not already present.
            //  @param requestedChapter Chapter number being requested.
            //  @return True if chapter was fetched and added to binder, false otherwise.
            //
            if (!this.doWhitelist(requestedChapter)) {
                console.warn("ChapterBinder.pullRequest\n", `Requested chapter ${requestedChapter} is not on whitelist.`);
                return false;
            }
            let isInBinder = false;
            Object.entries(this.SessionBinder).forEach(([chapter, contents]) => {
                if (Number(chapter) == requestedChapter) {
                    console.log("ChapterBinder.pullRequest\n", `Requested chapter ${requestedChapter} is already in binder.`);
                    isInBinder = true;
                }
            });
            if (!isInBinder) {
                let actnum = this.TOC[requestedChapter - 1].Act;
                let chapterURL = `${this.rootURL}/sectioned/${this.storyName}/${actnum}/${requestedChapter}.json`;
                const response = yield fetch(chapterURL);
                if (!response.ok) {
                    console.debug(`ChapterBinder.pullRequest\n","Error fetching manuscript from URL at ${chapterURL}.`);
                    return false;
                }
                else {
                    console.debug("ChapterBinder.pullRequest\n", "Successfully fetched manuscript from URL.");
                }
                this.SessionBinder[requestedChapter] = yield response.json();
                return true;
            }
            return true;
        });
    }
    ToggleSpecificName(setting = null) {
        if (setting != null) {
            this.doSpecificName = setting;
        }
        else {
            this.doSpecificName = !this.doSpecificName;
        }
        this.DeployOnPage('', DEPLOY);
    }
    DeployOnPage(requestedChapter_1, targetElementID_1) {
        return __awaiter(this, arguments, void 0, function* (requestedChapter, targetElementID, purgeContent = true) {
            // 
            //  Deploys the requested chapter's content onto the specified HTML element.
            //  @param requestedChapter Chapter number being requested.
            //  @param targetElementID ID of the HTML element to deploy content to.
            //
            // If requested chapter is a string, make sure it's the right string.
            switch (requestedChapter) {
                case "PREV":
                    requestedChapter = Number(this.DataCard.currentChapter() - 1);
                    console.log("ChapterBinder.DeployOnPage\n", `Retrieving Chapter ${requestedChapter}.`);
                    break;
                case "NEXT":
                    requestedChapter = Number(this.DataCard.currentChapter() + 1);
                    console.log("ChapterBinder.DeployOnPage\n", `Retrieving Chapter ${requestedChapter}.`);
                    break;
                default:
                    if (!(typeof (requestedChapter) == "number")) {
                        console.warn("ChapterBinder.DeployOnPage\n", `Chapter ${requestedChapter} is not a valid string.`);
                        requestedChapter = 1;
                    }
                    break;
            }
            // Is it on the whitelist per user's permissions?
            if (!this.doWhitelist(requestedChapter)) {
                console.warn("ChapterBinder.DeployOnPage\n", `Chapter ${requestedChapter} is not on the whitelist.`);
                return false;
            }
            // Save to local storage configurations.
            SRC.SetSavedChapter(requestedChapter);
            eBODY.scrollTo(0, 0);
            // Is it in the binder already? If not, pull it in.
            let isInBinder = yield this.pullRequest(requestedChapter);
            if (!isInBinder) {
                console.error("ChapterBinder.DeployOnPage\n", "Error fetching chapter for deployment.");
                return false;
            }
            // Was a target element for this HTML correctly defined?
            let targetElement = document.getElementById(targetElementID);
            if (!targetElement) {
                console.error("ChapterBinder.DeployOnPage\n", "Target HTML element not found.");
                return false;
            }
            if (purgeContent) {
                targetElement.innerHTML = "";
            }
            // By this point, we have the chapter in the binder and a valid target element.
            console.info("ChapterBinder.DeployOnPage\n", `Deploying chapter on page.`, `This chapter ${this.SHOW_STARTER_TAGS ? "DOES" : "DOES NOT"} include setting tags.`);
            // Get chapter content from the Session Binder.
            let chapter = this.SessionBinder[requestedChapter];
            // Chapter content (HTML) starts empty.
            let chapterContent = "";
            let starterTag = "";
            // Get chapter info from TOC for this chapter.
            let ChapterInfo = this.TOC[requestedChapter - 1];
            // CHAPTER HEADER:
            let prefix = this.Config.config["Styles"][ChapterInfo.Character[0]]["Prefix"];
            let suffix = this.Config.config["Styles"][ChapterInfo.Character[0]]["Suffix"];
            chapterContent += `<h3 id="title_${ChapterInfo.ChapterFull}" class="${ChapterInfo.Character[0]}Head Title">${ChapterInfo.ChapterNumber}</h3>`;
            chapterContent += `<h3 id="sub_${ChapterInfo.ChapterFull}" class="${ChapterInfo.Character[0]}Head Subtitle">${prefix + ChapterInfo.ChapterName + suffix}</h3>`;
            // Enumerate sections since forEach doesn't iterate over a for loop index.
            let thisSection = 0;
            // Each chapter holds a section.
            chapter.forEach((section) => {
                // Define a Section ID for this section.
                let SectionID = `${requestedChapter}.${thisSection + 1}`;
                this.CURRENT_SCENE = [ChapterInfo.Act, requestedChapter, thisSection, 0];
                if (thisSection != 0 || true) {
                    chapterContent += `${this.Config.config["Bonus"][this.storyName]["Dividers"][ChapterInfo.Character[thisSection]]}<br>`;
                }
                // Get the three datums in every feedline: [style, body text, is End Of Line]
                let wasEOL = true; // start true to get first <p> tag
                let thisLine = 0;
                // Each section holds multiple fragments. The End Of Line indicator defines the end of a Line.
                // It is in fragments, because a line may have multiple styles within it as <span>s.
                let sectionContent = "";
                let lineContent = [];
                // Handle story starter tags.
                if (this.SHOW_STARTER_TAGS) {
                    let sceneDate = this.TOC[requestedChapter - 1].Settings[thisSection].ISO;
                    let sceneSetting = this.TOC[requestedChapter - 1].Settings[thisSection];
                    let RegionName = `${sceneSetting.Area == "Unspecified" ? "" : (sceneSetting.Area + ", ")}${sceneSetting.Region}`;
                    let PlaceName = `${sceneSetting.Location == "Unspecified" ? "" : sceneSetting.Location}`;
                    console.debug(ChapterInfo.Character[thisSection]);
                    // Format ISO date to "Weekday, Month Date"
                    starterTag = (() => {
                        let formatted = sceneDate;
                        const dt = new Date(sceneDate);
                        if (!isNaN(dt.getTime())) {
                            const datePart = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).format(dt);
                            const timePart = new Intl.DateTimeFormat('en-US', { hour: '2-digit', minute: '2-digit', /* second: '2-digit',*/ hour12: false }).format(dt);
                            formatted = `${datePart}, ${timePart}`;
                        }
                        return `<p class="StarterTag Body${ChapterInfo.Character[thisSection]}" style="font-size: var(--TagFontSize); margin-bottom: 20px;">
                ${this.Config.getFullName(ChapterInfo.Character[thisSection])} <br>
                ${formatted} <br>
                ${RegionName}  ${((PlaceName == "") || (!this.doSpecificName)) ? "" : "<br>" + PlaceName}             
                </p>`;
                    })();
                }
                chapterContent += starterTag;
                section.forEach((feedline) => {
                    // Store content of this individual line.
                    // The Section Style is an array containing the perspective of each section e.g. [Cody, Katiya, Titus, ...]
                    let SectionStyle = ChapterInfo.Character[thisSection];
                    // Chapter.Section.Line
                    let LineID = `${requestedChapter}.${thisSection + 1}.${thisLine + 1}`;
                    let style = feedline[0];
                    let text = feedline[1];
                    let isEOL = Boolean(feedline[2]);
                    let doPB = Boolean(feedline[3]); // do paragraph break instead of </p>     
                    let isRawHTML = Boolean(feedline[4]); // this is a special, raw HTML section.
                    if (doPB) {
                        text += '<br>';
                    }
                    lineContent.push([style, text]);
                    // End of line means closing </p> tag.
                    if (isEOL && (!doPB)) {
                        thisLine += 1;
                        // Append resolved line to section
                        sectionContent += this.ResolveThisLine(lineContent, LineID, SectionStyle);
                        // flush lineContent
                        lineContent = [];
                    }
                    wasEOL = isEOL;
                });
                chapterContent += `<div class='section' id='${SectionID}'> ${sectionContent} </div>`;
                thisSection += 1;
            });
            // Actual deployment of chapter content to target element.
            targetElement.innerHTML = chapterContent;
            // Update the DataCard with current chapter info.
            this.DataCard.Update(requestedChapter);
            this.placeWorldMap(ChapterInfo.Character[0]);
            return true;
        });
    }
    WhoIsSender(line) {
        let msgsource = "Anon";
        Object.entries(this.MsgMatch).forEach(([query, result]) => {
            if (line.search(query) != -1) {
                msgsource = result;
            }
        });
        //console.log(line,msgsource)
        return msgsource;
    }
    placeWorldMap(character) {
        let eIMG = eMAP;
        eIMG.src = `../Scriv2WN/maps/map${character}.jpg`;
        //this.CURRENT_SCENE[2]
    }
    ResolveThisLine(lineContent, lineID, sectionStyle) {
        // Generate the next paragraph <p> line for deployment.
        // 
        // lineContent contains a sequential array of snippets to put in this paragraph:
        //      [0] Local style of this specific snippet
        //      [1] Text of this snippet
        // lineID is the ID of this line.
        // sectionStyle is the style of the full section this paragraph is in.
        //
        //  List of every possible style:
        //  |  > STANDARD <  |  >  EMPTY   <  |  > SPECIAL  <  |  >  INLINE  <  |
        //  |----------------+----------------+----------------+----------------|
        //  | Block          | Comment        | NoteCody       | em             |
        //  | Body           | Heading1       | NoteKatiya     | Internal       |
        //  | BodyCody       | Heading2       | NoteJade       |                |
        //  | BodyJade       |                | MessageFrom    |                |
        //  | BodyKatiya     |                | MessageTo      |                |
        //  | BodyTitus      |                | MessageFromDate|                |
        //  |                |                | MessageToDate  |                |
        //  |----------------+----------------+----------------+----------------|
        //
        let ParagraphStyle = `Body${sectionStyle}`;
        let isSpecial = false;
        let extraStyles = "";
        let doStartP = true;
        let doEndP = true;
        let isCustomHTML = false;
        let spacerContent = "";
        //console.warn(sectionStyle,ParagraphStyle)
        // Determine line style by analyzing each line's reported local style.
        lineContent.forEach(([style, line]) => {
            if (style.includes("Timestamp")) { // This predicates the text message.
                let sender = this.WhoIsSender(line);
                //console.log("Sender is",sender)
                this.lastMessenger = sender;
                extraStyles += ` by${this.lastMessenger}`;
            }
            else if (!style.includes("Message")) {
                extraStyles = "";
            }
            if (style.includes("Message") && (!isSpecial)) {
                isSpecial = true;
                ParagraphStyle = style;
            }
            else if (style.includes("Note") && (!isSpecial)) {
                //console.warn(style) 
                isSpecial = true;
                ParagraphStyle = style;
            }
            else if (!style.includes("Note") && !style.includes("Message")) {
                spacerContent = '<span class="textspace"></span>';
            }
            // @TODO add other important styles to segregate
            if (style.includes("RawHTML")) {
                //console.log(style)
                isCustomHTML = true;
            }
        });
        let fullLine = "";
        if (isCustomHTML) {
            fullLine = `<div style="CustomHTMLsection" id="${lineID}">`;
            lineContent.forEach(([style, line]) => {
                fullLine += `${line}`;
            });
            fullLine += `</div>`;
        }
        else {
            fullLine = `<p class="${ParagraphStyle + extraStyles}" id="${lineID}">${spacerContent}`;
            let fragStyle = "";
            let fragEnum = 1;
            lineContent.forEach(([style, line]) => {
                let addBR = "";
                if (style.includes("Timestamp")) {
                    addBR = "<br>";
                }
                fragStyle = doStartP ? style : isSpecial ? ParagraphStyle : style + doStartP;
                fullLine += `<span class="${fragStyle}" id="${lineID}.${fragEnum}">${line}</span> ${addBR}`;
                fragEnum += 1;
            });
            fullLine += "</p>";
        }
        return fullLine;
    }
}
//
//  ▄█████ ▄█████ ▄█████   █ ██  ██ ██ ▄█████ ██  ██ ▄████▄ ██     ▄█████ 
//  ██     ▀▀▀▄▄▄ ▀▀▀▄▄▄  █  ██▄▄██ ██ ▀▀▀▄▄▄ ██  ██ ██▄▄██ ██     ▀▀▀▄▄▄ 
//  ▀█████ █████▀ █████▀ █    ▀██▀  ██ █████▀ ▀████▀ ██  ██ ██████ █████▀ 
//
class ThemeDriver {
    constructor(config, textContainer, datacard, eBackground, eTextCanvas, eProgressBar, doFading = true) {
        var _a;
        /**
         * Manages dynamic theming for manuscript reading.
         */
        this.Story = null;
        this.TextContainer = null;
        this.StaticContainer = null;
        this.ScrollBreaks = [];
        this.Keyframes = [];
        this.doFading = false;
        this.FadeStyle = {
            Background: [0, 0, 0, 1],
            Text: [0, 0, 0, 1],
            ProgressBar: [0, 0, 0, 1]
        };
        this.TransitionWidth = 400; // pixels
        this.CurrentFrame = {
            Background: [0, 0, 0, 1],
            Text: [0, 0, 0, 1],
            ProgressBar: [0, 0, 0, 1]
        };
        this.CurrentWall = {
            FromImage: "",
            ToImage: "",
            Progress: 0,
            FromCharacter: "",
            ToCharacter: ""
        };
        this.TravelHeight = 1;
        this.Story = datacard.Story;
        this.ThemeIndex = config["ThemeIndex"];
        this.ThemeData = config["Styles"];
        this.ThemeElements = {
            Background: eBackground,
            Text: eTextCanvas,
            ProgressBar: eProgressBar
        };
        this.TextContainer = document.getElementById(textContainer);
        this.StaticContainer = ((_a = this.TextContainer) === null || _a === void 0 ? void 0 : _a.parentElement) || null;
        datacard.setThemeDriver(this);
        this.DataCard = datacard;
        this.doFading = doFading;
        let BGelem = 255 * Number(!this.DataCard.NightMode);
        let FGelem = 255 * Number(this.DataCard.NightMode);
        this.CurrentFrame.Background = this.FadeStyle.Background = [BGelem, BGelem, BGelem, 1];
        this.CurrentFrame.Text = this.FadeStyle.Text = [FGelem, FGelem, FGelem, 1];
        this.CurrentFrame.ProgressBar = this.FadeStyle.ProgressBar = [FGelem, FGelem, FGelem, 1];
        this.BarFFG = document.getElementById('BARFFG');
    }
    set Transition(width) {
        width = width < 200 ? 200 : width > 800 ? 800 : width;
        this.TransitionWidth = width;
    }
    setKeyframes() {
        // EXAMPLE of a four-scene system with or without fading: (STATIC shows both)
        //             |    :         :    |    :         :    |    :         :    |    :         :    |
        //             |    :         :    |    :         :    |    :         :    |    :         :    |
        //     SCROLL [0]   :         :   [1]   :         :   [2]   :         :   [3]   :         :   [4]
        //        KEY [0]   :        [1]   |   [2]       [3]   |   [4]       [5]   |   [6]        :   [7]
        //   KEY+FADE [0]  [1]       [2]       [3]       [4]   |   [5]       [6]   |   [7]       [8]  [9]
        //     STATIC  |<---:<------->:    |    :<------->:    |    :<------->:    |    :<------->:--->|
        // TRANSITION  |    :         :<------->:         :<------->:         :<------->:         :    |
        //     FADERS  |<-->:         :    |    :         :    |    :         :    |    :         :<-->|
        //             |    :         :    |    :         :    |    :         :    |    :         :    |
        //             |    :         :    |    :         :    |    :         :    |    :         :    |
        // Have scroll breaks even been defined yet?
        if (this.ScrollBreaks.length == 0) {
            console.error("ThemeDriver.setKeyframes\n", "Scroll breaks have not been defined. Cannot set keyframes.");
            return;
        }
        // Minimum possible value for ScrollBreaks length is 2 (start and end).
        let FrameCount = 2 + (this.ScrollBreaks.length - 2) * 2;
        //console.debug("ThemeDriver.setKeyframes",`Setting ${FrameCount} keyframes...`)
        this.Keyframes = [];
        // DEFINING TRANSITIONS
        let start = 0;
        let end = 0;
        let start_theme = "";
        let end_theme = "";
        let sceneNumber = 1;
        // If fading, add a keyframe for the start transitioning from DEFAULT to the first theme.
        if (this.doFading) {
            start = 0;
            end = 0 + (this.TransitionWidth / 2);
            start_theme = "Default";
            end_theme = this.ScrollBreaks[0].Theme;
            sceneNumber = this.ScrollBreaks[0].scenenum;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end, scenenum: sceneNumber });
            start = end;
            // If not, STATIC until first transition.
        }
        else {
            start = 0;
        }
        end = this.ScrollBreaks[1].atPoint - (this.TransitionWidth / 2);
        start_theme = this.ScrollBreaks[0].Theme;
        end_theme = this.ScrollBreaks[0].Theme;
        sceneNumber = this.ScrollBreaks[0].scenenum;
        this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end, scenenum: sceneNumber });
        //console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as STATIC START`)
        // Iterations in the middle will all be the same.
        for (let i = 1; i < this.ScrollBreaks.length - 1; i++) {
            // This is an intermediate DYNAMIC transition.
            start = end;
            end = this.ScrollBreaks[i].atPoint + (this.TransitionWidth / 2);
            start_theme = this.ScrollBreaks[i - 1].Theme;
            end_theme = this.ScrollBreaks[i].Theme;
            sceneNumber = this.ScrollBreaks[i].scenenum;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end, scenenum: sceneNumber });
            //console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as DYNAMIC`)
            // This is an intermediate STATIC transition.
            start = end;
            end = this.ScrollBreaks[i + 1].atPoint - (this.TransitionWidth / 2);
            start_theme = this.ScrollBreaks[i].Theme;
            end_theme = this.ScrollBreaks[i].Theme;
            sceneNumber = this.ScrollBreaks[i].scenenum;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end, scenenum: sceneNumber });
            //console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as STATIC`)
        }
        start = end;
        start_theme = this.ScrollBreaks[this.ScrollBreaks.length - 1].Theme;
        // If fading, set the STATIC breakpoint early and do a DYNAMIC transition.
        if (this.doFading) {
            end = this.ScrollBreaks[this.ScrollBreaks.length - 1].atPoint - (this.TransitionWidth / 2);
            end_theme = this.ScrollBreaks[this.ScrollBreaks.length - 1].Theme;
            sceneNumber = this.ScrollBreaks[this.ScrollBreaks.length - 1].scenenum;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end, scenenum: sceneNumber });
            start = end;
            end = this.ScrollBreaks[this.ScrollBreaks.length - 1].atPoint;
            start_theme = end_theme;
            end_theme = "Default";
            // Otherwise, STATIC transition until the end.
        }
        else {
            end = this.ScrollBreaks[this.ScrollBreaks.length - 1].atPoint; // @TODO black fade out
            end_theme = this.ScrollBreaks[this.ScrollBreaks.length - 1].Theme;
            sceneNumber = this.ScrollBreaks[this.ScrollBreaks.length - 1].scenenum;
        }
        this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end, scenenum: sceneNumber });
        return;
    }
    getScrollBreaks() {
        return __awaiter(this, arguments, void 0, function* (doReport = true) {
            // Assume that HTML layout is [text container] => [<div> of scene] => ...
            // BoundingDims: Dimensions of the container sized to viewer window (100dvh less menu and footer)
            // TotalDims: Full dimensions of the text container with all content.
            // SceneDims[]: Array of bounding dimensions for each scene container.
            // Definition of "true scrolling position":
            //    - Full TotalDims height - (2 * (0.5 * BoundingDims height)) is total scrolling travel.
            // Check for valid arguments, and valid HTML setup.
            if (!this.TextContainer) {
                console.warn("ThemeDriver.getScrollBreaks\n", "Text container not found.");
                return [];
            }
            if (this.TextContainer.childNodes.length == 0) {
                console.warn("ThemeDriver.getScrollBreaks\n", "Text container has no child nodes.");
                return [];
            }
            if (!this.StaticContainer) {
                console.warn("ThemeDriver.getScrollBreaks\n", "Text container parent not found.");
                return [];
            }
            let BoundingDims = this.StaticContainer.getBoundingClientRect();
            if (!BoundingDims) {
                console.warn("ThemeDriver.getScrollBreaks\n", "Text container parent has no bounding dimensions.");
                return [];
            }
            // Return vertical size of container holding text (that scrolls inside the scene container).
            let TotalDims = this.TextContainer.getBoundingClientRect();
            // Get each of the <div> child elements of the TextContainer, which are each of the scene <div> containers.
            let SceneContainers = Array.from(this.TextContainer.getElementsByClassName('section'));
            // Aggregate each of the heights of the scene <div> containers. Start with an empty array, and append values.
            let SceneDims = [];
            let sceneNumber = 1; // Track number of this div scene.
            SceneContainers.forEach((sceneContainer) => {
                SceneDims.push(sceneContainer.getBoundingClientRect());
            });
            // Return the total travel height of scrolling: the total container height minus both halves of the view/bounding container.
            this.TravelHeight = TotalDims.height - BoundingDims.height;
            // First scroll break is set at zero. The theme will be the first character.
            // IMPORTANT NOTE: Denotation of the character for each LINE BREAK defines the theme for the NEXT section.
            this.ScrollBreaks = [{ Theme: this.DataCard.Data.TOC.Character[0], atPercent: 0, atPoint: 0, scenenum: sceneNumber }];
            // Sum the heights of each of the containers. This will define the SCROLL BREAK points.
            let SceneHeightSum = 0;
            for (let i = 1; i < SceneDims.length; i++) {
                sceneNumber += 1;
                SceneHeightSum += SceneDims[i - 1].height;
                let ScrollPosition = (SceneHeightSum / this.TravelHeight) * 100;
                this.ScrollBreaks.push({ Theme: this.DataCard.Data.TOC.Character[i], atPercent: ScrollPosition, atPoint: SceneHeightSum, scenenum: sceneNumber });
            }
            // Push the final value, at the bottom of the travel. Will have same theme as last entry to ensure constant end.
            this.ScrollBreaks.push({ Theme: this.DataCard.Data.TOC.Character[SceneDims.length - 1], atPercent: 100, atPoint: this.TravelHeight, scenenum: sceneNumber });
            // For debug report.
            if (doReport) {
                console.log(`----==== Scroll Break Report ====----`
                    + `Bounding Dimensions:      Height = ${BoundingDims.height.toFixed(2)} px`
                    + `Total Dimensions:         Height = ${TotalDims.height.toFixed(2)} px`
                    + `Travel Height:            ${this.TravelHeight.toFixed(2)} px`
                    + `Number of Scenes:         ${SceneDims.length}`
                    + `Scroll Breaks (%):\n`, this.ScrollBreaks, "\n\n");
            }
            this.setKeyframes();
            this.ProgressBarSplits();
            return;
        });
    }
    ProgressBarSplits() {
        this.BarFFG.innerHTML = "";
        let SB_index = 0;
        let SB_lim = this.ScrollBreaks.length - 1;
        let lastBreak = 0;
        let thisBreak = 0;
        let theme = "";
        this.ScrollBreaks.forEach((sbreak) => {
            lastBreak = thisBreak;
            thisBreak = sbreak.atPercent;
            //console.log(thisBreak)
            if (SB_index > 0) {
                this.BarFFG.innerHTML += `<div class="barsection bs${theme}" style="flex:${thisBreak - lastBreak}"></div>`;
                if (SB_index < SB_lim) {
                    this.BarFFG.innerHTML += `<div class="barblank"></div>`;
                }
            }
            theme = sbreak.Theme;
            //console.error(sbreak)
            SB_index += 1;
        });
    }
    getFrame(scrollPosition = null) {
        /**
         * Given a scroll position, interpolate for the correct display characteristics.
         * @param scrollPosition Current scroll position in pixels.
         * @return Keyframe object that applies to this scroll position.
         */
        // Check for problematic values.
        let FrameInfo = {
            voice: "Default",
            position: 0,
            progress: 0,
            scene: 1
        };
        if (scrollPosition == null) {
            if (!this.TextContainer) {
                console.warn("ThemeDriver.getFrame\n", "Text container not found. Cannot get scroll position.");
                return FrameInfo;
            }
            if (!this.StaticContainer) {
                console.warn("ThemeDriver.getFrame\n", "Static container not found. Cannot get scroll position.");
                return FrameInfo;
            }
            scrollPosition = this.StaticContainer.getBoundingClientRect().top - this.TextContainer.getBoundingClientRect().top;
        }
        let scrollPercent = (100 * scrollPosition / this.TravelHeight).toFixed(2);
        FrameInfo.position = Number(scrollPercent);
        ROOT.style.setProperty("--BarLength", `${scrollPercent}%`);
        // @OPTIMIZE does this need updates this frequently???
        // this.DataCard.updateDataBar()
        // Dark theming will determine color palette.
        let darkTheme = this.DataCard.NightMode ? "Dark" : "Light";
        let currentKey = null;
        let index = 0;
        for (let i = 0; i < this.Keyframes.length; i++) {
            if (scrollPosition >= this.Keyframes[i].min && scrollPosition <= this.Keyframes[i].max) {
                currentKey = this.Keyframes[i];
                FrameInfo.scene = this.Keyframes[i].scenenum;
                break;
            }
            index += 1;
        }
        if (currentKey == null) {
            //console.warn("ThemeDriver.getFrame","No keyframe found for scroll position:",scrollPosition)
            FrameInfo.voice = this.DataCard.Data.TOC.Character[0];
            return FrameInfo;
        }
        let KeyProgress = (scrollPosition - currentKey.min) / (currentKey.max - currentKey.min);
        FrameInfo.progress = KeyProgress;
        //let debug = document.getElementById("DEBUG");        
        if (currentKey.startTheme == currentKey.endTheme) {
            // if (debug != null) {
            //     debug.innerHTML = `<span style="color: white">Static keyframe found for scroll position ${scrollPosition.toFixed(0)} at ${(KeyProgress*100).toFixed(2)}% <br> This is ${currentKey.startTheme} at index ${index}.<br> ${currentKey.min.toFixed(0)} to ${currentKey.max.toFixed(0)}</span>`
            // }
            this.CurrentFrame = this.ThemeData[currentKey.startTheme][darkTheme];
            this.CurrentWall = {
                FromImage: this.ThemeData[currentKey.startTheme]["WallImage"],
                ToImage: this.ThemeData[currentKey.endTheme]["WallImage"],
                Progress: 0.5,
                FromCharacter: currentKey.startTheme,
                ToCharacter: currentKey.endTheme
            };
            FrameInfo.voice = currentKey.endTheme;
            return FrameInfo;
        }
        // if (debug != null) {
        //    debug.innerHTML = `<span style="color: white">Interpolating keyframe for scroll position ${scrollPosition.toFixed(0)} at ${(KeyProgress*100).toFixed(2)}% <br>From theme "${currentKey.startTheme}" to "${currentKey.endTheme}.<br> ${currentKey.min.toFixed(0)} to ${currentKey.max.toFixed(0)}"</span>`
        // }
        let startFrame = this.ThemeData[currentKey.startTheme][darkTheme];
        let endFrame = this.ThemeData[currentKey.endTheme][darkTheme];
        this.CurrentFrame = {
            Background: [
                startFrame.Background[0] + (endFrame.Background[0] - startFrame.Background[0]) * KeyProgress,
                startFrame.Background[1] + (endFrame.Background[1] - startFrame.Background[1]) * KeyProgress,
                startFrame.Background[2] + (endFrame.Background[2] - startFrame.Background[2]) * KeyProgress,
                startFrame.Background[3] + (endFrame.Background[3] - startFrame.Background[3]) * KeyProgress,
            ],
            Text: [
                startFrame.Text[0] + (endFrame.Text[0] - startFrame.Text[0]) * KeyProgress,
                startFrame.Text[1] + (endFrame.Text[1] - startFrame.Text[1]) * KeyProgress,
                startFrame.Text[2] + (endFrame.Text[2] - startFrame.Text[2]) * KeyProgress,
                startFrame.Text[3] + (endFrame.Text[3] - startFrame.Text[3]) * KeyProgress,
            ],
            ProgressBar: [
                startFrame.ProgressBar[0] + (endFrame.ProgressBar[0] - startFrame.ProgressBar[0]) * KeyProgress,
                startFrame.ProgressBar[1] + (endFrame.ProgressBar[1] - startFrame.ProgressBar[1]) * KeyProgress,
                startFrame.ProgressBar[2] + (endFrame.ProgressBar[2] - startFrame.ProgressBar[2]) * KeyProgress,
                startFrame.ProgressBar[3] + (endFrame.ProgressBar[3] - startFrame.ProgressBar[3]) * KeyProgress,
            ],
        };
        // @TODO image manipulation
        this.CurrentWall = {
            FromImage: this.ThemeData[currentKey.startTheme]["WallImage"],
            ToImage: this.ThemeData[currentKey.endTheme]["WallImage"],
            Progress: KeyProgress,
            FromCharacter: currentKey.startTheme,
            ToCharacter: currentKey.endTheme
        };
        FrameInfo.voice = currentKey.startTheme == "Default" ? currentKey.endTheme : currentKey.startTheme;
        return FrameInfo;
    }
    deployTheming() {
        /**
         *  Set the theme: apply to CSS ROOT variables.
         */
        if (ROOT == null) {
            console.warn("ThemeDriver.deployTheming\n", "Root HTML element not found. Cannot deploy colors.");
            return;
        }
        let t1 = this.CurrentWall.Progress;
        let t2 = 1.00 - t1;
        let edges = 0.450;
        let centers = 0.800;
        let WallCSS1 = `linear-gradient(
                            to right, 
                            rgba(128,128,128,${t1 * edges}) 0%,
                            rgba(128,128,128,${t1 * centers}) calc((( 100vw - var(--ContentWidth) ) * 0.5) + 20px),
                            rgba(128,128,128,${t1 * centers}) calc((( 100vw - var(--ContentWidth) ) * 0.5) +  var(--ContentWidth) - 20px),
                            rgba(128,128,128,${t1 * edges}) 100%
                        ),
                        var(--Wall${this.CurrentWall.FromCharacter})`;
        let WallCSS2 = `linear-gradient(
                            to right, 
                            rgba(128,128,128,${t2 * edges}) 0%,
                            rgba(128,128,128,${t2 * centers}) calc((( 100vw - var(--ContentWidth) ) * 0.5) + 20px),
                            rgba(128,128,128,${t2 * centers}) calc((( 100vw - var(--ContentWidth) ) * 0.5) +  var(--ContentWidth) - 20px),
                            rgba(128,128,128,${t2 * edges}) 100%
                        ),
                        var(--Wall${this.CurrentWall.ToCharacter})`;
        ROOT.style.setProperty("--TextColor", `rgba(${this.CurrentFrame["Text"][0]},${this.CurrentFrame["Text"][1]},${this.CurrentFrame["Text"][2]},${1})`);
        ROOT.style.setProperty("--BackgroundColor", `rgba(${this.CurrentFrame["Background"][0]},${this.CurrentFrame["Background"][1]},${this.CurrentFrame["Background"][2]},${1})`);
        let PercentOff = 0.80;
        let CalcRGBA = [((255 * (1 - PercentOff) * 0.5) + ((Number(this.CurrentFrame["Background"][0]) * PercentOff))),
            ((255 * (1 - PercentOff) * 0.5) + ((Number(this.CurrentFrame["Background"][1]) * PercentOff))),
            ((255 * (1 - PercentOff) * 0.5) + ((Number(this.CurrentFrame["Background"][2]) * PercentOff)))];
        ROOT.style.setProperty("--MidgroundColor", `rgba(${CalcRGBA[0]},${CalcRGBA[1]},${CalcRGBA[2]},${1})`);
        PercentOff = 0.60;
        CalcRGBA = [((255 * (1 - PercentOff) * 0.5) + ((Number(this.CurrentFrame["Background"][0]) * PercentOff))),
            ((255 * (1 - PercentOff) * 0.5) + ((Number(this.CurrentFrame["Background"][1]) * PercentOff))),
            ((255 * (1 - PercentOff) * 0.5) + ((Number(this.CurrentFrame["Background"][2]) * PercentOff)))];
        ROOT.style.setProperty("--ElementColor", `rgba(${CalcRGBA[0]},${CalcRGBA[1]},${CalcRGBA[2]},${1})`);
        ROOT.style.setProperty("--BarColor", `rgba(${this.CurrentFrame["ProgressBar"][0]},${this.CurrentFrame["ProgressBar"][1]},${this.CurrentFrame["ProgressBar"][2]},${1})`);
        ROOT.style.setProperty("--HoverColor", `rgba(${this.CurrentFrame["ProgressBar"][0]},${this.CurrentFrame["ProgressBar"][1]},${this.CurrentFrame["ProgressBar"][2]},${0.1})`);
        ROOT.style.setProperty("--TOCbackground", `rgba(${this.CurrentFrame["ProgressBar"][0]},${this.CurrentFrame["ProgressBar"][1]},${this.CurrentFrame["ProgressBar"][2]},${0.03})`);
        ROOT.style.setProperty("--ImageWallFore", WallCSS1);
        ROOT.style.setProperty("--ImageWallBack", WallCSS2);
        // Make sure it never sets it to Default style which is nothing.
        let TextStyle = this.CurrentWall.FromCharacter == "Default" ? this.CurrentWall.ToCharacter : this.CurrentWall.FromCharacter == "" ? "Fallback" : this.CurrentWall.FromCharacter;
        ROOT.style.setProperty("--ActiveTitle", `var(--${TextStyle}Title)`);
        ROOT.style.setProperty("--ActiveSub", `var(--${TextStyle}Text)`);
        ROOT.style.setProperty("--ActiveSize", `var(--${TextStyle}Size)`);
        ROOT.style.setProperty("--ActiveText", `var(--${TextStyle}Text)`);
        return;
    }
}
//
//  ██████ ██  ██ ███  ██ ▄█████ ██████ ██ ▄████▄ ███  ██ ▄█████ 
//  ██▄▄   ██  ██ ██ ▀▄██ ██       ██   ██ ██  ██ ██ ▀▄██ ▀▀▀▄▄▄ 
//  ██     ▀████▀ ██   ██ ▀█████   ██   ██ ▀████▀ ██   ██ █████▀ 
//
function buildManuscript(rootURL_1, storyName_1) {
    return __awaiter(this, arguments, void 0, function* (rootURL, storyName, startChapter = 1) {
        SRC = yield LocalStorageAndSrcVars.initialize(storyName);
        CFG = yield StoryConfig.initialize(rootURL, SRC.storyName);
        CARD = new ChapterDataCard(SRC.storyName);
        CARD.toggleNightMode(false); // Start in Night Mode.
        BIND = yield ChapterBinder.initialize(rootURL, SRC.storyName, CFG, SRC.Local.permlevel, CARD, DEPLOY, 0, IncludeSettingTags);
        SRC.AttachBinder(BIND);
        CTRL = new ControlBar(SRC, CARD);
        //BIND.DeployOnPage(CARD.Data.TOC.Chapter,DEPLOY)
        THEME = new ThemeDriver(CFG.config, DEPLOY, CARD, eBackground, eText, eProgressBar, true);
        //console.log(SRC.Local.chapter)
        yield BIND.DeployOnPage(SRC.Local.chapter, DEPLOY);
        EXTRAS = yield StoryExtrasWindow.initialize(SRC.storyName, rootURL, EXTRAID);
        THEME.deployTheming();
        BIND.LockUp();
        yield EXTRAS.loadAnnouncements();
        yield EXTRAS.loadInExtras();
        EXTRAS.deployContent();
        return;
    });
}
function doThemeChange() {
    CTRL.setTheme(CARD);
    THEME.setKeyframes();
    runScrollEvents();
}
function runScrollEvents() {
    LookingAt = THEME.getFrame();
    // contains voice, position, progress, scene
    THEME.deployTheming();
    if (CARD.lookingAt(LookingAt)) {
        BIND.placeWorldMap(LookingAt.voice);
    }
    ;
    BIND.CURRENT_SCENE[2] = LookingAt.scene;
    BIND.CURRENT_SCENE[3] = Number(LookingAt.progress.toFixed(2));
    console.log(BIND.CURRENT_SCENE);
    return;
}
function runResizeEvents() {
    THEME.getScrollBreaks();
    runScrollEvents();
    console.log("runResizeEvents", "\nA resize event has taken place.");
}
function LoadOtherStory(otherstory) {
    let address = window.location.search;
    let Parameters = new URLSearchParams(address);
    let dmap = new Map();
    Parameters.forEach((value, key) => {
        dmap.set(key, value);
    });
    let varargin = "";
    switch (dmap.get("mode")) {
        case "author":
        case "3":
            varargin += '&mode=3';
            break;
        case "editor":
        case "2":
            varargin += '&mode=2';
            break;
        default:
            break;
    }
    let origin = location.origin != 'null' ? location.origin : "";
    let path = location.pathname;
    let hash = location.hash;
    window.open(origin + path + hash + `?story=${otherstory}` + varargin, '_top');
}
//  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
//
//  █████▄ █████▄   ▄████  ██▄  ▄██   ██████ ██  ██ ██████ ▄█████ 
//  ██▄▄█▀ ██▄▄██▄ ██  ▄▄▄ ██ ▀▀ ██   ██▄▄    ████  ██▄▄   ██     
//  ██     ██   ██  ▀███▀  ██    ██   ██▄▄▄▄ ██  ██ ██▄▄▄▄ ▀█████ 
//  The code that interacts with the classes and variables.
//  Runs at init in the HTML script.
document.getElementsByTagName('body')[0].style.backgroundColor = "black";
const ROOT = document.querySelector(':root');
function GEBID(name) { return document.getElementById(name); }
const eBACKGROUND = GEBID('BACKGROUND');
const eHEADER = GEBID('HEADER');
const eBODY = GEBID('BODY');
const eTYPESET = GEBID('TYPESET');
const eIDCHAPTER = GEBID('IDCHAPTER');
const eIDNAME = GEBID('IDNAME');
const eMAP = GEBID('MAP');
const DEPLOY = "TYPESET";
const EXTRAID = "EXTRACONTENT";
var StartChapter = 1;
var CARD;
var CFG;
var BIND;
var THEME;
var SRC;
var EXTRAS;
var CTRL;
var LookingAt = {
    voice: "Default",
    position: 0,
    progress: 0,
    scene: 1
};
var ACTIVESTORY = "Paragate";
var IncludeSettingTags = false;
var eBackground = document.getElementById("BACKGROUND");
var eText = document.getElementById("BODY");
var eProgressBar = document.getElementById("PROGRESS");
// @TODO this will be defined by a JSON config file.
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN";
// Append provided tags to document <head>
const iconaddress = `icons/favicon-${ACTIVESTORY}.png`;
(() => {
    const head = document.head || document.getElementsByTagName('head')[0];
    const linkDefs = [
        { rel: "icon", href: iconaddress, type: "image/x-icon" },
        { rel: "icon", href: iconaddress, type: "image/png", sizes: "32x32" },
        { rel: "apple-touch-icon", href: "icons/apple-touch-icon.png" }
    ];
    linkDefs.forEach(def => {
        const link = document.createElement("link");
        Object.entries(def).forEach(([k, v]) => link.setAttribute(k, v));
        head.appendChild(link);
    });
})();
buildManuscript(rootURL, ACTIVESTORY, StartChapter);
eBODY.addEventListener('scroll', runScrollEvents);
addEventListener("resize", runResizeEvents);
function getMousePosInImage(img, ev) {
    const r = img.getBoundingClientRect();
    const x = ev.clientX - r.left;
    const y = ev.clientY - r.top;
    const px = r.width > 0 ? Math.max(0, Math.min(1, x / r.width)) : 0;
    const py = r.height > 0 ? Math.max(0, Math.min(1, y / r.height)) : 0;
    const percentX = px * 100;
    const percentY = py * 100;
    return { x, y, px, py, percentX, percentY, bounds: r };
}
if (eMAP instanceof HTMLImageElement) {
    eMAP.addEventListener('mousedown', (ev) => {
        const pos = getMousePosInImage(eMAP, ev);
        // Example usage: expose as CSS vars or log
        ROOT.style.setProperty('--img-mouse-x', `${(pos.px * 100).toFixed(2)}%`);
        ROOT.style.setProperty('--img-mouse-y', `${(pos.py * 100).toFixed(2)}%`);
        console.debug('Image mouse pos', `[${pos.percentX},${pos.percentY}]`);
    });
    eMAP.addEventListener('mouseleave', () => {
        ROOT.style.removeProperty('--img-mouse-x');
        ROOT.style.removeProperty('--img-mouse-y');
    });
}
