from tkinter import Widget
from turtle import width
from django import forms
from .models import *

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm


class RegisterTeacherForm(UserCreationForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Придумайте пароль'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Повторите пароль'}))

    class Meta:
        model = Teacher
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Введите e-mail'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Фамилия'}),
        }


class RegisterStudentForm(UserCreationForm):
    group = forms.CharField(label="Группа", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Группа'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Придумайте пароль'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Повторите пароль'}))

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'group', 'password1', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Введите e-mail'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Фамилия'}),
        }


class RegisterStudentSkills(forms.ModelForm):

    desc = forms.CharField(label="Описание", required=False,
                            widget=forms.Textarea(attrs={'class': 'load-about', 
                                                'placeholder': "Расскажите немного о себе!", 'cols': 70, 'rows': 10}))

    class Meta:
        model = User_Skills
        fields = [
            'leader',
            'team_management_s', 'negotitation_s', 'resoinsibility_s', 'organization_s', 'log_think_s', 'abstrat_think_s',
            'creativity_s',
            'stress_resist_s', 'analyt_skill_s', 'fast_learn_s', 'ability_develop_s', 'sociability_s', 'customer_focus_s',
            'serach_info_s', 'work_team_s',
            'html_css_f', 'js_f', 'reg_ang_vue_f', 'ts_f', 'jquery_f', 'git_f', 
            'server_lang_b', 'sql_b', 'pret_bd_b', 'api_b', 'unit_test_b', 'solid_b',
            'creative_skills_d', 'prototype_d', 'typography_d', 'draw_skills_d', 'photoshop_d', 'adobe_d',
            'figma_d', 'sketch_d', 'color_sience_d',
        ]
        widgets = {

            # Лидер/Куратор/Наставник
            'leader': forms.CheckboxInput(attrs={'class': 'lg-checkbox', 'style': "vertical-align: baseline; margin:10px"}),

            # Soft skills
            'team_management_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'negotitation_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'resoinsibility_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'organization_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'log_think_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'abstrat_think_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'creativity_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'stress_resist_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'analyt_skill_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'fast_learn_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'ability_develop_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'sociability_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'customer_focus_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'serach_info_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'work_team_s': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),

            # Frontend skills
            'html_css_f': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'js_f': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'reg_ang_vue_f': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'ts_f': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'jquery_f': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'git_f': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),

            # Backend skills
            'server_lang_b': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'sql_b': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'pret_bd_b': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'api_b': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'unit_test_b': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'solid_b': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),

            # Designer skills
            'creative_skills_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'prototype_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'typography_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'draw_skills_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'photoshop_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'adobe_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'figma_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'sketch_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),
            'color_sience_d': forms.CheckboxInput(attrs={'class': 'lg-checkbox'}),

        }


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Почта', widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Введите e-mail'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Введите пароль'}))


# Для загрузки фотографий в профилях
class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'input__file-button-text', 'placeholder': 'Выбрать файл'}),
         }