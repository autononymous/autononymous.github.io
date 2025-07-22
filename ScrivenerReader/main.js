
function SetPreferences(property,increment) {
    let Params = SETTINGS[property];
    let range = [ 0 , Params.Options.length ];
    let current = Params.Setting;
    let queried = current + increment;

    if (queried >= range[0] && queried < range[1]) {
        Params.Setting = queried;
        PREFERENCES[property] = Params.Options[queried];
        ROOT.style.setProperty(Params.CSSname,PREFERENCES[property])
        DConsole("main.js > SetPreferences",`Parameter '${property}' is now set to ${PREFERENCES[property]}.`)

        SaveLocalData();

        SetScrollerEvents();
        runScrollEvents();

    } else {
        DConsole("main.js > SetPreferences",`NOTICE: Parameter setting for '${property}' is out of bounds [${range[0]},${range[1]}].`,true)
    }
}

async function main() 
{

}