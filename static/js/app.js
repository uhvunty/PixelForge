document.addEventListener(
"DOMContentLoaded",
()=>{


const buttons =
document.querySelectorAll(
"[data-confirm]"
);



buttons.forEach(
button=>{


button.addEventListener(
"click",
(event)=>{


const message =
button.dataset.confirm;



if(
!confirm(message)
){

event.preventDefault();

}


}
);


}
);


});