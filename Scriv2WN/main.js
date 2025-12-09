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
    constructor(sourceURL, script) {
        this.sourceURL = sourceURL;
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
            this.unpackScript();
            return new Manuscript(sourceURL, this.data);
        });
    }
}
class TableOfContents {
    constructor(sourceURL, toc) {
        this.TOC = toc;
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
            return new TableOfContents(sourceURL, this.data);
        });
    }
}
class ChapterBinder {
}
function buildManuscript() {
    return __awaiter(this, void 0, void 0, function* () {
        const addr_script = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN/output/Paragate/MC_Latest.json";
        const addr_toc = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN/TOC/TOC_Paragate.json";
        const Script = yield Manuscript.initialize(addr_script);
        const TOC = yield TableOfContents.initialize(addr_toc);
        console.log(TOC);
        return;
    });
}
buildManuscript();
