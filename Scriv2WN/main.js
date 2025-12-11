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
class ChapterDataCard {
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
        // Act, ActName, Blurb, Chapter, ChapterName, ChapterNumber, Character[], Location, Summary, Written
        this.Data.META = this.Binder.source.list.Metadata;
        // ActCount, ChapterCount, SceneCount, Summary, WrittenCount, UnwrittenCount
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
        return;
    }
    constructor(StoryName) {
        /**
         * Contains requisite data for the chapter currently loaded into the display.
         */
        this.Story = null; // Story name.
        this.Data = { TOC: null, META: null }; // Data structure for current chapter data.
        this.Binder = null; // Pointer to the ChapterBinder object.
        this.ThemeDriver = null; // Pointer to the ThemeDriver object.
        this.NightMode = false; // Is Night Mode active?
        this.Story = StoryName;
    }
    toggleNightMode(doReport = true) {
        this.NightMode = !this.NightMode;
        console.info(`Night mode is now ${this.NightMode ? "on" : "off"}.`);
        return this.NightMode;
    }
}
class StoryConfig {
    constructor(cfg, storyName) {
        /**
         *  Retrieve StoryConfig.json from the directory this file is in.
         */
        this.story = null; // Story name.
        /**
         * @param cfg Full Story Config data.
         */
        this.config = cfg;
        this.story = storyName;
        // Make some friendly names for common config items.
        return;
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
                console.debug("Manuscript.initialize", "Error fetching manuscript from URL.");
            }
            else {
                console.debug("Manuscript.initialize", "Successfully fetched manuscript from URL.");
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
    constructor(rootURL, storyName, prgmConfig, source, permissions = 0, dataCard, elementID = "", doDeployment = 1) {
        this.rootURL = ""; // Base URL for fetching resources.
        this.storyName = ""; // Name of the story to fetch.
        this.SessionBinder = {}; // In-session cache of fetched chapters.
        this.Permissions = 0; // User permission level.
        /**
         *  @param rootURL Base URL for fetching resources.
         *  @param storyName Name of the story to fetch.
         *  @param source Full TOC source data.
         *  @param permissions User permission level. Base level is 0. Reviewer level is 2. Admin level is 3.
         *  @param dataCard Current chapter data card object pointer.
         */
        this.rootURL = rootURL;
        this.storyName = storyName;
        this.source = source;
        this.TOC = source.list.ChapterList;
        this.Permissions = permissions;
        this.DataCard = dataCard;
        this.Config = prgmConfig;
        // Establish accessible chapters per user criterion.
        this.ChapterBounds = { active: [], whitelist: [], full: [] };
        this.TOC.forEach((chapter) => {
            this.ChapterBounds.whitelist.push(chapter.Chapter);
            this.ChapterBounds.full.push(chapter.Chapter);
        });
        switch (this.Permissions) {
            case 0: // Base user.
                this.ChapterBounds.active = this.ChapterBounds.whitelist;
            case 1: // Reviewer.
                this.ChapterBounds.active = this.ChapterBounds.full;
            case 2: // Admin.
                this.ChapterBounds.active = this.ChapterBounds.full;
            // @TODO: Implement permission levels. Will change how chapters are whitelisted.
        }
        // Link the DataCard back to this binder.
        this.DataCard.setBinder(this);
        if (doDeployment != 0) {
            let openingChapter = doDeployment < 1 ? 1 : this.ChapterBounds.active.includes(doDeployment) ? doDeployment : 1;
            console.info("ChapterBinder.initialize", "Deploying initial chapter to DataCard.");
            this.DeployOnPage(openingChapter, elementID);
        }
        return;
    }
    static initialize(rootURL_1, storyName_1, prgmConfig_1) {
        return __awaiter(this, arguments, void 0, function* (rootURL, storyName, prgmConfig, permissions = 0, dataCard, elementID = "", doDeployment = 1) {
            /**
             * This is the access point for creating a ChapterBinder instance.
             * @param rootURL Base URL for fetching resources.
             * @param storyName Name of the story to fetch.
             * @return ChapterBinder instance with fetched data.
             */
            let sourceURL = `${rootURL}/TOC/TOC_${storyName}.json`;
            let source = yield TableOfContents.initialize(sourceURL);
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
                chapterContent += `${this.Config.config["Bonus"][this.storyName]["Dividers"][ChapterInfo.Character[thisSection]]}`;
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
            // Update the DataCard with current chapter info.
            this.DataCard.Update(requestedChapter);
            return true;
        });
    }
}
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
        console.debug("ThemeDriver.setKeyframes", `Setting ${FrameCount} keyframes...`);
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
        console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as STATIC START`);
        // Iterations in the middle will all be the same.
        for (let i = 1; i < this.ScrollBreaks.length - 1; i++) {
            // This is an intermediate DYNAMIC transition.
            start = end;
            end = this.ScrollBreaks[i].atPoint + (this.TransitionWidth / 2);
            start_theme = this.ScrollBreaks[i - 1].Theme;
            end_theme = this.ScrollBreaks[i].Theme;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
            console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as DYNAMIC`);
            // This is an intermediate STATIC transition.
            start = end;
            end = this.ScrollBreaks[i + 1].atPoint - (this.TransitionWidth / 2);
            start_theme = this.ScrollBreaks[i].Theme;
            end_theme = this.ScrollBreaks[i].Theme;
            this.Keyframes.push({ startTheme: start_theme, endTheme: end_theme, min: start, max: end });
            console.error(`${start} to ${end} from ${start_theme} to ${end_theme} as STATIC`);
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
            let SceneContainers = this.TextContainer.childNodes;
            // Aggregate each of the heights of the scene <div> containers. Start with an empty array, and append values.
            let SceneDims = [];
            SceneContainers.forEach((sceneContainer) => {
                SceneDims.push(sceneContainer.getBoundingClientRect());
            });
            // Return the total travel height of scrolling: the total container height minus both halves of the view/bounding container.
            let TravelHeight = TotalDims.height - BoundingDims.height;
            // First scroll break is set at zero. The theme will be the first character.
            // IMPORTANT NOTE: Denotation of the character for each LINE BREAK defines the theme for the NEXT section.
            this.ScrollBreaks = [{ Theme: this.DataCard.Data.TOC.Character[0], atPercent: 0, atPoint: 0 }];
            // Sum the heights of each of the containers. This will define the SCROLL BREAK points.
            let SceneHeightSum = 0;
            for (let i = 1; i < SceneDims.length; i++) {
                SceneHeightSum += SceneDims[i - 1].height;
                let ScrollPosition = (SceneHeightSum / TravelHeight) * 100;
                this.ScrollBreaks.push({ Theme: this.DataCard.Data.TOC.Character[i], atPercent: ScrollPosition, atPoint: SceneHeightSum });
            }
            // Push the final value, at the bottom of the travel. Will have same theme as last entry to ensure constant end.
            this.ScrollBreaks.push({ Theme: this.DataCard.Data.TOC.Character[SceneDims.length - 1], atPercent: 0, atPoint: TravelHeight });
            // For debug report.
            if (doReport) {
                let report = `ThemeDriver.getScrollBreaks Report for :
    Bounding Dimensions:      Height = ${BoundingDims.height.toFixed(2)} px
    Total Dimensions:         Height = ${TotalDims.height.toFixed(2)} px
    Travel Height:            ${TravelHeight.toFixed(2)} px
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
            console.warn("ThemeDriver.getFrame", "No keyframe found for scroll position:", scrollPosition);
            return;
        }
        let KeyProgress = (scrollPosition - currentKey.min) / (currentKey.max - currentKey.min);
        let debug = document.getElementById("DEBUG");
        if (currentKey.startTheme == currentKey.endTheme) {
            if (debug != null) {
                debug.innerHTML = `<span style="color: white">Static keyframe found for scroll position ${scrollPosition.toFixed(0)} at ${(KeyProgress * 100).toFixed(2)}% <br> This is ${currentKey.startTheme} at index ${index}.<br> ${currentKey.min.toFixed(0)} to ${currentKey.max.toFixed(0)}</span>`;
            }
            this.CurrentFrame = this.ThemeData[currentKey.startTheme][darkTheme];
            return;
        }
        if (debug != null) {
            debug.innerHTML = `<span style="color: white">Interpolating keyframe for scroll position ${scrollPosition.toFixed(0)} at ${(KeyProgress * 100).toFixed(2)}% <br>From theme "${currentKey.startTheme}" to "${currentKey.endTheme}.<br> ${currentKey.min.toFixed(0)} to ${currentKey.max.toFixed(0)}"</span>`;
        }
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
            FromCharacter: this.ThemeData[currentKey.startTheme],
            ToCharacter: this.ThemeData[currentKey.endTheme]
        };
        return;
    }
    deployColors() {
        /**
         *  Set the theme: apply to CSS ROOT variables.
         */
        if (ROOT == null) {
            console.warn("ThemeDriver.deployColors", "Root HTML element not found. Cannot deploy colors.");
            return;
        }
        ROOT.style.setProperty("--TextColor", `rgba(${this.CurrentFrame["Text"][0]},${this.CurrentFrame["Text"][1]},${this.CurrentFrame["Text"][2]},${1})`);
        ROOT.style.setProperty("--BackgroundColor", `rgba(${this.CurrentFrame["Background"][0]},${this.CurrentFrame["Background"][1]},${this.CurrentFrame["Background"][2]},${1})`);
        ROOT.style.setProperty("--BarColor", `rgba(${this.CurrentFrame["ProgressBar"][0]},${this.CurrentFrame["ProgressBar"][1]},${this.CurrentFrame["ProgressBar"][2]},${1})`);
        ROOT.style.setProperty("--HoverColor", `rgba(${this.CurrentFrame["ProgressBar"][0]},${this.CurrentFrame["ProgressBar"][1]},${this.CurrentFrame["ProgressBar"][2]},${0.1})`);
        ROOT.style.setProperty("--TOCbackground", `rgba(${this.CurrentFrame["ProgressBar"][0]},${this.CurrentFrame["ProgressBar"][1]},${this.CurrentFrame["ProgressBar"][2]},${0.03})`);
        //ROOT.style.setProperty("--CodyOp",CODY_Opacity); /*CHSET["Background"][3]);/**/
        //ROOT.style.setProperty("--KatiyaOp",KAT_Opacity); /*1-CHSET["Background"][3]);/**/
        //ROOT.style.setProperty("--TitusOp",TIE_Opacity); /*1-CHSET["Background"][3]);/**/
    }
}
//                          //
//  MAIN PROGRAM EXECUTION  //
//                          //
function buildManuscript(rootURL_1, storyName_1) {
    return __awaiter(this, arguments, void 0, function* (rootURL, storyName, startChapter = 1) {
        // I gotta do this in here because if I do it outside, the await won't work.
        prgmConfig = yield StoryConfig.initialize(rootURL, storyName);
        DataCard = new ChapterDataCard(storyName);
        DataCard.toggleNightMode(false); // Start in Night Mode.
        prgmBinder = yield ChapterBinder.initialize(rootURL, storyName, prgmConfig, 0, DataCard, TextDeploymentLocation, startChapter);
        ThemeController = new ThemeDriver(prgmConfig.config, TextDeploymentLocation, DataCard, eBackground, eText, eProgressBar, true);
        return;
    });
}
function runScrollEvents() {
    ThemeController.getFrame();
    ThemeController.deployColors();
    return;
}
const ROOT = document.querySelector(':root');
const TextDeploymentLocation = "TYPESET";
var StartChapter = 30;
var DataCard;
var prgmConfig;
var prgmBinder;
var ThemeController;
var eBackground = document.getElementById("BACKGROUND");
var eText = document.getElementById("BODY");
var eProgressBar = document.getElementById("PROGRESS");
// @TODO this will be defined by a JSON config file.
var rootURL = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/Scriv2WN";
buildManuscript(rootURL, 'Paragate', StartChapter);
