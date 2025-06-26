const ROOT = document.querySelector(':root');

function RootSet(param,value) {
  ROOT.style.setProperty(`--${param}`,value)
}

function initialize() {  
  
  var CFG = "";

  fetch('config.json')
    .then(response => response.json())
    .then(config => {
      // Use the parsed config object as needed
      console.log(config);
      CFG = config;
    })
    .catch(error => {
      console.error('Error loading config.json:', error);
    });  
}

initialize();