var textArea = document.querySelector("textarea");
let b_negative = document.querySelector('[name="btn_negative"]');
let symbols = document.querySelector('.show-symbol-length');

textArea.value = '';


function clickRadio(el) {
  var siblings = document.querySelectorAll("input[type='radio'][name='" + el.name + "']");

  for (var i = 0; i < siblings.length; i++) {
    if (siblings[i] != el)
    {
      siblings[i].oldChecked = false;
      textArea.disabled = true;
      textArea.value = '';
      symbols.textContent = "0/140";
      b_negative.disabled = false;
      symbols.style.color = "black";
     }

  }
  if (el.oldChecked)
  {
    el.checked = false;
    textArea.disabled = false;
   }
    el.oldChecked = el.checked;


};

    textArea.oninput = function () {

 // Выведем данные из поля ввода
 symbols.textContent = textArea.value.length + "/140";
 if (textArea.value.length >= 140)
    {
        b_negative.disabled = true;
        symbols.style.color = "red";
    }
    else
    {
        b_negative.disabled = false;
        symbols.style.color = "black";
    }
};