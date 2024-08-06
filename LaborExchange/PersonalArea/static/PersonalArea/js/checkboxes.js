let masterCheckbox = document.querySelector('input[type="checkbox"][name="accept"]');
let slaveCheckboxes = document.querySelectorAll('input[type="checkbox"]:not([name="accept"])');

masterCheckbox.addEventListener('change', function() {
    if (masterCheckbox.checked) {
        // Галочка поставлена. Деактивируем остальные чекбоксы.
        Array.prototype.forEach.call(slaveCheckboxes, function(checkbox) {
            checkbox.checked = false;
            checkbox.disabled = true;
        });
    } else {
        // Галочка убрана. Активируем остальные чекбоксы.
        Array.prototype.forEach.call(slaveCheckboxes, function(checkbox) {
            checkbox.disabled = false;
        });
    }
});