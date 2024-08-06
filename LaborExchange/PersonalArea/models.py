from unittest.util import _MAX_LENGTH
from django.urls import reverse
from django.db import models

from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from .manage import *


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"
        LEADER = "LEADER", "Leader"

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'

    base_role = Role.ADMIN

    user_id = models.AutoField(
        primary_key=True, verbose_name='ID пользователя')
    role = models.CharField(
        max_length=50, choices=Role.choices, verbose_name='Роль')
    email = models.EmailField(unique=True, verbose_name='Почта')

    photo = models.ImageField(verbose_name='Фото', blank=True, upload_to="photos/%Y/%m/%d/")

    first_name = models.CharField(verbose_name='Имя', max_length=30)
    last_name = models.CharField(verbose_name='Фамилия', max_length=15)
    username = models.CharField(
        verbose_name='Имя пользователя', max_length=150, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    # objects = UserManager()

    # def get_short_name(self):
    #     return self.email

    # def natural_key(self):
    #     return self.email

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)


class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.STUDENT)


class Student(User):

    base_role = User.Role.STUDENT

    student = StudentManager()

    class Meta:
        proxy = True


@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "STUDENT":
        StudentProfile.objects.create(user=instance)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    group = models.CharField(verbose_name='Группа', max_length=10, blank=True)
    desc = models.TextField(verbose_name='Описание', blank=True, null=True)


#     # Для отображения профиля студента при заявках и тд
#     def get_absolute_url(self):
#         return reverse("user_profile", kwargs={"pk": self.pk})


class TeacherManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        result = super().get_queryset(*args, **kwargs)
        return result.filter(role=User.Role.TEACHER)


class Teacher(User):

    base_role = User.Role.TEACHER

    teacher = TeacherManager()

    class Meta:
        proxy = True


@receiver(post_save, sender=Teacher)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "TEACHER":
        TeacherProfile.objects.create(user=instance)


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Team(models.Model):
    leader_id = models.SmallIntegerField(
        primary_key=True, verbose_name="Лидер команды")

    number = models.SmallIntegerField(verbose_name="Номер команды")

    teammates = models.CharField(
        verbose_name="Напарники", null=True, max_length=200, blank=True)

    themes = models.CharField(
        max_length=50, verbose_name="Тема команды", null=True)
    description_themes = models.CharField(
        max_length=255, verbose_name="Описание темы команды", null=True
    )
    url_space = models.URLField(max_length=200, verbose_name="Ссылка на рабочее пространство", null=True)
    max_amount = models.SmallIntegerField(verbose_name="Максимальное кол-во людей в команде")
    customer = models.CharField(max_length=255, verbose_name="Заказчик команды", null=True)

    class Meta:
        verbose_name_plural = "Команды"
        verbose_name = "Команда"

    def __str__(self) -> str:
        return "Команда номер: " + str(self.number)


class User_No_Team(models.Model):
    user_id = models.SmallIntegerField(
        verbose_name="ID пользователя", primary_key=True)

    fio = models.CharField(verbose_name="ФИО", max_length=60)

    class Meta:
        verbose_name_plural = "Пользователи без команды"
        verbose_name = "Пользователь без команды"


class Leader_Request(models.Model):
    user_id = models.SmallIntegerField(
        verbose_name="ID пользователя", primary_key=True)

    fio = models.CharField(verbose_name="ФИО", max_length=60)

    class Meta:
        verbose_name_plural = "Заявки лидеров на подтверждение"
        verbose_name = "Заявка лидера на подтверждение"


class Request_Join_Team(models.Model):

    leader_id = models.SmallIntegerField(verbose_name="ID лидера")
    student_id = models.SmallIntegerField(verbose_name="ID студента")

    who_sent = models.CharField(
        verbose_name="Кто отправил приглошение", max_length=10)

    class Meta:
        verbose_name_plural = "Заявки от лидера/студента на вступление в команду"
        verbose_name = "Заявка от лидера/студента на вступление в команду"


class Curator_Team(models.Model):
    curator_id = models.SmallIntegerField(verbose_name="ID куратора")

    leader_id = models.SmallIntegerField(verbose_name="ID лидера")

    class Meta:
        verbose_name_plural = "Команды и ее куратор"
        verbose_name = "Команда и ее куратор"


class Denial_Application(models.Model):
    student_id = models.SmallIntegerField(verbose_name="ID студента")

    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name_plural = "Отказы"
        verbose_name = "Отказ"


