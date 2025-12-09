class Manuscript {
    public sourceURL: string;
    public script: any;
    public static data: any;
    public static META: any;
    public static ACT_COUNT: number;
    public static CHAPTER_COUNT: number;
    public static SCENE_COUNT: number;
    public static FEED: any;
    /**
     * Constructor set to be private, ensures all consumers
     * of class use the factory function as an entry point.
     * A factory function is used to allow for async initialization.
     */
    private constructor(sourceURL: string, script: any) {
        this.sourceURL = sourceURL;
        this.script = script;
    }
    static unpackScript() {        
        this.META = this.data["Metadata"];
        this.ACT_COUNT = this.data["ActCount"];
        this.CHAPTER_COUNT = this.data["ChapterCount"];
        this.SCENE_COUNT = this.data["SceneCount"];
        this.FEED = this.data["Story"];
        return
    }
    static async initialize(sourceURL: string) {
        const response = await fetch(sourceURL);
        if (!response.ok) {
            console.debug("Manuscript.initialize","Error fetching manuscript from URL.")
        } else {
            console.debug("Manuscript.initialize","Successfully fetched manuscript from URL.")
        }
        this.data = await response.json();
        this.unpackScript();
        return new Manuscript(sourceURL, this.data);
    }
    
}

class TableOfContents {
    public TOC: any;
    public static data: any;

    private constructor(sourceURL: string, toc: any) {
        this.TOC = toc;
    }

    static async initialize(sourceURL: string) {
        const response = await fetch(sourceURL);
        if (!response.ok) {
            console.debug("Manuscript.initialize","Error fetching manuscript from URL.")
        } else {
            console.debug("Manuscript.initialize","Successfully fetched manuscript from URL.")
        }
        this.data = await response.json();
        return new TableOfContents(sourceURL, this.data);
    }
}

class ChapterBinder {

}


async function buildManuscript() {
    const addr_script = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN/output/Paragate/MC_Latest.json"
    const addr_toc = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN/TOC/TOC_Paragate.json"
    const Script = await Manuscript.initialize(addr_script)
    const TOC = await TableOfContents.initialize(addr_toc)
    console.log(TOC)
    return;
}
buildManuscript();