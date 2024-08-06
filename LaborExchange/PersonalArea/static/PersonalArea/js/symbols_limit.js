let textArea = document.querySelector('textarea');
textArea.value = '';
let deny = document.querySelector('[name="deny"]');
// Добавим обработчик событий
textArea.oninput = function () {
 // Выведем данные из поля ввода
 if (textArea.value.length >= 140)
    {
        deny.disabled = true;
    }
    else
    {
        deny.disabled = false;
    }
};
