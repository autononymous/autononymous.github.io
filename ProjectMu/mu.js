class BiomeMap { 

    BiomeParams = {
        0 : {
            "name":"grassland",
            "symbol":"<span style='color:lightgreen;'>g</span>",
            "elev":0,
            "mult":0.2
        },
        1 : {
            "name":"forest",
            "symbol":"<span style='color:darkgreen;'>f</span>",
            "elev":2,
            "mult":0.4,
            "decay":4
        },
        2 : {
            "name":"desert",
            "symbol":"<span style='color:orange;'>d</span>",
            "elev":0.1,
            "mult":0.3,
            "decay":6
        },
        3 : {
            "name":"mountains",
            "symbol":"<span style='color:purple;'>m</span>",
            "elev":3,
            "mult":0.8,
            "decay":3
        },
        4 : {
            "name":"water",
            "symbol":"<span style='color:darkblue;'>o</span>",
            "elev":-4,
            "mult":0.2,
            "decay":0
        }
    };
    ElevParams = {
        0 : { "symbol" : "&nbsp;"  },
        1 : { "symbol" : "<span style='opacity:0.3;'>&#9617;</span>" },
        2 : { "symbol" : "<span style='opacity:0.3;'>&#9618;</span>" },
        3 : { "symbol" : "<span style='opacity:0.3;'>&#9619;</span>" },
        4 : { "symbol" : "<span style='opacity:0.6;'>&#9617;</span>" },
        5 : { "symbol" : "<span style='opacity:0.6;'>&#9618;</span>" },
        6 : { "symbol" : "<span style='opacity:0.6;'>&#9619;</span>" }
    };
    CharParams = {
        0 : { "symbol" : "&nbsp;"  },
        1 : { "symbol" : "&mu;" }
    };

    BiomeTypes = Object.keys(this.BiomeParams).length; 
    BiomeRecord = [];
    OverSample = 30;
    Decay = 5.0;
    Lows = 20;
    Highs = 20;
    ElevSteps = 30;
    
    constructor(width,height,elements) {
        this.width = width;
        let widthOS = width + (this.OverSample*2);
        this.height = height;
        let heightOS = height + (this.OverSample*2)
        this.elements = elements;

        let sDISP = "";
        let sELEV = "";
        let sCHAR = "";

        // Arrays
        this.mapOS = Array.from({ length: widthOS }, () => Array(heightOS).fill(0));
        this.map = Array.from({ length: width }, () => Array(height).fill(0));        
        this.dist = Array.from({ length: widthOS }, () => Array(heightOS).fill(widthOS));
        this.elev = Array.from({ length: width }, () => Array(height).fill(0));  
        this.elevI = Array.from({ length: width }, () => Array(height).fill(0));   
         
        this.MuPos = Array.from({ length: width }, () => Array(height).fill(0));       


        // Vornoi Biome Creation
        for(let i=0; i<=elements; i++) {
            let x = Math.round(Math.random() * widthOS-1,0)
            let y = Math.round(Math.random() * heightOS-1,0)
            let b = Math.round(Math.random() * (this.BiomeTypes-1),0)
            //this.mapOS[x][y] = b;
            this.BiomeRecord.push([x,y,b])
        }
        
        for(let i=0; i<heightOS; i++) {
            for(let j=0; j<widthOS; j++) {
                let xd = 0;
                let yd = 0;
                let R = 0;
                this.BiomeRecord.forEach( ([x,y,b]) => {
                    xd = x-j;
                    yd = y-i;
                    R = Math.pow((Math.pow(xd,2) + Math.pow(yd,2)),0.5) + (Math.random()*this.BiomeParams[b].decay);
                    let IsSmaller = this.dist[j][i] > R;
                    this.dist[j][i] = IsSmaller ? R : this.dist[j][i];
                    this.mapOS[j][i] = IsSmaller ? b : this.mapOS[j][i];
                });
                
                
            }
        }       


        for(let i=0; i<height; i++) {
            for(let j=0; j<width; j++) {
                this.map[j][i] = this.mapOS[j+this.OverSample][i+this.OverSample];
            }            
        }
        for(let i=0; i<height; i++) {
            for(let j=0; j<width; j++) {
                this.elev[j][i] = this.BiomeParams[this.map[j][i]].elev;
            }
        }
        let maxima = [0,0]
        for(let h=0; h<this.ElevSteps; h++){
            for(let i=0; i<height; i++) {
                for(let j=0; j<width; j++) {
                    let randmul = (Math.random() - 0.5) * 2;
                    this.elev[j][i] += this.BiomeParams[this.map[j][i]].mult * randmul;
                    maxima[0] = this.elev[j][i] < maxima[0] ? this.elev[j][i] : maxima[0];
                    maxima[1] = this.elev[j][i] > maxima[1] ? this.elev[j][i] : maxima[1];
                }
            }
        }
        let range = maxima[1] - maxima[0];
        console.log(maxima)
        console.log(range)
        let ParamSplits = Object.keys(this.ElevParams).length - 1;
        for(let i=0; i<height; i++) {
            for(let j=0; j<width; j++) {
                this.elevI[j][i] = Math.round(((this.elev[j][i] - maxima[0]) / range) * (ParamSplits),0);
            }
            
        }
        this.CharPos = [10,10];

        this.MuPos[this.CharPos[0]][this.CharPos[1]] = 1;

        console.log(this.elevI)
        for(let i=0; i<height; i++) {
            for(let j=0; j<width; j++) {
                sDISP += this.BiomeParams[this.map[j][i]].symbol;
                sELEV += this.ElevParams[this.elevI[j][i]].symbol;
                sCHAR += this.CharParams[this.MuPos[j][i]].symbol;
            }            
            sDISP += "<br>";
            sELEV += "<br>";
            sCHAR += "<br>";
        }
        eMAIN.innerHTML = sDISP;
        eELEV.innerHTML = sELEV;
        eCHAR.innerHTML = sCHAR;
    }

    CharacterMove(dx,dy) {
        let sCHAR = "";
        this.MuPos[this.CharPos[0]][this.CharPos[1]] = 0;
        this.CharPos[0] += dx;
        this.CharPos[1] += dy;        
        this.MuPos[this.CharPos[0]][this.CharPos[1]] = 1;
        for(let i=0; i<this.height; i++) {
            for(let j=0; j<this.width; j++) {
                sCHAR += this.CharParams[this.MuPos[j][i]].symbol;
            } 
            sCHAR += "<br>";
        }
        eCHAR.innerHTML = sCHAR;
    }
}

