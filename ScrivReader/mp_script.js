

var MiddleOfPage;
var CurrentIndex = 0;
var CurrentPage = PAGES[CurrentIndex];
var ScrollIdlePos = 0;

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
            console.log(index,condition,sheet)
            sheet.style.setProperty("opacity",condition);
            sheet.style.setProperty("pointer-events",((condition == 0) ? "none" : "all"));
        })
    }
}
function ReturnPage()
{
    MiddleOfPage = eVIEWER.getBoundingClientRect().width/2;
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
    console.log(LatestReleases)
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
async function DeployStoryTitles() {
    let newHTML = ""
    Object.entries(LOCATIONS).forEach( ([title,data]) => {
         let link = `scrivreader.html?story=${title}`
        newHTML += `
        <div id="book-${title}" style="background-image: url(${data.StoryRoot + data.CoverImage});" onclick="window.location='${link}' "></div>
        `;
    });
    eBOOKSHELF.innerHTML = newHTML;
}


async function PopulateMainPage() {
    await RetrieveLatestStories(5);
    await DeployLatestStories();
    await DeployStoryTitles();
}

eSLIDER.addEventListener("scroll",ScrollForPage);
eSLIDER.addEventListener("resize",AlignSlider);