class Calendar_Meetings(models.Model):
    leader_id = models.SmallIntegerField(verbose_name="ID лидера")
    curator_id = models.SmallIntegerField(verbose_name="ID куратора")
    other_leader_id = models.SmallIntegerField(
        verbose_name="ID другого лидера")

    time = models.CharField(
        verbose_name="Дата и время встречи с куратором", max_length=20)
    meet = models.CharField(
        verbose_name="Место встречи с куратором", max_length=255
    )

    description = models.TextField(verbose_name="Описание")
    status = models.CharField(verbose_name='Статус встречи', max_length=5)
    who_sent = models.CharField(verbose_name='Кто отправил', max_length=10)

    class Meta:
        verbose_name_plural = "Две похожих таблицы"
        verbose_name = "Две похожих таблицы"


class User_Skills(models.Model):
    user_id = models.SmallIntegerField(
        verbose_name="ID пользователя", blank=True)

    leader = models.BooleanField(verbose_name="Лидер")
    role_skill = models.CharField(verbose_name="Роль пользователя данная моделью", max_length=10)

    # Soft Skills
    team_management_s = models.BooleanField(verbose_name="Управление командой и процессами")
    negotitation_s = models.BooleanField(verbose_name="Ведение переговоров")
    resoinsibility_s = models.BooleanField(verbose_name="Ответственность")
    organization_s = models.BooleanField(verbose_name="Организованность")
    log_think_s = models.BooleanField(verbose_name="Логическое мышление")
    abstrat_think_s = models.BooleanField(verbose_name="Абстрактное мышление")
    creativity_s = models.BooleanField(verbose_name="Креативность")
    stress_resist_s = models.BooleanField(verbose_name="Стрессоустойчивость")
    analyt_skill_s = models.BooleanField(verbose_name="Аналитические навыки")
    fast_learn_s = models.BooleanField(verbose_name="Быстрая обучаемость и гибкость")
    ability_develop_s = models.BooleanField(verbose_name="Способность к саморазвитию")
    sociability_s = models.BooleanField(verbose_name="Коммуникабельность")
    customer_focus_s = models.BooleanField(verbose_name="Клиентоориентированность")
    serach_info_s = models.BooleanField(verbose_name="Умение быстро и эффективно искать информацию в авторитетных источника")
    work_team_s = models.BooleanField(verbose_name="Умение работать в команде")

    # Frontend Skills
    html_css_f = models.BooleanField(verbose_name="Языки верстки web-страниц HTML и CSS;")
    js_f = models.BooleanField(verbose_name="Знание языка программирования JavaScript")
    reg_ang_vue_f = models.BooleanField(verbose_name="Знание JavaScript-фреймворков (React, Angular, Vue.js)")
    ts_f = models.BooleanField(verbose_name="Знание TypeScript")
    jquery_f = models.BooleanField(verbose_name="Знание jQuery")
    git_f = models.BooleanField(verbose_name="Знание инструментов контроля версий Git")

    # Backend Skills
    server_lang_b = models.BooleanField(verbose_name="Знание «серверного» языка программирования: PHP, Go, ASP.NET, C/C++, Python, Ruby, Java")
    sql_b = models.BooleanField(verbose_name="Знание SQL, принципов работы с базой данных")
    pret_bd_b = models.BooleanField(verbose_name="Навыки проектирования баз данных")
    api_b = models.BooleanField(verbose_name="Знание API")
    unit_test_b = models.BooleanField(verbose_name="Навыки написания юнит-тестов и покрытия кода тестами")
    solid_b = models.BooleanField(verbose_name="Понимание и навык использования SOLID-принципов")

    # Designer Skills
    creative_skills_d = models.BooleanField(verbose_name="Владение творческими навыками")
    prototype_d = models.BooleanField(verbose_name="Навык создания прототипов экранов")
    typography_d = models.BooleanField(verbose_name="Знание основ типографики")
    draw_skills_d = models.BooleanField(verbose_name="Навыки рисования")
    photoshop_d = models.BooleanField(verbose_name="Навык использования Photoshop")
    adobe_d = models.BooleanField(verbose_name="Навык использования Adobe XD, Adobe Illustrator")
    figma_d = models.BooleanField(verbose_name="Навык работы с Figma")
    sketch_d = models.BooleanField(verbose_name="Навык работы с Sketch")
    color_sience_d = models.BooleanField(verbose_name="Знание основ колористики и цветоведения")

    class Meta:
        verbose_name_plural = "User Skills"
        verbose_name = "User Skills"


# Модель для всех загружаемых фотографий в проекте
class Image(models.Model):
    user_id = models.SmallIntegerField(
        verbose_name="ID пользователя", blank=True)
    image = models.ImageField(
        verbose_name='Фото', blank=True, upload_to="images/%Y/%m/%d/")

    class Meta:
        verbose_name_plural = "Фотографии"
        verbose_name = "Фотография"
