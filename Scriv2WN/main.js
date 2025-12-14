"use strict";
//  ██ ███  ██ ██████ ██████ █████▄  ██████ ▄████▄ ▄█████ ██████ ▄█████ 
//  ██ ██ ▀▄██   ██   ██▄▄   ██▄▄██▄ ██▄▄   ██▄▄██ ██     ██▄▄   ▀▀▀▄▄▄ 
//  ██ ██   ██   ██   ██▄▄▄▄ ██   ██ ██     ██  ██ ▀█████ ██▄▄▄▄ █████▀ 
//  Templates used in classes.
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
        this.Story = storyName;
        this.rootURL = rootURL;
        this.Container = document.getElementById(containerID);
        if (!this.Container) {
            console.warn("StoryExtrasWindow.constructor", `Container element with ID "${containerID}" not found.`);
        }
    }
    static initialize(storyName, rootURL, containerID) {
        return __awaiter(this, void 0, void 0, function* () {
            return new StoryExtrasWindow(storyName, rootURL, containerID);
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
                    console.error("StoryExtrasWindow.loadContent", `Error fetching content from ${url}.`);
                    return false;
                }
                this.Content = yield response.text();
                return true;
            }
            catch (error) {
                console.error("StoryExtrasWindow.loadContent", `Failed to load content: ${error}`);
                return false;
            }
        });
    }
    deployContent() {
        if (!this.Container) {
            console.warn("StoryExtrasWindow.deployContent", "Container element not found.");
            return false;
        }
        if (!this.Content) {
            console.warn("StoryExtrasWindow.deployContent", "No content loaded.");
            return false;
        }
        this.Container.innerHTML = this.Content;
        return true;
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
class LocalStorageAndSrcVars {
    constructor(binder) {
        //  Search variables take priority over Local Storage.
        this.Parameters = null;
        this.Map = null;
        this.requestedChapter = null;
        this.default = {
            "chapter": 1
        };
        // Default local setup.
        this.Local = Object.create(this.default);
        this.Map = this.PollSrcVars();
        this.Binder = binder;
        let localprefs = localStorage.getItem('SG_Bookmark');
        if (localprefs) {
            try {
                this.Local = JSON.parse(localprefs);
                if (this.ParseSrcVars()) {
                    console.info("LSASV.ParseSrcVars", `Setting chapter to ${this.requestedChapter} from search parameter variables.`);
                    this.Local.chapter = this.requestedChapter;
                    localStorage.setItem('SG_Bookmark', JSON.stringify(this.Local));
                }
            }
            catch (_a) {
                console.error("LSASV.ParseSrcVars", "Issue reading LocalStorage save. Creating new save.");
                localStorage.setItem('SG_Bookmark', JSON.stringify(this.default));
                let get = localStorage.getItem('SG_Bookmark');
                this.Local = JSON.parse(get);
            }
        }
        else {
            console.warn("LSASV.ParseSrcVars", "LocalStorage save does not exist yet. Creating new save.");
            localStorage.setItem('SG_Bookmark', JSON.stringify(this.default));
            let get = localStorage.getItem('SG_Bookmark');
            this.Local = JSON.parse(get);
        }
    }
    static initialize(binder) {
        return __awaiter(this, void 0, void 0, function* () {
            return new LocalStorageAndSrcVars(binder);
        });
    }
    SaveLocalStorage() {
        localStorage.setItem('SG_Bookmark', JSON.stringify(this.Local));
        console.info("LSASV.ParseSrcVars", "Saved local storage:", this.Local);
    }
    SetSavedChapter(chapter) {
        this.Local.chapter = chapter;
        console.info("LSASV.SetSavedChapter", `Last position saved as ${chapter}.`, this.Local);
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
            console.info(`Variables are present in search bar:`, map);
        }
        return map;
    }
    ParseSrcVars(doReport = true) {
        if (this.Map == null) {
            console.error("LSASV.ParseSrcVars", "Unable to parse: not retrieved yet.");
            return false;
        }
        let doPermissions = false;
        switch (this.Map.get("mode")) {
            case "author":
            case "3":
                this.Binder.Permissions = 3;
                console.info("Access level 3 / Author.");
                doPermissions = true;
                break;
            case "editor":
            case "2":
                this.Binder.Permissions = 2;
                console.info("Access level 2 / Reviewer.");
                doPermissions = true;
                break;
            default:
                break;
        }
        if (doPermissions) {
            BIND.HandlePermissions(true);
        }
        let doURLchap = isNaN(Number(this.Map.get("chapter")));
        if (!doURLchap) {
            this.requestedChapter = Math.round(Number(this.Map.get("chapter")));
            console.error("LSASV.ParseSrcVars", `Chapter specified in URL as ${this.requestedChapter}.`);
            return true;
        }
        return false;
    }
}
class ChapterDataCard {
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
    Update(chapterNumber, doReport = true) {
        if (this.Binder == null) {
            console.warn("ChapterDataCard.Update", "No ChapterBinder paired to DataCard. Cannot update data.");
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
        this.Story = StoryName;
        this.eTOC_ID = document.getElementById('TTC_ID');
        this.eTOC_NAME = document.getElementById('TTC_name');
        this.eTOC_BLURB = document.getElementById('TTC_blurb');
        this.eEXTRAHEAD = document.getElementById('EXhead');
    }
    updateTOCinfo() {
        let actRoman = { 0: "Prologue", 1: "Act I", 2: "Act II", 3: "Act III", 4: "Act IV" };
        let actnum = Number(this.Data.TOC.Act);
        this.eTOC_ID.innerHTML = `${actRoman[actnum]}, Chapter ${this.Data.TOC.ChapterNumber}`;
        let ChapterView = this.Data.TOC.Character[0];
        this.Data.TOC.Character.forEach((element) => { ChapterView = ChapterView == element ? ChapterView : "Mixed"; console.log(element); });
        this.eTOC_NAME.innerHTML = `${ChapterView} &mdash; <em>${this.Data.TOC.ChapterName}</em>`;
        this.eTOC_BLURB.innerHTML = `<p>"${this.Data.TOC.Blurb}"</p>`;
        this.eEXTRAHEAD.innerHTML = `${this.Story} Extras`;
    }
    toggleNightMode(doReport = true) {
        this.NightMode = !this.NightMode;
        ROOT.style.setProperty("--IconState", `invert(${this.NightMode})`);
        ROOT.style.setProperty("--BooleanColor", `${this.NightMode ? "white" : "black"}`);
        console.info(`Night mode is now ${this.NightMode ? "on" : "off"}.`);
        return this.NightMode;
    }
    updateDataBar() {
        eIDCHAPTER.innerHTML = `<span>Chapter ${this.Data.TOC.ChapterNumber}</span>`;
        eIDNAME.innerHTML = `<span>${this.Data.TOC.ChapterName}</span>`;
    }
}
class StoryConfig {
    constructor(cfg, storyName) {
        this.config = cfg;
        this.story = storyName;
        this.themes = (this.getAllPossibleThemes());
        return;
    }
    doesThemeExist(characterName, ignoreDefault = false) {
        if (this.themes.includes(characterName) && (!(characterName == "Default" && ignoreDefault))) {
            return true;
        }
        else {
            console.warn("StoryConfig.doesThemeExist", `Character ${characterName} is not a theme name, so it is not a POV character.`);
            return false;
        }
    }
    getAllPossibleThemes() {
        return Object.keys(this.config.Styles);
    }
    ThemesInStory() {
        return this.config.ThemeIndex[this.story];
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
            console.warn("StoryConfig.getCharacterStyle", `${item} is not a theme object.`);
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
                console.debug("StoryConfig.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("StoryConfig.initialize", "Successfully fetched manuscript from URL.");
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
                console.debug("Manuscript.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
            }
            this.data = yield response.json();
            return new Manuscript(rootURL, storyName, this.data);
        });
    }
}
class TableOfContents {
    constructor(toc) {
        this.TOCstate = false;
        this.EXTRAstate = true;
        /**
         * @param toc Full Table Of Contents data.
         */
        this.list = toc;
        this.ToggleDisplay(this.TOCstate);
        this.ToggleInfo(this.EXTRAstate);
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
                console.debug("TableOfContents.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("TableOfContents.initialize", "Successfully fetched manuscript from URL.");
            }
            this.data = yield response.json();
            // ....and now initialization of the Table Of Contents panel.
            ROOT.style.setProperty("--TitleImageTOC", `url(../design/${storyName}_logo.png)`);
            ROOT.style.setProperty("--WallImageTOC", `url()`);
            return new TableOfContents(this.data);
        });
    }
    ToggleDisplay(setState = null) {
        if (this.EXTRAstate) {
            console.error("Unable to activate TOC while Special Window is active.");
            return;
        }
        if (setState == null) {
            this.TOCstate = !this.TOCstate;
        }
        else {
            this.TOCstate = setState;
        }
        console.log("TableOfContents.ToggleDisplay", `Table Of Contents is now ${this.TOCstate ? "shown" : "hidden"}.`);
        // Changing width of TOC? Set --TOCWIDTH in contentstyles.css
        ROOT.style.setProperty("--READER_TOCOFFSET", this.TOCstate ? "var(--TOCWIDTH)" : "0px");
    }
    ToggleInfo(setState = null) {
        if (this.TOCstate) {
            console.error("Unable to activate Special Window while TOC is active.");
            return;
        }
        if (setState == null) {
            this.EXTRAstate = !this.EXTRAstate;
        }
        else {
            this.EXTRAstate = setState;
        }
        console.log("TableOfContents.ToggleInfo", `Special Window is now ${this.EXTRAstate ? "shown" : "hidden"}.`);
        // Changing width of TOC? Set --TOCWIDTH in contentstyles.css
        ROOT.style.setProperty("--READER_EXTRAOFFSET", this.EXTRAstate ? "calc( -1 * var(--EXTRAWIDTH))" : "0px");
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
                console.log("Permissions at ADMIN level.");
                this.ChapterBounds.active = this.ChapterBounds.full;
                break;
            case 1: // Reviewer.
                console.log("Permissions at REVIEWER level.");
                this.ChapterBounds.active = this.ChapterBounds.full;
                break;
            default: // Base user.
                console.log("Permissions at GUEST level.");
                this.ChapterBounds.active = this.ChapterBounds.whitelist;
                break;
        }
        this.ChapterBounds.active.forEach((chapnum) => {
            // recall: chapnum vs chapter indexing
            this.TOC[chapnum - 1]["AccessGranted"] = true;
        });
        if (doReport) {
            console.log(`--- User access report: ---\n > Today is ${today.getUTCDate()}.\n > Access level is ${["GUEST", "REVIEWER", "ADMIN"][this.Permissions]} (${this.Permissions}).\n> User has access to: `, this.ChapterBounds.active);
        }
    }
    constructor(rootURL, storyName, prgmConfig, source, permissions = 0, dataCard, elementID = "", doDeployment = 1, doReport = true) {
        this.rootURL = "";
        this.storyName = "";
        this.SessionBinder = {};
        this.Permissions = 0;
        this.lastMessenger = "Anon";
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
        // Establish accessible chapters per user criterion.
        this.ChapterBounds = { active: [], whitelist: [], full: [] };
        this.HandlePermissions();
        // Link the DataCard back to this binder.
        this.DataCard.setBinder(this);
        // Deploy a chapter on build.
        if (doDeployment != 0) {
            let openingChapter = doDeployment < 1 ? 1 : this.ChapterBounds.active.includes(doDeployment) ? doDeployment : 1;
            console.info("ChapterBinder.initialize", "Deploying initial chapter to DataCard.");
            this.DeployOnPage(openingChapter, elementID);
        }
        return;
    }
    static initialize(rootURL_1, storyName_1, prgmConfig_1) {
        return __awaiter(this, arguments, void 0, function* (rootURL, storyName, prgmConfig, permissions = 0, dataCard, elementID = "", doDeployment = 1) {
            let sourceURL = `${rootURL}/TOC/TOC_${storyName}.json`;
            let source = yield TableOfContents.initialize(sourceURL, storyName);
            return new ChapterBinder(rootURL, storyName, prgmConfig, source, permissions, dataCard, elementID, doDeployment);
        });
    }
    doWhitelist(requestedChapter) {
        if (!this.ChapterBounds.active.includes(requestedChapter)) {
            console.warn("ChapterBinder.pullRequest", `Requested chapter is out of bounds of access for permission level ${this.Permissions}.`);
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
                console.info("ChapterBinder.pullRequest", `Requested chapter ${requestedChapter} is not on whitelist.`);
                return false;
            }
            let isInBinder = false;
            Object.entries(this.SessionBinder).forEach(([chapter, contents]) => {
                if (Number(chapter) == requestedChapter) {
                    console.info("ChapterBinder.pullRequest", `Requested chapter ${requestedChapter} is already in binder.`);
                    isInBinder = true;
                }
            });
            if (!isInBinder) {
                let actnum = this.TOC[requestedChapter - 1].Act;
                let chapterURL = `${this.rootURL}/sectioned/${this.storyName}/${actnum}/${requestedChapter}.json`;
                const response = yield fetch(chapterURL);
                if (!response.ok) {
                    console.debug(`ChapterBinder.pullRequest","Error fetching manuscript from URL at ${chapterURL}.`);
                    return false;
                }
                else {
                    console.debug("ChapterBinder.pullRequest", "Successfully fetched manuscript from URL.");
                }
                this.SessionBinder[requestedChapter] = yield response.json();
                return true;
            }
            return true;
        });
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
                    console.info("ChapterBinder.DeployOnPage", `Retrieveing Chapter ${requestedChapter}.`);
                    break;
                case "NEXT":
                    requestedChapter = Number(this.DataCard.currentChapter() + 1);
                    console.info("ChapterBinder.DeployOnPage", `Retrieveing Chapter ${requestedChapter}.`);
                    break;
                default:
                    if (!(typeof (requestedChapter) == "number")) {
                        console.warn("ChapterBinder.DeployOnPage", `Chapter ${requestedChapter} is not a valid string.`);
                        requestedChapter = 1;
                    }
                    break;
            }
            // Is it on the whitelist per user's permissions?
            if (!this.doWhitelist(requestedChapter)) {
                console.warn("ChapterBinder.DeployOnPage", `Chapter ${requestedChapter} is not on the whitelist.`);
                return false;
            }
            // Save to local storage configurations.
            SRC.SetSavedChapter(requestedChapter);
            eBODY.scrollTo(0, 0);
            // Is it in the binder already? If not, pull it in.
            let isInBinder = yield this.pullRequest(requestedChapter);
            if (!isInBinder) {
                console.warn("ChapterBinder.DeployOnPage", "Error fetching chapter for deployment.");
                return false;
            }
            // Was a target element for this HTML correctly defined?
            let targetElement = document.getElementById(targetElementID);
            if (!targetElement) {
                console.warn("ChapterBinder.DeployOnPage", "Target HTML element not found.");
                return false;
            }
            if (purgeContent) {
                targetElement.innerHTML = "";
            }
            // By this point, we have the chapter in the binder and a valid target element.
            console.info("ChapterBinder.DeployOnPage", "Deploying chapter on page.");
            // Get chapter content from the Session Binder.
            let chapter = this.SessionBinder[requestedChapter];
            // Chapter content (HTML) starts empty.
            let chapterContent = "";
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
                section.forEach((feedline) => {
                    // Store content of this individual line.
                    // The Section Style is an array containing the perspective of each section e.g. [Cody, Katiya, Titus, ...]
                    let SectionStyle = ChapterInfo.Character[thisSection];
                    // Chapter.Section.Line
                    let LineID = `${requestedChapter}.${thisSection + 1}.${thisLine + 1}`;
                    let style = feedline[0];
                    let text = feedline[1];
                    let isEOL = Boolean(feedline[2]);
                    lineContent.push([style, text]);
                    // End of line means closing </p> tag.
                    if (isEOL) {
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
                isSpecial = true;
                ParagraphStyle = style;
            }
            else {
            }
            // @TODO add other important styles to segregate
        });
        let fullLine = `<p class="${ParagraphStyle + extraStyles}" id="${lineID}}">`;
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
        return fullLine + "</p>";
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
        // Have scroll breaks even been deined yet?
        if (this.ScrollBreaks.length == 0) {
            console.warn("ThemeDriver.setKeyframes", "Scroll breaks have not been defined. Cannot set keyframes.");
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
        // If fading, add a keyframe for the start transitioning from DEFAULT to the first theme.
        if (this.doFading) {
            start = 0;
            end = 0 + (this.TransitionWidth / 2);
            start_theme = "Default";
            end_theme = this.ScrollBreaks[0].Theme;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
            start = end;
            // If not, STATIC until first transition.
        }
        else {
            start = 0;
        }
        end = this.ScrollBreaks[1].atPoint - (this.TransitionWidth / 2);
        start_theme = this.ScrollBreaks[0].Theme;
        end_theme = this.ScrollBreaks[0].Theme;
        this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
        //console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as STATIC START`)
        // Iterations in the middle will all be the same.
        for (let i = 1; i < this.ScrollBreaks.length - 1; i++) {
            // This is an intermediate DYNAMIC transition.
            start = end;
            end = this.ScrollBreaks[i].atPoint + (this.TransitionWidth / 2);
            start_theme = this.ScrollBreaks[i - 1].Theme;
            end_theme = this.ScrollBreaks[i].Theme;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
            //console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as DYNAMIC`)
            // This is an intermediate STATIC transition.
            start = end;
            end = this.ScrollBreaks[i + 1].atPoint - (this.TransitionWidth / 2);
            start_theme = this.ScrollBreaks[i].Theme;
            end_theme = this.ScrollBreaks[i].Theme;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
            //console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as STATIC`)
        }
        start = end;
        start_theme = this.ScrollBreaks[this.ScrollBreaks.length - 1].Theme;
        // If fading, set the STATIC breakpoint early and do a DYNAMIC transition.
        if (this.doFading) {
            end = this.ScrollBreaks[this.ScrollBreaks.length - 1].atPoint - (this.TransitionWidth / 2);
            end_theme = this.ScrollBreaks[this.ScrollBreaks.length - 1].Theme;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
            start = end;
            end = this.ScrollBreaks[this.ScrollBreaks.length - 1].atPoint;
            start_theme = end_theme;
            end_theme = "Default";
            // Otherwise, STATIC transition until the end.
        }
        else {
            end = this.ScrollBreaks[this.ScrollBreaks.length - 1].atPoint; // @TODO black fade out
            end_theme = this.ScrollBreaks[this.ScrollBreaks.length - 1].Theme;
        }
        this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
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
                console.warn("ThemeDriver.getScrollBreaks", "Text container not found.");
                return [];
            }
            if (this.TextContainer.childNodes.length == 0) {
                console.warn("ThemeDriver.getScrollBreaks", "Text container has no child nodes.");
                return [];
            }
            if (!this.StaticContainer) {
                console.warn("ThemeDriver.getScrollBreaks", "Text container parent not found.");
                return [];
            }
            let BoundingDims = this.StaticContainer.getBoundingClientRect();
            if (!BoundingDims) {
                console.warn("ThemeDriver.getScrollBreaks", "Text container parent has no bounding dimensions.");
                return [];
            }
            // Return vertical size of container holding text (that scrolls inside the scene container).
            let TotalDims = this.TextContainer.getBoundingClientRect();
            // Get each of the <div> child elements of the TextContainer, which are each of the scene <div> containers.
            let SceneContainers = Array.from(this.TextContainer.getElementsByClassName('section'));
            // Aggregate each of the heights of the scene <div> containers. Start with an empty array, and append values.
            let SceneDims = [];
            SceneContainers.forEach((sceneContainer) => {
                SceneDims.push(sceneContainer.getBoundingClientRect());
            });
            // Return the total travel height of scrolling: the total container height minus both halves of the view/bounding container.
            this.TravelHeight = TotalDims.height - BoundingDims.height;
            // First scroll break is set at zero. The theme will be the first character.
            // IMPORTANT NOTE: Denotation of the character for each LINE BREAK defines the theme for the NEXT section.
            this.ScrollBreaks = [{ Theme: this.DataCard.Data.TOC.Character[0], atPercent: 0, atPoint: 0 }];
            // Sum the heights of each of the containers. This will define the SCROLL BREAK points.
            let SceneHeightSum = 0;
            for (let i = 1; i < SceneDims.length; i++) {
                SceneHeightSum += SceneDims[i - 1].height;
                let ScrollPosition = (SceneHeightSum / this.TravelHeight) * 100;
                this.ScrollBreaks.push({ Theme: this.DataCard.Data.TOC.Character[i], atPercent: ScrollPosition, atPoint: SceneHeightSum });
            }
            // Push the final value, at the bottom of the travel. Will have same theme as last entry to ensure constant end.
            this.ScrollBreaks.push({ Theme: this.DataCard.Data.TOC.Character[SceneDims.length - 1], atPercent: 0, atPoint: this.TravelHeight });
            // For debug report.
            if (doReport) {
                let report = `ThemeDriver.getScrollBreaks Report for :
    Bounding Dimensions:      Height = ${BoundingDims.height.toFixed(2)} px
    Total Dimensions:         Height = ${TotalDims.height.toFixed(2)} px
    Travel Height:            ${this.TravelHeight.toFixed(2)} px
    Number of Scenes:         ${SceneDims.length}
    Scroll Breaks (%):`;
                console.log(report, this.ScrollBreaks);
            }
            this.setKeyframes();
            return;
        });
    }
    getFrame(scrollPosition = null) {
        /**
         * Given a scroll position, interpolate for the correct display characteristics.
         * @param scrollPosition Current scroll position in pixels.
         * @return Keyframe object that applies to this scroll position.
         */
        // Check for problematic values.
        if (scrollPosition == null) {
            if (!this.TextContainer) {
                console.warn("ThemeDriver.getFrame", "Text container not found. Cannot get scroll position.");
                return;
            }
            if (!this.StaticContainer) {
                console.warn("ThemeDriver.getFrame", "Static container not found. Cannot get scroll position.");
                return;
            }
            scrollPosition = this.StaticContainer.getBoundingClientRect().top - this.TextContainer.getBoundingClientRect().top;
        }
        ROOT.style.setProperty("--BarLength", `${(100 * scrollPosition / this.TravelHeight).toFixed(2)}%`);
        // @OPTIMIZE does this need updates this frequently???
        // this.DataCard.updateDataBar()
        // Dark theming will determine color palette.
        let darkTheme = this.DataCard.NightMode ? "Dark" : "Light";
        let currentKey = null;
        let index = 0;
        for (let i = 0; i < this.Keyframes.length; i++) {
            if (scrollPosition >= this.Keyframes[i].min && scrollPosition <= this.Keyframes[i].max) {
                currentKey = this.Keyframes[i];
                break;
            }
            index += 1;
        }
        if (currentKey == null) {
            //console.warn("ThemeDriver.getFrame","No keyframe found for scroll position:",scrollPosition)
            return;
        }
        let KeyProgress = (scrollPosition - currentKey.min) / (currentKey.max - currentKey.min);
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
            return;
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
        return;
    }
    deployTheming() {
        /**
         *  Set the theme: apply to CSS ROOT variables.
         */
        if (ROOT == null) {
            console.warn("ThemeDriver.deployTheming", "Root HTML element not found. Cannot deploy colors.");
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
        // I gotta do this in here because if I do it outside, the await won't work.
        CFG = yield StoryConfig.initialize(rootURL, storyName);
        CARD = new ChapterDataCard(storyName);
        CARD.toggleNightMode(false); // Start in Night Mode.
        BIND = yield ChapterBinder.initialize(rootURL, storyName, CFG, 0, CARD, DEPLOY, 0);
        SRC = yield LocalStorageAndSrcVars.initialize(BIND);
        //BIND.DeployOnPage(CARD.Data.TOC.Chapter,DEPLOY)
        THEME = new ThemeDriver(CFG.config, DEPLOY, CARD, eBackground, eText, eProgressBar, true);
        //console.log(SRC.Local.chapter)
        yield BIND.DeployOnPage(SRC.Local.chapter, DEPLOY);
        EXTRAS = yield StoryExtrasWindow.initialize(storyName, rootURL, EXTRAID);
        THEME.deployTheming();
        BIND.LockUp();
        yield EXTRAS.loadContent();
        return;
    });
}
function runScrollEvents() {
    THEME.getFrame();
    THEME.deployTheming();
    return;
}
function runResizeEvents() {
    THEME.getScrollBreaks();
    runScrollEvents();
    console.debug("runResizeEvents", "A resize event has taken place.");
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
const DEPLOY = "TYPESET";
const EXTRAID = "EXTRACONTENT";
var StartChapter = 9;
var CARD;
var CFG;
var BIND;
var THEME;
var SRC;
var EXTRAS;
var eBackground = document.getElementById("BACKGROUND");
var eText = document.getElementById("BODY");
var eProgressBar = document.getElementById("PROGRESS");
// @TODO this will be defined by a JSON config file.
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN";
buildManuscript(rootURL, 'Paragate', StartChapter);
eBODY.addEventListener('scroll', runScrollEvents);
addEventListener("resize", runResizeEvents);
