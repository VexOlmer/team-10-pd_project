  let tooltip = document.querySelector('.tooltip');
let closeButton = document.querySelector('.btn-close');
let tooltipCheckboxs = document.querySelectorAll('.tooltip-checkbox');
let tooltipText = document.querySelector('.tooltip-text');

for (let tooltipCheckbox of tooltipCheckboxs) {
    try
    {
    tooltipCheckbox.onclick = function () {
    tooltipText.textContent = tooltipCheckbox.dataset.tooltipText;
    console.log(tooltipText.textContent);
    tooltip.classList.toggle('opened');
    console.log(tooltip);
  };
  }
  catch
  {
  
  }
}
console.log(tooltip);
closeButton.onclick = function () {
    try
    {
    tooltip.classList.remove('opened');
    }
    catch
    {

    }

  };