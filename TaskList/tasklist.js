var TASKS = {};

function diffstar(diff) {
    let result = "";
    for (let i=0; i<Math.round(diff-0.5,0); i++) {
        result += "S";
    }
    if (diff % 1 >= 0.5) {
        result += "s";
    }
    return result;
}

const CMDbox = document.getElementById('cmdbox');
const CMD = document.getElementById('command');

function init() {
    let dat = localStorage.getItem('TaskMgrData');
    if (dat != null) {
        console.info('Loading existing task data.')
        TASKS = JSON.parse(dat);
        Object.entries(TASKS).forEach(([id,task]) => {
            taskgen(task,id)
        })
    } else {       
        console.info('No existing task data. Creating new.') 
        taskgen(TemplateItem);
    }
}

function SaveState() {
    localStorage.setItem('TaskMgrData', JSON.stringify(TASKS));
}

function EditField(elem) {
    let text = elem.innerText;
    if (elem.querySelector('input')) {
        return;
    }
    elem.innerHTML = `<input type="text" id="editeditem" width="100%" value="${text}">`;
    document.addEventListener('mousedown', function handler(event) {
        if (!elem.contains(event.target)) {
            const input = elem.querySelector('input');
            if (input) {
                //elem.innerHTML = `<span>${input.value}</span>`;
                //console.log(elem.id)
                TASKS[elem.parentElement.id][elem.id] = input.value
                taskmod(elem.parentElement.id,TASKS[elem.parentElement.id])
                SaveState();
            }
            document.removeEventListener('mousedown', handler);
        }
    });
}

function taskHTML(id,item) {
    return `
    <div class="taskitem" id="${id}">
        <div class="ti t_box" id="box"><span>${id}</span></div>
        <div class="ti t_progress" id="progress" onclick="EditField(this)"><span>${item.progress}</span></div>
        <div class="ti t_title" id="title" onclick="EditField(this)"><span>${item.title}</span></div>
        <div class="ti t_desc" id="description" onclick="EditField(this)"><span>${item.description}</span></div>
        <div class="ti t_subject" id="subject" onclick="EditField(this)"><span>${item.subject}</span></div>
        <div class="ti t_diff" id="difficulty" onclick="EditField(this)"><span>${diffstar(item.difficulty)}</span></div>
        <div class="ti t_imp" id="importance" onclick="EditField(this)"><span>${item.importance}</span></div>
        <div class="ti t_due" id="duedate" onclick="EditField(this)"><span>${item.duedate}</span></div>
        <div class="ti t_days"><span>${0}</span></div>
    </div>`;
}

function taskgen(item,id) {
    //console.warn(id)
    if(id == undefined) {        
        id = Math.round(Math.random() * Math.pow(16, 4), 0).toString(16);
    }
    let str = taskHTML(id,item);
    document.getElementById('task-container').innerHTML += str;
    TASKS[`${id}`] = { ...TemplateItem };
}
function taskmod(id,item) {
    let str = taskHTML(id,item);
    document.getElementById(id).outerHTML = str;
}

TemplateItem = 
{
    "progress":0.10,
    "title":"Task Name",
    "subject":"Subtext",
    "description":"Description",
    "difficulty":2.5,
    "importance":2.5,
    "duedate":"08/11"
}

init();

CMDbox.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        // Your code here, e.g.:
        let command = CMD.value;
        let args = command.split(' ');
        if (args[0] == "del" || args[0] == "rmv") {
            document.getElementById(args[1]).outerHTML = "";
            delete TASKS[args[1]];
            SaveState();
        } else if (args[0] == "add") {
            taskgen(TemplateItem);
            SaveState();
        }
        console.log(args)
        CMD.value = "";
    }
});