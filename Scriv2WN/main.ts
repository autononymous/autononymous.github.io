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
    async DeployOnPage(requestedChapter: number, targetElementID: string) {
        /**
         * Deploys the requested chapter's content onto the specified HTML element.
         * @param requestedChapter Chapter number being requested.
         * @param targetElementID ID of the HTML element to deploy content to.
         */
        if (!this.doWhitelist(requestedChapter)) {
            console.warn("ChapterBinder.DeployOnPage","Chapter is not on the whitelist.")
            return false
        }
        let isInBinder: boolean = await this.pullRequest(requestedChapter);
        if (!isInBinder) {
            console.warn("ChapterBinder.DeployOnPage","Error fetching chapter for deployment.")
            return false
        }
        let targetElement = document.getElementById(targetElementID);
        if (!targetElement) {
            console.warn("ChapterBinder.DeployOnPage","Target HTML element not found.")
            return false
        }
        console.info("ChapterBinder.DeployOnPage","Deploying chapter on page.")
        let ticker = this.SessionBinder[requestedChapter];
        let chapterContent : string = "";
        ticker.forEach( (section: any[]) => {
            section.forEach( (feedline: any[]) => {
                let style = feedline[0];
                let text = feedline[1];
                let isEOL = feedline[2];
                console.log(style);
            });
        });
        targetElement.innerHTML = chapterContent;
        return true
    }
}

async function buildManuscript(rootURL: string, storyName: string) {
    prgmScript = await Manuscript.initialize(rootURL, storyName);
    prgmBinder = await ChapterBinder.initialize(rootURL, storyName);
    prgmBinder.DeployOnPage(1, "content")
    return
}

var prgmScript: any;
var prgmBinder: any;
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN"
buildManuscript(rootURL,'Paragate');
console.log(prgmScript);