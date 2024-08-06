let textArea = document.querySelector("textarea");
let b_negative = document.querySelector('[name="b_negative"]');
textArea.oninput = function () {

 // Выведем данные из поля ввода
 if (textArea.value.length >= 140)
    {
        b_negative.disabled = true;
    }
    else
    {
        b_negative.disabled = false;
    }
};
