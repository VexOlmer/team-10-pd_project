from unicodedata import name
from django.urls import reverse
from django.db import models
from django.db.models import Q

import re
import joblib

from .models import *

model = joblib.load('PersonalArea/static/PersonalArea/model/model.joblib') # Модель для компетенций

# Получить словарь списков
def get_all_competence(user_id):

    # 1 - есть хоть какое-то направление
    # 0 - если нет ни одного

    all_competence = {
        'soft': 0, 'frontend': 0, 'backend': 0, 'designer': 0, 'hard': 0
    }

    user_skills = User_Skills.objects.get(user_id=user_id)

    soft = list()
    frontend = list()
    backend = list()
    designer = list()

    fields = User_Skills._meta.get_fields()
    name_fields = dict()

    for i in fields:
        name_fields[f'{i.attname}'] = i.verbose_name
    
    del_key = [
        'id', 'user_id', 'leader'
    ]

    for i in del_key:
        name_fields.pop(i)

    abreviation = {
        's':soft, 'f':frontend, 'b':backend, 'd':designer
    }

    for key, elem in name_fields.items():

        if '_' in key and key not in ['user_id', 'role_skill']:
            route = abreviation[f'{key[-1]}']

            val = getattr(user_skills, key)
            
            if val:
                route.append(elem)

    all_competence['soft'] = soft
    all_competence['frontend'] = frontend
    all_competence['backend'] = backend
    all_competence['designer'] = designer
    all_competence['all_skills'] = soft + frontend + backend + designer
    all_competence['role'] = user_skills.role_skill

    return all_competence


# Получить ФИО по id
def get_fio(user_id):

    user = User.objects.get(user_id=int(user_id))

    return user.first_name + ' ' + user.last_name


# Проверка на свободные места в команде
def check_empty_place_team(leader_id):

    team = Team.objects.get(leader_id = leader_id)
    teammates = get_all_id_teammates(team.teammates)

    return team.max_amount > len(teammates) + 1


# Курируемые команды преподавателем
def get_curator_for_team(curator_id):
    my_curator_teams = Curator_Team.objects.filter(
        curator_id=curator_id)  # Все курируемые команд

    teams = list()
    for team in my_curator_teams:
        this_team = Team.objects.get(leader_id=team.leader_id)

        teams.append({
            'number': this_team.number,
            'themes': this_team.themes,
            'leader': get_fio(this_team.leader_id)
        })
    return teams


# Получение списка id тиммейтов по строке из БД
def get_all_id_teammates(teammates):

    teammates = teammates.split(',')

    if '' in teammates or ',' in teammates:
        teammates.pop(-1)

    id_teammates = list()

    for student in teammates:
        id_teammates.append(student)
    
    return id_teammates


# Получение id всех из команды
def get_all_id_in_team(leader_id):
    team = Team.objects.get(leader_id=leader_id)

    all_id_teammates = get_all_id_teammates(team.teammates)
    all_id_teammates.insert(0, team.leader_id)

    return all_id_teammates

# Получение информации о команде по списку id (или одному) лидеров
def get_info_team_for_leader(leaders_id):

    # Получение всех команд, с нужными id лидеров
    teams = Team.objects.filter(
        leader_id__in=[*leaders_id,])

    teams_info = list()  # Финальная инфа про все нужные команды

    for team in teams:

        id_teammates = [team.leader_id,]    # id всех студентов из команды, первый всегда идет лидер

        teammates = team.teammates.split(',')

        if '' in teammates or ',' in teammates:
            teammates.pop(-1)

        for teammate in teammates:
            id_teammates.append(teammate)

        # Инфа про одну из нужных команд
        team_info = {
            'leader_id': team.leader_id, 'number': team.number, 'leader': '', 'teammates_id': id_teammates, 'teammates_fio': list(),
            'themes': team.themes,
            'desc': team.description_themes,
            'max_amount' : team.max_amount
        }

        team_info['leader'] = get_fio(id_teammates[0])

        for i in range(1, len(id_teammates)):
            team_info['teammates_fio'].append(get_fio(id_teammates[i]))

        if not len(team_info['teammates_fio']):
            team_info['teammates_fio'].append('Напарников нет')
        if not len(team_info['desc']):
            team_info['desc'] = 'Описания темы на данный момент нет'
        
        team_info['teammates_id'][0] = 0

        teams_info.append(team_info)

    return teams_info


# Студент принимают в команду
# True - удачно принят, False - команда переполнена
def add_student_in_team(leader_id, student_id):
    leader_team = Team.objects.get(leader_id=leader_id)
    teammates = get_all_id_teammates(leader_team.teammates)

    # Если команда уже переполнена, то удаляются все заявки к этому лидеру
    if len(teammates) == leader_team.max_amount - 1:
        req_leader = Request_Join_Team.objects.filter(leader_id=leader_id)

        for elem in req_leader:
            elem.delete()
        return False
    else:
        leader_team.teammates += f'{student_id},'
        leader_team.save()

        # В случае успешного добавления удаляем все его заявки в другие команды и убираем из безкомандных
        User_No_Team.objects.get(user_id=student_id).delete()
        my_req = Request_Join_Team.objects.filter(student_id=student_id)

        for elem in my_req:
            elem.delete()

        return True

