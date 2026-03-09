

var MiddleOfPage;
var CurrentIndex = 0;
var CurrentPage = PAGES[CurrentIndex];
var ScrollIdlePos = 0;
const WhatIsANewRelease = 14;

const StoryPremises = {
    "Firebrand":
       "<br><hr><p style='text-align: center; font-weight: 600; font-size: 1.2rem; font-variant: small-caps;'>Time Travel &centerdot; Fantasy &centerdot; Drama</p><hr><p>With unlimited chances to rewrite the past, would you find peace in imperfection — or lose yourself in eternity?</p><p><strong>“Firebrand”</strong> (Book One of The Frostburn Chronicles) follows Titus Berguard, a valedictorian from a military academy in a frostbitten wasteland. As graduation nears, Titus and his friends—Sylvia, Romin, and Valentina—face the looming threat of service. When disaster strikes the last human city, Titus discovers he can rewrite the past. But with each reset, his friends forget everything, and Titus is left alone with the weight of every outcome.</p><p>Torn by guilt and loneliness, Titus battles his need for perfection and the decay of his sanity. <em>Firebrand</em> is a story of time travel, romance, friendship, and never giving up hope in a dying world.</p>",
    "Paragate":
        "<br><hr><p style='text-align: center; font-weight: 600; font-size: 1.2rem; font-variant: small-caps;'>Contemporary &centerdot; Fantasy &centerdot; Enemies to Lovers</p><hr><p><strong>PARAGATE: Fate Across Worlds</strong> is a new-adult romance web novel where two strangers, divided by realities, discover a mysterious doorway linking their worlds. Katiya, a fierce warrior-in-training, is burdened by the fear of being sent to the front lines. Meanwhile, Cody, a disillusioned office worker, struggles against corporate monotony. The two protagonists collide in a reluctant partnership, and as they navigate their shared space, romantic tension builds, challenging them to face their deepest fears and desires.</p><p>Will their bond help them survive the trials of love, Essence, and the brutality of war, or will it tear them apart? Follow this romance novel for twists, adventure, and passionate moments that cross worlds.</p>"
}

var TableOfContents = {};

function ScrollForPage()
{
    if (Math.abs(eSLIDER.scrollLeft - ScrollIdlePos) < 10) {
        return
    }
    let CheckedPage; let CheckedIndex;
    [CheckedPage,CheckedIndex] = ReturnPage();
    if (CurrentPage != CheckedPage) {
        //console.log(`Changed to "${CurrentPage.innerHTML}" at index ${CheckedIndex}.`)
        CurrentPage = CheckedPage; 
        CurrentIndex = CheckedIndex;
        Object.entries(SHEETS).forEach( ([index,sheet]) => {
            let condition = 1 * (index == CheckedIndex);
            //console.log(index,condition,sheet)
            sheet.style.setProperty("opacity",condition);
            sheet.style.setProperty("pointer-events",((condition == 0) ? "none" : "all"));
            sheet.style.setProperty("height",((condition == 0) ? "0px" : ""));
        })
    }
}
function ReturnPage()
{
    MiddleOfPage = eALL.getBoundingClientRect().width/2;
    let SelectedPage = PAGES[0];
    let SelectedIndex = 0;
    let MinDistance = Infinity;
    Object.entries(PAGES).forEach( ([index,page]) => {
        let thispage = page.getBoundingClientRect()
        let distance = Math.abs(MiddleOfPage - (thispage.left + (thispage.width/2)));
        if(MinDistance > distance) {
            SelectedPage = page;
            MinDistance = distance;
            SelectedIndex = index;
            
        }
    })
    //console.log(`Page ${SelectedIndex}: ${MinDistance}`);
    
    //console.log(ScrollIdlePos,eSLIDER.scrollLeft)
    return [SelectedPage,SelectedIndex];
}
function AlignSlider()
{
    if (Math.abs(eSLIDER.scrollLeft - ScrollIdlePos) < 10) {
        return
    }
    ScrollIdlePos = eSLIDER.scrollLeft - (MiddleOfPage - (PAGES[CurrentIndex].getBoundingClientRect().left + (PAGES[CurrentIndex].getBoundingClientRect().width/2)));   
    eSLIDER.scrollLeft = ScrollIdlePos;
}

async function RetrieveTableOfContents() {
    TableOfContents = await GetJSONFromSource(ScrivReaderSOURCE+'story/process/MasterTOC.JSON')
}
/*
async function RetrieveLatestStories(count = 5) { 
    let HighestRelease = 0;
    STORIES.forEach( story => {
        Object.values(story).forEach( chapter => {
            OrderedReleases.push([chapter.Release,chapter])
            HighestRelease = (chapter.Release>HighestRelease) ? chapter.Release : HighestRelease;
        });
    });
    let SortedReleases = OrderedReleases.sort();
    for (let i=0; i<OrderedReleases.length; i++) {
        if( SortedReleases[i][0] > dNOW) {      
            for (let j=0; j<count; j++) {
                LatestReleases[j] = SortedReleases[i-(count-j)][1]
            }
            if( SortedReleases[i-(count+1) == SortedReleases[i-count]]) {
                LatestReleases.push(SortedReleases[i-(count+1)][1])
            }
            break
        }
    }
    //console.log(LatestReleases)
}
    
async function DeployLatestStories() {
    let newHTML = "";
    LatestReleases.forEach( release => {
        let link = `scrivreader.html?story=${release.Story}&chapter=${release.ChapterNumber-1}`
        newHTML += `
        <div class="Release${release.Story} Wall${release.Perspective}" onclick="window.location='${link}'  ">
            <div class="R-ICON ${release.Story}Icon"></div>
            <div class="R-STORY ${release.Perspective}Head">${dateyear(release.Release)}&ensp;|&ensp; ${release.Story} ${release.ID}</div>
            <div class="R-NAME ${release.Perspective}Head"><em>"${release.Subtitle}"</em></div>
            <div class="R-BODY ${release.Perspective}Body">${release.Synopsis}</div>
        </div>
        `
    })
    eRELEASES.innerHTML = newHTML;
}
    */
