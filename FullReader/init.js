
const LOC   = "https://raw.githubusercontent.com/autononymous/autononymous.github.io/refs/heads/master/FullReader/config.json";


async function initialize() 
{
    try {
        const response = await fetch(LOC);
        if (!response.ok) {
            console.error("Error pulling init JSON.")
        }
        let data = await response.text();
        let result = JSON.parse(data.replaceAll(/(\r\n|\n|\r)/gm, ''));
        return result;
    } catch (error) {
        console.error("Error in fetch process for init.")
    }
}
function allocate()
{
    const ROOT  = document.querySelector(':root');
    let StyleNum = 0;
    Object.values(CFG.Styles).forEach( style => {      
        console.log(style.Header.Font)
        ROOT.style.setProperty(`--T${StyleNum}_TitleFont`   ,style.Header.Font);
        ROOT.style.setProperty(`--T${StyleNum}_TextFont`    ,style.Body.Font);
        ROOT.style.setProperty(`--T${StyleNum}_SubFont`     ,style.Section.Font);    
        ROOT.style.setProperty(`--T${StyleNum}_Background`  ,`linear-gradient(to right,${style.BackgroundGradient.Outer} 0%,${style.BackgroundGradient.Inner} 10%, ${style.BackgroundGradient.Inner} 90%, ${style.BackgroundGradient.Outer} 100%),url(${style.BackgroundGradient.Image});`);    
        StyleNum++;
    });
  }

async function main() 
{
    CFG = await initialize();
    allocate();
}


main();


