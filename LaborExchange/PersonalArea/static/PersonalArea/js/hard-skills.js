console.log(document.querySelectorAll(".hard-skills-checkbox"));
let closeButton_sup = document.querySelectorAll('.close-button-sup');
let hard_skills = document.querySelectorAll(".hard-skills-checkbox");
let sup = document.querySelector(".support-menu");
let sup_list = document.querySelector(".support-list");


for (let skill of hard_skills) {
    skill.onclick = function () {
    
    sup.classList.add('sup-opened');
    if (skill.name == "Frontend")
    {
        document.querySelector(".Frontend").classList.add('list-opened');
    }
    else if (skill.name == "Backend")
    {
        document.querySelector(".Backend").classList.add('list-opened');
    }
    else if (skill.name == "Designer")
    {
        document.querySelector(".Designer").classList.add('list-opened');
    }
    else if (skill.name == "Architect")
    {
        document.querySelector(".Architect").classList.add('list-opened');
    }
    else if (skill.name == "math")
    {
        document.querySelector(".math").classList.add('list-opened');
    }
    else if (skill.name == "Manager")
    {
        document.querySelector(".Manager").classList.add('list-opened');
    }
  };
}

for(let close of closeButton_sup)
{
close.onclick = function () {
    sup.classList.remove('sup-opened');
    close.parentNode.classList.remove('list-opened');
  };
}