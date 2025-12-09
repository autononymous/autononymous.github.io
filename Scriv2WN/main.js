"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
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
        /**
         * @param toc Full Table Of Contents data.
         */
        this.list = toc;
    }
    static initialize(sourceURL) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * This is the access point for creating a TableOfContents instance.
             * @param sourceURL URL to fetch the TOC JSON from.
             * @return TableOfContents instance with fetched data.
             */
            const response = yield fetch(sourceURL);
            if (!response.ok) {
                console.debug("Manuscript.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
            }
            this.data = yield response.json();
            return new TableOfContents(this.data);
        });
    }
}
class ChapterBinder {
    constructor(rootURL, storyName, source, permissions = 0) {
        this.rootURL = ""; // Base URL for fetching resources.
        this.storyName = ""; // Name of the story to fetch.
        this.SessionBinder = {}; // In-session cache of fetched chapters.
        this.Permissions = 0; // User permission level.
        /**
         *  @param rootURL Base URL for fetching resources.
         *  @param storyName Name of the story to fetch.
         *  @param source Full TOC source data.
         *  @param permissions User permission level. Base level is 0. Reviewer level is 2. Admin level is 3.
         */
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.source = source;
        this.TOC = source.list.ChapterList;
        this.Permissions = permissions;
        // Establish accessible chapters per user criterion.
        this.ChapterBounds = { whitelist: [], full: [] };
        this.TOC.forEach((chapter) => {
            // @TODO: Implement permission levels. Will change how chapters are whitelisted.
            this.ChapterBounds.whitelist.push(chapter.Chapter);
            this.ChapterBounds.full.push(chapter.Chapter);
        });
    }
    static initialize(rootURL, storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * This is the access point for creating a ChapterBinder instance.
             * @param rootURL Base URL for fetching resources.
             * @param storyName Name of the story to fetch.
             * @return ChapterBinder instance with fetched data.
             */
            let sourceURL = `${rootURL}/TOC/TOC_${storyName}.json`;
            let source = yield TableOfContents.initialize(sourceURL);
            return new ChapterBinder(rootURL, storyName, source);
        });
    }
    doWhitelist(requestedChapter) {
        if (this.Permissions >= 1) {
            if (!this.ChapterBounds.full.includes(requestedChapter)) {
                console.warn("ChapterBinder.pullRequest", "Requested chapter is out of bounds of access.");
                return false;
            }
        }
        else {
            if (!this.ChapterBounds.whitelist.includes(requestedChapter)) {
                console.warn("ChapterBinder.pullRequest", "Requested chapter does not exist. Cannot add to binder.");
                return false;
            }
        }
        return true;
    }
    pullRequest(requestedChapter) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * Handles a chapter pull request, fetching and caching the chapter if not already present.
             * @param requestedChapter Chapter number being requested.
             * @return True if chapter was fetched and added to binder, false otherwise.
             */
            if (!this.doWhitelist(requestedChapter)) {
                return false;
            }
            let isInBinder = false;
            Object.entries(this.SessionBinder).forEach(([chapter, contents]) => {
                if (Number(chapter) == requestedChapter) {
                    console.info("ChapterBinder.pullRequest", "Requested chapter is already in binder.");
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
            return false;
        });
    }
    DeployOnPage(requestedChapter, targetElementID) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * Deploys the requested chapter's content onto the specified HTML element.
             * @param requestedChapter Chapter number being requested.
             * @param targetElementID ID of the HTML element to deploy content to.
             */
            if (!this.doWhitelist(requestedChapter)) {
                console.warn("ChapterBinder.DeployOnPage", "Chapter is not on the whitelist.");
                return false;
            }
            let isInBinder = yield this.pullRequest(requestedChapter);
            if (!isInBinder) {
                console.warn("ChapterBinder.DeployOnPage", "Error fetching chapter for deployment.");
                return false;
            }
            let targetElement = document.getElementById(targetElementID);
            if (!targetElement) {
                console.warn("ChapterBinder.DeployOnPage", "Target HTML element not found.");
                return false;
            }
            console.info("ChapterBinder.DeployOnPage", "Deploying chapter on page.");
            let ticker = this.SessionBinder[requestedChapter];
            let chapterContent = "";
            ticker.forEach((section) => {
                section.forEach((feedline) => {
                    let style = feedline[0];
                    let text = feedline[1];
                    let isEOL = feedline[2];
                    console.log(style);
                });
            });
            targetElement.innerHTML = chapterContent;
            return true;
        });
    }
}
function buildManuscript(rootURL, storyName) {
    return __awaiter(this, void 0, void 0, function* () {
        prgmScript = yield Manuscript.initialize(rootURL, storyName);
        prgmBinder = yield ChapterBinder.initialize(rootURL, storyName);
        prgmBinder.DeployOnPage(1, "content");
        return;
    });
}
var prgmScript;
var prgmBinder;
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN";
buildManuscript(rootURL, 'Paragate');
console.log(prgmScript);
