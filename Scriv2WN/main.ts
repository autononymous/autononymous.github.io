class StoryConfig {
    /**
     *  Retrieve StoryConfig.json from the directory this file is in.
     */
    public config: any;                    // Full config data.
    public static data: any;               // Program data retrieved from the source.
    private constructor(config: any) {
        /**
         * @param config Full Story Config data.
         */        
        this.config = config;
    }
    static async initialize(rootURL: string) {     
        /**
         * This is the access point for creating a StoryConfig instance.
         * @param rootURL Base URL for fetching resources.
         * StoryConfig.json should be in the root directory.
         * @return Manuscript instance with fetched data.
         */   
        const response = await fetch(`${rootURL}/StoryConfig.json`);
        if (!response.ok) {
            console.debug("Manuscript.initialize","Error fetching manuscript from URL.")
        } else {
            console.debug("Manuscript.initialize","Successfully fetched manuscript from URL.")
        }
        this.data = await response.json();
        return new StoryConfig(this.data);
    }       
}

class Manuscript {
    /** Constitutes the full manuscript data structure as fetched from the source JSON file.
     *  This is an async class method; use `await Manuscript.initialize(rootURL, storyName)` to create an instance.
     */
    public rootURL: string;                 // Base URL for fetching resources.
    public storyName: string;               // Name of the story to fetch.
    public script: any;                     // Full unparsed script data.
    public static data: any;                // Program data retrieved from the source.

    private constructor(rootURL: string, storyName: string, script: any) {
        /**
         *  @param rootURL Base URL for fetching resources.
         *  @param storyName Name of the story to fetch.
         *  @param script Full unparsed script data.
         */
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.script = script;
    }
    static async initialize(rootURL: string, storyName: string) {     
        /**
         * This is the access point for creating a Manuscript instance.
         * @param rootURL Base URL for fetching resources.
         * @param storyName Name of the story to fetch.
         * @return Manuscript instance with fetched data.
         */   
        let sourceURL = `${rootURL}/output/${storyName}/MC_Latest.json`
        const response = await fetch(sourceURL);
        if (!response.ok) {
            console.debug("Manuscript.initialize","Error fetching manuscript from URL.")
        } else {
            console.debug("Manuscript.initialize","Successfully fetched manuscript from URL.")
        }
        this.data = await response.json();
        return new Manuscript(rootURL, storyName, this.data);
    }    
}

class TableOfContents {
    /**
     * Constitutes the Table of Contents data structure as fetched from the source JSON file.
     * This is an async class method; use `await TableOfContents.initialize(sourceURL)` to create an instance.
     */
    public list: any;                      // Full TOC data.
    public static data: any;               // Program data retrieved from the source.

    private constructor(toc: any) {
        /**
         * @param toc Full Table Of Contents data.
         */        
        this.list = toc;
    }

    static async initialize(sourceURL: string) {
        /**
         * This is the access point for creating a TableOfContents instance.
         * @param sourceURL URL to fetch the TOC JSON from.
         * @return TableOfContents instance with fetched data.
         */
        const response = await fetch(sourceURL);
        if (!response.ok) {
            console.debug("Manuscript.initialize","Error fetching manuscript from URL.")
        } else {
            console.debug("Manuscript.initialize","Successfully fetched manuscript from URL.")
        }
        this.data = await response.json();
        return new TableOfContents(this.data);
    }
}

class ChapterBinder {    
    /** Constitutes the Chapter Binder data structure for managing chapter access and retrieval.
     *  This is an async class method; use `await ChapterBinder.initialize(rootURL, storyName)` to create an instance.
     *  The premise behind this class is to allow on-demand fetching and caching of chapters as needed.
     */
    public source : any;                                        // Full TOC source data.
    public TOC : any;                                           // Table of Contents extracted from source.
    public rootURL : string = "";                               // Base URL for fetching resources.
    public storyName : string = "";                             // Name of the story to fetch.
    public SessionBinder : any = {};                            // In-session cache of fetched chapters.
    public ChapterBounds : {whitelist:number[], full:number[]}; // Chapter access bounds.
    public Permissions : number = 0;                            // User permission level.

