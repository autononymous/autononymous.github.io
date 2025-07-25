var BLACKBOOK = [];
class taskitem {
    constructor(mode=1,title="Title",subject="Subject",premise="",color=[220,20,20],parent=undefined) {
        this.mode = mode;
        this.title = title;
        this.subject = subject;
        this.premise = premise;
        this.color = (parent == undefined) ? color : parent.color;
        this.analog = [0,0,0];
        this.slider = 0.01;
        this.id = Math.round(Math.random()*100000);
        this.children = [];
        this.parent = parent;
    }
    set AppendItem(child) {
        child.parent = this;
        this.children.push(child);
        BLACKBOOK.push(child);
    }
}

var firstelem = BLACKBOOK.push(new taskitem(0,"Category Name","for a category","to categorize things"));
BLACKBOOK[0].AppendItem = new taskitem(1,"First item","with description","and stuff about it",parent=firstelem);
BLACKBOOK[0].AppendItem = new taskitem(3,"Second item","with description","and stuff about it",parent=firstelem);
BLACKBOOK[0].AppendItem = new taskitem(4,"Third item","with description","and stuff about it",parent=firstelem);

const EntryTypes = ["Header","1-Box","2-Box","3-Box","Slider"];

var SelectedParent = null;
var SelectedObject = null;

function ChooseItem(elem) {
    SelectedObject = elem;
    SelectedParent = elem.parentElement;
    eIDBOX.innerHTML = `ID ${SelectedParent.id}<br>${SelectedParent.innerText}<br>${EntryTypes[SelectedParent.id.slice(0,1)]}`;
    sTYPE.value = SelectedParent.id.slice(0,1);
    //sTITLE.value = 
    //sSUB.value = 
}
function ModifyItem() {

}
function AppendItem() {

}
function FormattedHTML(entry) {
    //console.log(entry.mode)
    let result = "";
    let color = `rgb(${entry.color[0]},${entry.color[1]},${entry.color[2]})`;
    switch(entry.mode) {
    case 0:     // Header
        result = `<div id="${entry.id}" style="color: ${color}; border-color: ${color};" class="T-CATEGORY">
                    <div id="T-${entry.id}" class="T-TITLE" style="" onclick="ChooseItem(this)">Category Name</div>
                 </div>`;
        break
    case 1:     // 1-box
        result = `<div id="${entry.id}" style="color: ${color}; border-color: ${color};" class="T-ITEM" onclick="ChooseItem(this)">
                    <div class="T-BOXES">
                        <div id="B1-${entry.id}" class="T-BOX" onclick="ToggleBox(this)"></div>
                    </div>
                    <div class="T-ITEMTITLE">${entry.title}</div>
                    <div class="T-ITEMSUB">${entry.subject}</div>
                 </div>`;
        break
    case 2:     // 2-box
        result = `<div id="${entry.id}" style="color: ${color}; border-color: ${color};" class="T-ITEM" onclick="ChooseItem(this)">
                    <div class="T-BOXES">
                        <div id="B1-${entry.id}" class="T-BOX" onclick="ToggleBox(this)"></div>
                        <div id="B2-${entry.id}" class="T-BOX" onclick="ToggleBox(this)"></div>
                    </div>
                    <div class="T-ITEMTITLE">${entry.title}</div>
                    <div class="T-ITEMSUB">${entry.subject}</div>
                 </div>`;
        break
    case 3:     // 3-box
        result = `<div id="${entry.id}" style="color: ${color}; border-color: ${color};" class="T-ITEM" onclick="ChooseItem(this)">
                    <div class="T-BOXES">
                        <div id="B1-${entry.id}" class="T-BOX" onclick="ToggleBox(this)"></div>
                        <div id="B2-${entry.id}" class="T-BOX" onclick="ToggleBox(this)"></div>
                        <div id="B3-${entry.id}" class="T-BOX" onclick="ToggleBox(this)"></div>
                    </div>
                    <div class="T-ITEMTITLE">${entry.title}</div>
                    <div class="T-ITEMSUB">${entry.subject}</div>
                 </div>`;
        break
    case 4:     // Slider
        result = `<div id="${entry.id}" style="color: ${color}; border-color: ${color};" class="T-ITEM" onclick="ChooseItem(this)">
                    <div class="T-BOXES">
                        <div id="S1-${entry.id}" class="T-SLIDER" onclick="ToggleBox(this)"></div>
                    </div>
                    <div class="T-ITEMTITLE">${entry.title}</div>
                    <div class="T-ITEMSUB">${entry.subject}</div>
                 </div>`;
        break
    default:
        result = ``;
        break
    }
    return result
}
//console.error(BLACKBOOK)
function WriteBook() {
    eTASKS.innerHTML = "";
    Object.entries(BLACKBOOK).forEach( ([index,entry]) => {
        let target = undefined;
        //console.warn(entry.parent)
        if (entry.parent == undefined) {target = eTASKS}
        else {target = document.getElementById(entry.parent.id)}
        target.innerHTML += FormattedHTML(entry);
    });
}

WriteBook();