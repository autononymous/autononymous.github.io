class taskitem {
    constructor(mode=1,title="Title",subject="Subject",premise="") {
        this.mode = mode;
        this.title = title;
        this.subject = subject;
        this.premise = premise;
        this.analog = [0,0,0];
        this.slider = 0.01;
        this.id = Math.round(Math.random()*10000);
    }
}

const EntryTypes = ["Header","1-Box","2-Box","3-Box","Slider"];

var SelectedParent = null;
var SelectedObject = null;

function ChooseItem(elem) {
    SelectedObject = elem;
    SelectedParent = elem.parentElement;
    eIDBOX.innerHTML = `ID ${SelectedParent.id}<br>${SelectedParent.innerText}<br>${EntryTypes[SelectedParent.id.slice(0,1)]}`;
    sTYPE.value = SelectedParent.id.slice(0,1);
    sTITLE.value = 
    sSUB.value = 
}
function ModifyItem() {

}
function AppendItem() {

}