    private constructor(rootURL : string, storyName: string, source : any, permissions: number = 0) {
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
        this.ChapterBounds = {whitelist:[], full:[]};
        this.TOC.forEach((chapter: any) => {
            // @TODO: Implement permission levels. Will change how chapters are whitelisted.
            this.ChapterBounds.whitelist.push(chapter.Chapter);
            this.ChapterBounds.full.push(chapter.Chapter);
        });
    }
    static async initialize(rootURL: string, storyName: string) {
        /**
         * This is the access point for creating a ChapterBinder instance.
         * @param rootURL Base URL for fetching resources.
         * @param storyName Name of the story to fetch.
         * @return ChapterBinder instance with fetched data.
         */
        let sourceURL = `${rootURL}/TOC/TOC_${storyName}.json`
        let source = await TableOfContents.initialize(sourceURL)
        return new ChapterBinder(rootURL, storyName, source);
    }
    private doWhitelist(requestedChapter: number) {
        if (this.Permissions >= 1) {
            if (!this.ChapterBounds.full.includes(requestedChapter)) {
                console.warn("ChapterBinder.pullRequest","Requested chapter is out of bounds of access.") 
                return false
            }
        } else {
            if (!this.ChapterBounds.whitelist.includes(requestedChapter)) {
                console.warn("ChapterBinder.pullRequest","Requested chapter does not exist. Cannot add to binder.") 
                return false
            }
        }
        return true
    }
    async pullRequest(requestedChapter: number) {
        /**
         * Handles a chapter pull request, fetching and caching the chapter if not already present.
         * @param requestedChapter Chapter number being requested.
         * @return True if chapter was fetched and added to binder, false otherwise.
         */
        if (!this.doWhitelist(requestedChapter)) {
            return false
        }
        
        let isInBinder: boolean = false;
        Object.entries(this.SessionBinder).forEach(([chapter, contents]) => {
            if (Number(chapter) == requestedChapter) {
                console.info("ChapterBinder.pullRequest","Requested chapter is already in binder.")
                isInBinder = true;
            }
        });     
        if (!isInBinder) { 
            let actnum = this.TOC[requestedChapter - 1].Act;
            let chapterURL = `${this.rootURL}/sectioned/${this.storyName}/${actnum}/${requestedChapter}.json`;
            const response = await fetch(chapterURL);
            if (!response.ok) {
                console.debug(`ChapterBinder.pullRequest","Error fetching manuscript from URL at ${chapterURL}.`)
                return false
            } else {
                console.debug("ChapterBinder.pullRequest","Successfully fetched manuscript from URL.")
            }
            this.SessionBinder[requestedChapter] = await response.json();
            return true
        }
        return false
    }
    async DeployOnPage(requestedChapter: number, targetElementID: string, purgeContent: boolean = true) {
        /**
         * Deploys the requested chapter's content onto the specified HTML element.
         * @param requestedChapter Chapter number being requested.
         * @param targetElementID ID of the HTML element to deploy content to.
         */
        
        // Is it on the whitelist per user's permissions?
        if (!this.doWhitelist(requestedChapter)) {
            console.warn("ChapterBinder.DeployOnPage","Chapter is not on the whitelist.")
            return false
        }
        // Is it in the binder already? If not, pull it in.
        let isInBinder: boolean = await this.pullRequest(requestedChapter);
        if (!isInBinder) {
            console.warn("ChapterBinder.DeployOnPage","Error fetching chapter for deployment.")
            return false
        }
        // Was a target element for this HTML correctly defined?
        let targetElement = document.getElementById(targetElementID);
        if (!targetElement) {
            console.warn("ChapterBinder.DeployOnPage","Target HTML element not found.")
            return false
        }
        if (purgeContent) { targetElement.innerHTML = ""; }
        // By this point, we have the chapter in the binder and a valid target element.
        console.info("ChapterBinder.DeployOnPage","Deploying chapter on page.")
        // Get chapter content from the Session Binder.
        let chapter = this.SessionBinder[requestedChapter];
        // Chapter content (HTML) starts empty.
        let chapterContent : string = "";
        // Enumerate sections since forEach doesn't iterate over a for loop index.
        let thisSection : number = 0;
        // Each chapter holds a section.
        chapter.forEach( (section: any[]) => {
            // Get chapter info from TOC for this chapter.
            let ChapterInfo = this.TOC[requestedChapter - 1]
            // Define a Section ID for this section.
            let SectionID = `${requestedChapter}.${thisSection+1}`;
            // Start with a <div> element. @TODO may change this later.
            chapterContent += `<div class='section' id='${SectionID}'>`;
            // Get the three datums in every feedline: [style, body text, is End Of Line]
            let wasEOL : boolean = true;  // start true to get first <p> tag
            let thisLine : number = 0;
            let thisFragment : number = 0;
            // Each section holds multiple fragments. The End Of Line indicator defines the end of a Line.
            // It is in fragments, because a line may have multiple styles within it as <span>s.
            section.forEach( (feedline: any[]) => {
                // The Section Style is an array containing the perspective of each section e.g. [Cody, Katiya, Titus, ...]
                let SectionStyle : string = ChapterInfo.Character[thisSection];
                // Chapter.Section.Line
                let LineID = `${requestedChapter}.${thisSection+1}.${thisLine+1}`;
                let style : string = feedline[0];
                let text : string = feedline[1];
                let isEOL : boolean = Boolean(feedline[2]);
                // New line means new <p> tag.
                if (wasEOL) {
                    chapterContent += `<p class='Body${SectionStyle}' id='${LineID}'>`;
                    thisFragment = 0;
                }
                // Chapter.Section.Line.Fragment
                let FragmentID = `${LineID}.${thisFragment+1}`;
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
        return true
    }
}




//                          //
//  MAIN PROGRAM EXECUTION  //
//                          //

async function buildManuscript(rootURL: string, storyName: string ) {
    // I gotta do this in here because if I do it outside, the await won't work.
    prgmConfig = await StoryConfig.initialize(rootURL);
    prgmBinder = await ChapterBinder.initialize(rootURL, storyName);
    prgmBinder.DeployOnPage(1, "TYPESET")
    return
}

var prgmConfig: any;
var prgmBinder: any;
// @TODO this will be defined by a JSON config file.
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN"

buildManuscript(rootURL,'Paragate');