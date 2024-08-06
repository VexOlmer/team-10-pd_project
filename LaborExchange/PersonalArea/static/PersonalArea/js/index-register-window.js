let link = document.querySelector('.reg');
let close = document.querySelector('.close');
let wind = document.querySelector('.modal-Dialog');

link.onclick = function()
{
wind.style.display = "block"
};

close.onclick = function()
{
console.log(close)
wind.style.display = "none"
};