# Удаление студента из команды
def delete_student_team(id_student):

    """

    Лидера запрещенно удалять
    Если обычный студент, то просто его удаляем
    При удалении нужно студента оповестить об этом, заносим инфу в Denial_Application

    """

    if id_student != '':
        my_team = get_my_team(id_student)  # Команда нужного студента
        teammates = get_all_id_teammates(my_team.teammates)  # Список id тиммейтов
        teammates.remove(f'{id_student}')  # Удаляем его, если его нет то вылетит ошибка!!

        my_team.teammates = ','.join(teammates)
        my_team.save()

        Denial_Application.objects.create(student_id=id_student, description='Вы были удалены из команды преподавателем')
        User_No_Team.objects.create(user_id=id_student, fio=get_fio(id_student))


# Полный роспуск команды
def delete_team(leader_id):

    """
    
    При расформировки команды лидер теряет лидерство и становиться обычным +
    Все из команды становиться безкомандными и заносятся в таблицу User_No_Team +
    Команда удалется из курируемых каким-либо преподавателем и из таблицы с времени встречи с куратором и тд +
    Все упоминаются в Denial_Application +
    Также удаляются все встречи этой команды, как и с куратором, так и с другими командами

    """

    if leader_id != '':
        my_team = Team.objects.get(leader_id=leader_id)  # Команда лидера, подлежащая полному удалению
        id_in_team = get_all_id_in_team(leader_id)  # Все студенты из команды, включая лидера
        my_team.delete()

        User.objects.filter(user_id=leader_id).update(role='STUDENT')  # Обнуляем лидерство
        
        # Заносим всех в таблице User_No_Team
        for id in id_in_team:
            User_No_Team.objects.create(user_id=id, fio=get_fio(id))
        
        Curator_Team.objects.filter(leader_id=leader_id).delete()  # Удаляем из кураторства
        # Team_Time_Link.objects.filter(leader_id=leader_id).delete()

        # Отправляем всем упоминание об удалении из команды
        for id in id_in_team:
            Denial_Application.objects.create(student_id=id, description='Ваша команда была полностью расформирована')
        
        # Удаляем все упоминания о встречах
        # Meet_Other_Team.objects.filter(Q(leader_king_id=leader_id) | Q(other_leader_id=leader_id)).delete()
        Calendar_Meetings.objects.filter(Q(leader_id=leader_id) | Q(other_leader_id=leader_id)).delete()


# Изменение максимального числа людей в команде
def change_max_members_team(leader_id, new_number):

    if new_number != '' and int(new_number) >= 1:
        my_team = Team.objects.get(leader_id=leader_id)

        if len(get_all_id_in_team(leader_id)) <= int(new_number):
            my_team.max_amount = new_number
            my_team.save()


# Обычный студент становиться лидером
def get_student_status_leader(student_id):

    """
    
    Обычный студент становиться лидером, при этом он не должен находиться в команде

    """

    # Проверка на то, что он не состоит в команде и не лидер
    if not Team.objects.filter(teammates__in=[student_id,]) and User.objects.get(user_id=student_id).role == 'STUDENT':

        count = Team.objects.count()
        Team.objects.create(leader_id=student_id, number=count + 1, teammates='',
                        themes='', description_themes='', url_space='', max_amount=5, customer='')
        Leader_Request.objects.filter(user_id=student_id).delete()  # Для подтверждения заявки преподавателем
        skills = User_Skills.objects.get(user_id=student_id)
        skills.leader = 1
        skills.save()

        User.objects.filter(user_id=student_id).update(
            role='LEADER')


# Изменение почты студента
def change_email(user_id, new_email):

    pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"

    if new_email and re.match(pattern, new_email) is not None:
                User.objects.filter(user_id=user_id).update(
                    email=new_email)

# Изменение имени студента
def change_fio(user_id, new_fio):

    if new_fio:
        new_fio = new_fio.split(' ')
        User.objects.filter(user_id=user_id).update(
            first_name = new_fio[1], last_name = new_fio[0])


# Изменение группы студента
def change_group(user_id, new_group):

    if new_group:
        StudentProfile.objects.filter(user_id=user_id).update(
            group = new_group)

# Изменение описания студента
def change_desc(user_id, new_desc):

    if new_desc:
        StudentProfile.objects.filter(user_id=user_id).update(
            desc = new_desc)

# Получение своей команды, когда ты тиммейт
def get_my_team(user_id):

    all_team = Team.objects.all()

    for team in all_team:
        if str(user_id) in team.teammates:
            return team

# Предсказание роли студента в команде
def role_prediction(user_id):

    user_skills = User_Skills.objects.get(user_id=user_id)
    fields = User_Skills._meta.get_fields()

    skills_int = list() # Список значений скиллов
    
    for key in fields:

        val = getattr(user_skills, key.attname)
        skills_int.append( 1 if val else 0)
    
    skills_int = skills_int[4:]

    role_pred = model.predict([skills_int])

    # if role_pred == 1.0:
    #     role = 'Frontend'
    # elif role_pred == 0.0:
    #     role = 'Backend'
    # else:
    #     role = 'Designer'

    if role_pred == 2.0:
        role = 'Frontend'
    elif role_pred == 1.0:
        role = 'Backend'
    else:
        role = 'Designer'
    print(role)

    return role


# Вывод форматированной даты в виде текста
def date_in_text(date):
    try:
        try:
            date, time = date.split('T')
        except:
            time = date
        year, mounth, day = date.split('-')
        return '.'.join([day, mounth, year]) + ', ' + time
    except:
        return date