async function DeployTableOfContents() {
    let newHTML = ""
    let InactiveCount = 0;
    let FirstNew = true;
    TableOfContents.reverse().forEach(release => {
        let perspective = (Object.keys(SOURCE.Shorthands.Names).includes(release.Perspective)) ? release.Perspective : "Mixed";
        let link = `scrivreader.html?story=${release.Story}&chapter=${release.ChapterNumber-1}`
        let newbadge = parseInt(release.Release) >= (dNOW - WhatIsANewRelease) ? "<span class='NEWBADGE'>NEW</span>" : "";
        if (parseInt(release.Release) <= dNOW) {
            newHTML += `
            ${FirstNew ? '<hr class="nowHR"><div class="nowDIV">TODAY</div>' : ''}
            <div class="RELEASEBIN">
                <div class="RELEASE Release${release.Story} Wall${release.Story}" onclick="window.location='${link}'  ">
                    <div class="R-ICON ${release.Story}Icon"><img src="icons/logo-${perspective}.png"/></div>
                    <div class="R-STORY ${perspective}Head"><span class="datenum">${dateyear(release.Release)}</span>&ensp;|&ensp;${newbadge} ${release.Story} ${release.ID}</div>
                    <div class="R-NAME ${perspective}Head"><em>"${release.Subtitle}"</em></div>
                    <div class="R-BODY ${perspective}Body">${release.Synopsis}&ensp;</div>
                </div>
            </div>
            `;
            FirstNew = false;
        } else {
            newHTML += `
            <div class="RELEASEBIN">
                <div class="RELEASE Release${release.Story} WallInactive">
                    <div class="R-INACTIVE R-ICON ${release.Story}Icon"><img src="icons/logo-${perspective}.png" style="opacity:0.3;"/></div>
                    <div class="R-INACTIVE R-STORY ${perspective}Head"><span class="datenum">${dateyear(release.Release)}</span>&ensp;|&ensp; ${release.Story} ${release.ID}</div>
                    <div class="R-INACTIVE R-NAME ${perspective}Head"><em>"${release.Subtitle}"</em></div>
                    <div class="R-INACTIVE R-BODY ${perspective}Body">${release.Synopsis}&ensp;</div>
                </div>
                <div class="WallInactiveTag">&#128274; ${parseInt(release.Release) - dNOW}d</div>                
            </div>
            `   
            InactiveCount++;
        }
        
    });
    eRELEASES.innerHTML = newHTML + "<br><br><br><br><br><br><br>";
    eRELEASES.scrollTop = `${(80 * InactiveCount) - 30}`
}

async function DeployStoryTitles() {
    let newHTML = ""
    let firsttitle = "";
    let firstlink = "";
    let isfirst = true;
    Object.entries(LOCATIONS).forEach( ([title,data]) => {
        let link = `scrivreader.html?story=${title}`
        if(isfirst) {
            isfirst = false;
            firsttitle = title;
            firstlink = link;
        }        
        newHTML += `
        <div id="book-${title}" style="background-image: url(${data.StoryRoot + data.CoverImage});" onclick=" ViewedStory(this,'${title}', '${link}'); "></div>
        `;
    });
    eBOOKSHELF.innerHTML = newHTML;
    ViewedStory(Object.values(eBOOKSHELF.getElementsByTagName('DIV'))[0],firsttitle,firstlink)
}

function ViewedStory(elem,title,url) {
    eBOOKDATA.innerHTML = `        
        <div id="ViewedSynopsis" class="ViewedSynopsis"><a class="readbutton" href="${url}">Read Story</a>${StoryPremises[title]}</div>
    `
    /*<div id="ViewedImage" class="ViewedImage"><img src="${url}"/></div>*/   

    Object.values(eBOOKSHELF.getElementsByTagName('DIV')).forEach(cover => {
        //console.log(cover)
        cover.style.setProperty("border","");
        cover.style.setProperty("box-shadow","");
    })

    elem.style.setProperty("border","2px solid var(--AccentThreeLight)");
    elem.style.setProperty("box-shadow","0px 0px 5px 2px var(--AccentThreeLight)");
    eBOOKDATA.style.setProperty("box-shadow",`0px 0px 10px 6px black`);
}

async function PopulateMainPage() {
    await RetrieveTableOfContents();
    //await RetrieveLatestStories(5);
    //await DeployLatestStories();
    await DeployTableOfContents();
    await DeployStoryTitles();
}

eSLIDER.addEventListener("scroll",ScrollForPage);
eSLIDER.addEventListener("resize",AlignSlider);
eSLIDER.addEventListener("wheel", function(e) {
    if (e.deltaY !== 0) {
        e.preventDefault();
        eSLIDER.scrollTo({
            left: eSLIDER.scrollLeft + (e.deltaY*0.99),
            behavior: "smooth"
        });
    }
}, { passive: false });

