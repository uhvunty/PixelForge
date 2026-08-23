document.addEventListener(
"DOMContentLoaded",
()=>{


const canvas =
document.getElementById(
"pixel-result-canvas"
);



if(!canvas){

return;

}



const data =
JSON.parse(
document.getElementById(
"pixel-data"
).textContent
);



const editor =
new PixelEditor(
canvas,
data.width,
data.height
);



data.pixels.forEach(
pixel=>{


editor.setPixel(

pixel.x,

pixel.y,

pixel.color

);


}
);



const color =
document.getElementById(
"pixel-color"
);



if(color){

color.addEventListener(
"input",
()=>{

editor.setColor(
color.value
);

}
);

}



const clear =
document.getElementById(
"clear-pixel-art"
);



if(clear){

clear.onclick =
()=>{

editor.clear();

};

}



const download =
document.getElementById(
"download-pixel-art"
);



if(download){

download.onclick =
()=>{

editor.download();

};

}



const save =
document.getElementById(
"save-pixel-art"
);



if(save){

save.onclick =
async ()=>{


const title =
document.getElementById(
"artwork-title"
).value;



const response =
await fetch(
"/studio/save",
{

method:"POST",

headers:{
"Content-Type":
"application/json"
},


body:
JSON.stringify({

title:title,

...editor.getData()

})


}
);



const result =
await response.json();



document.getElementById(
"pixel-message"
)
.innerText =
result.message;



};

}



});