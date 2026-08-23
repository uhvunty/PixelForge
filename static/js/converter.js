document.addEventListener(
"DOMContentLoaded",
()=>{


const input =
document.getElementById(
"image"
);


const preview =
document.getElementById(
"image-preview"
);


const filename =
document.getElementById(
"selected-file-name"
);



if(!input){

return;

}



input.addEventListener(
"change",
()=>{


const file =
input.files[0];


if(!file){

return;

}



filename.innerText =
file.name;



preview.src =
URL.createObjectURL(
file
);


preview.hidden =
false;



});


});