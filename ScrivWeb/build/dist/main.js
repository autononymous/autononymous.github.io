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
    /**
     * Constructor set to be private, ensures all consumers
     * of class use the factory function as an entry point.
     * A factory function is used to allow for async initialization.
     */
    constructor(rootURL, storyName, script) {
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.script = script;
    }
    static unpackScript() {
        this.META = this.data["Metadata"];
        this.ACT_COUNT = this.data["ActCount"];
        this.CHAPTER_COUNT = this.data["ChapterCount"];
        this.SCENE_COUNT = this.data["SceneCount"];
        this.FEED = this.data["Story"];
        return;
    }
    static initialize(rootURL, storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            let sourceURL = `${rootURL}/output/${storyName}/MC_Latest.json`;
            const response = yield fetch(sourceURL);
            if (!response.ok) {
                console.debug("Manuscript.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
            }
            this.data = yield response.json();
            this.unpackScript();
            return new Manuscript(rootURL, storyName, this.data);
        });
    }
}
class TableOfContents {
    constructor(toc) {
        this.list = toc;
    }
    static initialize(sourceURL) {
        return __awaiter(this, void 0, void 0, function* () {
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
        this.rootURL = "";
        this.storyName = "";
        this.SessionBinder = {};
        this.Permissions = 0;
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.source = source;
        this.TOC = source.list.ChapterList;
        this.Permissions = permissions;
        // Establish accessible chapters per user criterium.
        this.ChapterBounds = { whitelist: [], full: [] };
        this.TOC.forEach((chapter) => {
            // @TODO: Implement permission levels. Will change how chapters are whitelisted.
            this.ChapterBounds.whitelist.push(chapter.Chapter);
            this.ChapterBounds.full.push(chapter.Chapter);
        });
    }
    static initialize(rootURL, storyName) {
        return __awaiter(this, void 0, void 0, function* () {
            let sourceURL = `${rootURL}/TOC/TOC_${storyName}.json`;
            let source = yield TableOfContents.initialize(sourceURL);
            return new ChapterBinder(rootURL, storyName, source);
        });
    }
    pull(requestedChapter) {
        return __awaiter(this, void 0, void 0, function* () {
            //! Add this into the binder of chapters for later retrieval by retrieve().
            if (this.Permissions >= 1) {
                if (this.ChapterBounds.full.includes(requestedChapter)) {
                    let wasPulled = false;
                    this.SessionBinder.forEach((entry) => {
                        if (entry.Chapter == requestedChapter) {
                            wasPulled = true;
                        }
                    });
                    if (!wasPulled) {
                        let actnum = this.TOC[requestedChapter - 1].Act;
                        let chapterURL = `${this.rootURL}/sectioned/${this.storyName}/${actnum}/${requestedChapter}.json`;
                        const response = yield fetch(chapterURL);
                        if (!response.ok) {
                            console.debug(`Manuscript.initialize","Error fetching manuscript from URL at ${chapterURL}.`);
                        }
                        else {
                            console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
                        }
                        this.SessionBinder[requestedChapter] = yield response.json();
                    }
                    else {
                        console.info("ChapterBinder.pull", "Requested chapter is already in binder.");
                    }
                }
                else {
                    console.warn("ChapterBinder.retrieve", "Requested chapter is out of bounds of access.");
                }
            }
            else {
                if (this.ChapterBounds.whitelist.includes(requestedChapter)) {
                }
                else {
                    console.warn("ChapterBinder.retrieve", "Requested chapter does not exist. Cannot add to binder.");
                }
            }
            return;
        });
    }
}
function buildManuscript(rootURL, storyName) {
    return __awaiter(this, void 0, void 0, function* () {
        let Script = yield Manuscript.initialize(rootURL, storyName);
        let Binder = yield ChapterBinder.initialize(rootURL, storyName);
        console.log(Script);
        console.log(Binder);
        return { Script, Binder };
    });
}
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN";
var result = buildManuscript(rootURL, 'Paragate');
