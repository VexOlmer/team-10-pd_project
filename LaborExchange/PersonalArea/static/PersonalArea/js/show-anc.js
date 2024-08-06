let show_student_anc = document.querySelectorAll('.btn-show-anc');
let show_anc = document.querySelectorAll('.show-anc');
console.log(show_anc);
function show()
  {
     console.log('da');
    show_anc.classList.toggle('opened');
  };

function show_aaaanc(id){
    elem = document.getElementById(id); //находим блок div по его id, который передали в функцию
    state = elem.style.display; //смотрим, включен ли сейчас элемент
    if (state =='') elem.style.display='none'; //если включен, то выключаем
    else elem.style.display=''; //иначе - включаем
}
