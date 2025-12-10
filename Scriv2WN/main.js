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
class StoryConfig {
    constructor(config) {
        /**
         * @param config Full Story Config data.
         */
        this.config = config;
    }
    static initialize(rootURL) {
        return __awaiter(this, void 0, void 0, function* () {
            /**
             * This is the access point for creating a StoryConfig instance.
             * @param rootURL Base URL for fetching resources.
             * StoryConfig.json should be in the root directory.
             * @return Manuscript instance with fetched data.
             */
            const response = yield fetch(`${rootURL}/StoryConfig.json`);
            if (!response.ok) {
                console.debug("Manuscript.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
            }
            this.data = yield response.json();
            return new StoryConfig(this.data);
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
    DeployOnPage(requestedChapter_1, targetElementID_1) {
        return __awaiter(this, arguments, void 0, function* (requestedChapter, targetElementID, purgeContent = true) {
            /**
             * Deploys the requested chapter's content onto the specified HTML element.
             * @param requestedChapter Chapter number being requested.
             * @param targetElementID ID of the HTML element to deploy content to.
             */
            // Is it on the whitelist per user's permissions?
            if (!this.doWhitelist(requestedChapter)) {
                console.warn("ChapterBinder.DeployOnPage", "Chapter is not on the whitelist.");
                return false;
            }
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
            // Enumerate sections since forEach doesn't iterate over a for loop index.
            let thisSection = 0;
            // Each chapter holds a section.
            chapter.forEach((section) => {
                // Get chapter info from TOC for this chapter.
                let ChapterInfo = this.TOC[requestedChapter - 1];
                // Define a Section ID for this section.
                let SectionID = `${requestedChapter}.${thisSection + 1}`;
                // Start with a <div> element. @TODO may change this later.
                chapterContent += `<div class='section' id='${SectionID}'>`;
                // Get the three datums in every feedline: [style, body text, is End Of Line]
                let wasEOL = true; // start true to get first <p> tag
                let thisLine = 0;
                let thisFragment = 0;
                // Each section holds multiple fragments. The End Of Line indicator defines the end of a Line.
                // It is in fragments, because a line may have multiple styles within it as <span>s.
                section.forEach((feedline) => {
                    // The Section Style is an array containing the perspective of each section e.g. [Cody, Katiya, Titus, ...]
                    let SectionStyle = ChapterInfo.Character[thisSection];
                    // Chapter.Section.Line
                    let LineID = `${requestedChapter}.${thisSection + 1}.${thisLine + 1}`;
                    let style = feedline[0];
                    let text = feedline[1];
                    let isEOL = Boolean(feedline[2]);
                    // New line means new <p> tag.
                    if (wasEOL) {
                        chapterContent += `<p class='Body${SectionStyle}' id='${LineID}'>`;
                        thisFragment = 0;
                    }
                    // Chapter.Section.Line.Fragment
                    let FragmentID = `${LineID}.${thisFragment + 1}`;
                    // Here is the actual TEXT addition.
                    chapterContent += `<span class='${style}' id='${FragmentID}'>${text}</span>`;
                    // End of line means closing </p> tag.
                    if (isEOL) {
                        chapterContent += "</p>";
                        thisLine += 1;
                    }
                    thisFragment += 1;
                    wasEOL = isEOL;
                });
                // End of section. Close out with </div>.
                chapterContent += "</div>";
                thisSection += 1;
            });
            // Actual deployment of chapter content to target element.
            targetElement.innerHTML = chapterContent;
            return true;
        });
    }
}
//                          //
//  MAIN PROGRAM EXECUTION  //
//                          //
function buildManuscript(rootURL, storyName) {
    return __awaiter(this, void 0, void 0, function* () {
        // I gotta do this in here because if I do it outside, the await won't work.
        prgmConfig = yield StoryConfig.initialize(rootURL);
        prgmBinder = yield ChapterBinder.initialize(rootURL, storyName);
        prgmBinder.DeployOnPage(1, "TYPESET");
        return;
    });
}
var prgmConfig;
var prgmBinder;
// @TODO this will be defined by a JSON config file.
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN";
buildManuscript(rootURL, 'Paragate');