G = new BiomeMap(200,150,100);

document.addEventListener('keydown', function(event) {
    switch(event.key) {
        case 'ArrowUp':
            console.log('Up arrow pressed');
            G.CharacterMove(0,-1);
            break;
        case 'ArrowDown':
            console.log('Down arrow pressed');
            G.CharacterMove(0,1);
            break;
        case 'ArrowLeft':
            console.log('Left arrow pressed');
            G.CharacterMove(-1,0);
            break;
        case 'ArrowRight':
            console.log('Right arrow pressed');
            G.CharacterMove(1,0);
            break;
    }
});

var STATE = [0,0,0];
var CHECK = false;

var STORY = {
    0 : {
        0 : {
            0 : {
                "requires" : "", "next" : [0,0,1], "newscreen" : false, "hideconsole" : false,
                "passage" : "<p>> the poison in your breath strains your lungs</p>"},
            1 : {
                "requires" : "", "next" : [0,0,2], "newscreen" : false, "hideconsole" : false,
                "passage" : "<p>> you've been running from the capital for minutes</p>" },
            2 : {
                "requires" : "", "next" : [0,0,3], "newscreen" : false, "hideconsole" : false,
                "passage" : "<p>> places and people reduced to ashes</p>" },
            3 : {
                "requires" : "", "next" : [0,0,4], "newscreen" : false, "hideconsole" : false,
                "passage" : "<p>> clutching what the chymaerans were after</p>" },
            4 : {
                "requires" : "", "next" : [0,0,5], "newscreen" : false, "hideconsole" : false,
                "passage" : "<p>> declared a traitor by your own people</p>" },
            5: {
                "requires" : "", "next" : [0,0,6], "newscreen" : false, "hideconsole" : false,
                "passage" : "<span>> as the royal son, </span>" },
            6 : {
                "requires" : "", "next" : [0,0,7], "newscreen" : false, "hideconsole" : false,
                "passage" : " the last living royal of northaven," },
            7 : {
                "requires" : "", "next" : [0,0,8], "newscreen" : false, "hideconsole" : false,
                "passage" : "<p>> chased by the arbiters of liquidation,</p>" },
            8 : {
                "requires" : "", "next" : [0,0,9], "newscreen" : true, "hideconsole" : false,
                "passage" : "<p>> all you have left to do</p>" },
            9 : {
                "requires" : "", "next" : [0,0,10], "newscreen" : true, "hideconsole" : false,
                "passage" : "<p>> is</p>" },
            10: {
                "requires" : "", "next" : [0,1,0], "newscreen" : true, "hideconsole" : false,
                "passage" : "<p>> run</p>" },

        },
    1 : { 
        0 : {
                "requires" : "run", "next" : [0,0,1], "newscreen" : false, "hideconsole" : true,
                "passage" : "<p>> the poison in your breath strains your lungs</p>"}
        }
    }
}

function StoryState(text) 
{
    let entry = STORY[STATE[0]][STATE[1]][STATE[2]];
    console.log(text)
    CHECK = (entry.requires == "") ? true : (text == entry.requires) ? true : false;
    if (CHECK) {
        eCONSOLE.innerHTML = entry.newscreen ? entry.passage : eCONSOLE.innerHTML + entry.passage;
        STATE[0] = entry.next[0];    
        STATE[1] = entry.next[1];
        STATE[2] = entry.next[2];
        if (entry.hideconsole) {
            eSCR.style.setProperty("mouse-events","none");
            eSCR.style.setProperty("opacity","0");
        }
    }
    
}

function Proceed(text) 
{
    StoryState(text);
    eTEXT.value = "";
}

