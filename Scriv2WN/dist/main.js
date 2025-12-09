"use strict";
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
    static async initialize(sourceURL) {
        const response = await fetch(sourceURL);
        if (!response.ok) {
            console.debug("Manuscript.initialize", "Error fetching manuscript from URL.");
        }
        else {
            console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
        }
        const data = await response.json();
        return new Manuscript(sourceURL, data);
    }
}
/**

    ParseJSON(source) {
        parsed = JSON.parse(source.replaceAll(/(\r\n|\n|\r)/gm, ''));
        console.debug("Fetched JSON item.")
        return parsed
    }
    async RetrieveJSON(location) {
        try {
            const response = await fetch(location);
            if (!response.ok) {
                console.debug("initialize.js > GetJSONFromSource","Error pulling JSON item.")
            }
            let data = await response.text();
            let result = await this.ParseJSON(data)
            return result;
        } catch (error) {
            console.debug("initialize.js > GetJSONFromSource","Error processing JSON item from URL.")
        }
    }
    async RetrieveManuscript() {
        this.script = await this.RetrieveJSON(this.sourceURL);
        this.GetMetadata();
        return
    }
    GetMetadata() {
        this.data = this.script.Metadata;
        this.acts = this.script.ActCount;
        this.chapters = this.script.ChapterCount;
        this.scenes = this.script.SceneCount;
        this.feed = this.script.Story;
        return
    }
    ManuscriptToHTML() {
        let bodyHTML = "";
        return bodyHTML
    }
    async Process() {
        await this.RetrieveManuscript();
    }
}

**/
async function buildManuscript() {
    const addr = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN/output/MasterTOC_Paragate.json";
    const Script = await Manuscript.initialize(addr);
}
buildManuscript();
