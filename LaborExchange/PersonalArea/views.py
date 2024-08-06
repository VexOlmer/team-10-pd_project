import re
import copy
import os

from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator


from .models import *
from .forms import *
from .DataBases import *
from .decorators import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LaborExchange.settings")

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


# Проверка на роль преподавателя
def teacher(user):
    return user.is_authenticated() and user.role == 'TEACHER'


# Приветственная страница
def home_hello(request):

    if request.user.is_authenticated:

        user_role = request.user.role
        id = request.user.user_id

        if user_role == 'LEADER':
            return redirect('leader_profile')
        elif user_role == 'STUDENT':
            return redirect('student_profile')
        else:
            return redirect('teacher_profile')

    return render(request, "PersonalArea/home_hello.html")


# Страница авторизации
class HomeAuth(LoginView):
    form_class = LoginUserForm
    template_name = 'PersonalArea/home_auth.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        user_role = self.request.user.role
        id = self.request.user.user_id

        if user_role == 'LEADER':
            return reverse_lazy('leader_profile')
        elif user_role == 'STUDENT':
            return reverse_lazy('student_profile')
        else:
            return reverse_lazy('teacher_profile')


# Для кнопок Выйти
def logout_user(request):
    logout(request)
    return redirect('home_auth')


class TeacherRegister(CreateView):
    form_class = RegisterTeacherForm
    template_name = 'PersonalArea/teacher_register.html'
    success_url = reverse_lazy('home_auth')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # c_def = self.get_user_context(title="Авторизация")
        # return dict(list(context.items()) + list(c_def.items()))
        return dict(list(context.items()))


class StudentRegister(CreateView):
    form_class = RegisterStudentForm
    template_name = 'PersonalArea/student_register.html'

    def form_valid(self, form):
        group = form.cleaned_data['group']
        form.cleaned_data.pop('group')

        obj = form.save(commit=False)
        obj.save()

        user_id = User.objects.get(email=form.cleaned_data['email']).user_id
        self.request.session['user_id'] = user_id

        student = StudentProfile.objects.get(user_id=user_id)
        student.group = group
        student.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('student_reg_skills')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # c_def = self.get_user_context(title="Авторизация")
        # return dict(list(context.items()) + list(c_def.items()))
        return dict(list(context.items()))


def StudentRegSkills(request):
    if request.method == 'POST':

        user_id = request.session['user_id']

        form = RegisterStudentSkills(request.POST)
        if form.is_valid():

            new_student_skills = form.save(commit=False)

            del_key = [
                'desc'
            ]

            add_key = {
                'user_id': user_id,
                'role_skill': ''
            }

            desc = form.cleaned_data['desc']
            leader_request = form.cleaned_data['leader']

            student = StudentProfile.objects.get(user_id=user_id)
            student.desc = desc
            student.save()

            # Заявка на подтверждение лидерства
            if leader_request:
                req_leader = Leader_Request.objects.create(
                    user_id=user_id, fio=get_fio(user_id))
                req_leader.save()

            for key in del_key:
                form.cleaned_data.pop(key)

            for key, items in add_key.items():
                form.cleaned_data[key] = items

            new_student_skills.role_skill = add_key['role_skill']
            new_student_skills.user_id = add_key['user_id']
            new_student_skills.leader = 0

            new_student_skills.save()

            role = role_prediction(user_id)
            my_skills = User_Skills.objects.get(user_id=user_id)
            my_skills.role_skill = role
            my_skills.save()

            # Возможных лидеров не добавляем сразу в безкомандные
            if not leader_request:
                User_No_Team.objects.create(user_id=user_id, fio=get_fio(user_id))

            return redirect('home_auth')

    else:
        form = RegisterStudentSkills()

    return render(request, 'PersonalArea/student_register_soft-skills.html', {'form': form})


# Все страницы, связанные с преподователем
menu_teacher = [
    {"title": "Профиль", "url_name": "teacher_profile", "pick": False,
        "show": True, "photo": 'PersonalArea/img/home.svg'},
    {"title": "Заявки", "url_name": "teacher_list_req_leader",
        "pick": False, "show": True, "photo": 'PersonalArea/img/list.svg'},
    {"title": "Команды", "url_name": "teacher_team", "pick": False,
        "show": True, "photo": 'PersonalArea/img/team.svg'},
    {"title": "Встречи", "url_name": "teacher_meet_team", "pick": False,
        "show": True, "photo": 'PersonalArea/img/project.svg'},
    #{"title": "История встреч", "url_name": "teacher_calendar_meet", "pick": False, "show": True, "photo": 'PersonalArea/img/project.svg'},
]


# Профиль преподавателя
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['TEACHER'])
def teach_profile(request):

    user = request.user
    my_id = user.user_id

    context = dict()
    context['fio'] = user.first_name + ' ' + user.last_name
    context['email'] = user.email
    context['header'] = 'Профиль'

    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_teacher)

    for elem in context['menu']:
        if elem['title'] == 'Профиль':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/home-white.svg'

    # Все курируемые команды данным преподавателем
    context['teams'] = get_curator_for_team(user.user_id)

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        req = request.POST

        if 'save_setting' in req:

            change_email(my_id, req['email'])
            change_fio(my_id, req['fio'])
            
            return redirect('teacher_profile')

        if form.is_valid():

            image_form = form.save(commit=False)
            image_form.user_id = my_id

            my_images = Image.objects.filter(user_id=my_id)
            for elem in my_images:
                elem.delete()

            image_form.save()

            context['form'] = image_form
    else:
        form = ImageForm()

    context['form'] = form
    context['photo'] = ''

    my_image = Image.objects.filter(user_id=my_id)
    if my_image:
        context['photo'] = my_image[0].image

    return render(request, "PersonalArea/teacher_profile.html", context=context)


# Список заявок на лидерство
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['TEACHER'])
def teach_list_req_leader(request):

    context = dict()
    context['header'] = 'Заявки на лидерство'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_teacher)

    for elem in context['menu']:
        if elem['title'] == 'Заявки':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    list_leader = Leader_Request.objects.all()

    leaders = list()
    for leader in list_leader:

        id = leader.user_id
        leaders.append({'id': id, 'fio': get_fio(id)})

    context['leaders'] = leaders

    return render(
        request, "PersonalArea/teacher_request_leadership.html", context=context)


# Подтверждение или отклонение заявки лидера
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['TEACHER'])
def teach_accept_req_leader(request, student_id):

    user = User.objects.get(user_id=student_id)
    student_profile = StudentProfile.objects.get(user_id=student_id)

    context = dict()
    context['fio'] = user.first_name + ' ' + user.last_name
    context['email'] = user.email
    context['group'] = student_profile.group
    context['skills'] = get_all_competence(student_id)
    context['id'] = student_id
    image = Image.objects.filter(user_id=student_id)
    if image:
        context['photo'] = image[0].image

    context['menu'] = copy.deepcopy(menu_teacher)

    for elem in context['menu']:
        if elem['title'] == 'Заявки':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/team-white.svg'

    context['accept_button'] = True
    context['accept_button_text'] = 'Принять заявку'

    context['negative_button'] = True
    context['negative_button_text'] = 'Отклонить заявку'

    context['url_view'] = 'accept_req_leader'

    if request.method == 'POST':

        if 'accept' in request.POST:

            get_student_status_leader(student_id)

        if 'negative' in request.POST:

            req = request.POST

            Leader_Request.objects.get(user_id=student_id).delete()
            Denial_Application.objects.create(
                student_id=student_id, description=req['refusal_reason'])
            User_No_Team.objects.create(user_id=student_id, fio=get_fio(student_id))

        return redirect('teacher_list_req_leader')

    return render(request, "PersonalArea/general_student_view.html", context=context)


# Список доступных и курируемых команд у преподавателя
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['TEACHER'])
def teach_team(request):

    user = request.user
    teacher_id = user.user_id

    context = dict()
    context['header'] = 'Команды'

    context['menu'] = copy.deepcopy(menu_teacher)

    for elem in context['menu']:
        if elem['title'] == 'Команды':
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/team-white.svg'

    all_curating_team = Curator_Team.objects.all()  # Все курируемые тимы
    id_leaders_curator = list()  # ID лидер, чьи команды курируются другими

    for team in all_curating_team:
        if team.curator_id != teacher_id:
            id_leaders_curator.append(team.leader_id)

    team_without_curator = Team.objects.exclude(
        leader_id__in=id_leaders_curator)  # Получение не курируемых команд
    
    leader_id_team = list() # Нужные лидеры
    for team in team_without_curator:
        leader_id_team.append(team.leader_id)

    if team_without_curator:
        context['teams'] = get_info_team_for_leader(leader_id_team)
    else:
        context['teams'] = ''

    if request.method == 'POST':

        req = request.POST

        # При отправке макс студентов отправляется так же удаление студента первого
        # Изменение максимального числа людей в команде   
        if 'max_numbers_btn' in req and req['max_numbers']:
            change_max_members_team(req['max_numbers_btn'], req['max_numbers'])
 
        # Полная расформировка команды
        elif 'del_team' in req and req['del_team']:
            id_leader = req['del_team']
            delete_team(id_leader)

        # Скрипт на удаление студента из команды
        elif 'del_student_for_team' in req and req['del_student_for_team']:
            id_student = req['del_student_for_team']
            delete_student_team(id_student)

        elif 'save-themes' in req:

            # Если еще куратор не закреплен
            if not Curator_Team.objects.filter(leader_id=req['save-themes']):
                Curator_Team.objects.create(curator_id=teacher_id, leader_id=req['save-themes'])

            this_team = Team.objects.get(leader_id=req['save-themes'])
            if req['themes']:
                this_team.themes = req['themes']
            if req['description_themes']:
                this_team.description_themes = req['description_themes']
            if req['customer']:
                this_team.customer = req['customer']
            this_team.save()
        return redirect('teacher_team')

    return render(request, "PersonalArea/teacher_my_team.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['TEACHER'])
def teach_meet_team(request):

    user = request.user
    teacher_id = user.user_id

    context = dict()
    context['header'] = 'Встречи с курируемыми командами'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_teacher)

    for elem in context['menu']:
        if elem['title'] == 'Встречи':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/project-white.svg'

    my_curator_teams = Curator_Team.objects.filter(curator_id=teacher_id)  # Все курируемые тимы

    teams_cur = list()
    for team in my_curator_teams:
        this_team = Team.objects.get(leader_id=team.leader_id)
        leader = User.objects.get(user_id=this_team.leader_id)

        fio = leader.first_name + ' ' + leader.last_name

        time_meet = ''
        place_meet = 'Нет ближайших встреч'

        last_meet_this_team = Calendar_Meetings.objects.filter(leader_id=team.leader_id, curator_id=team.curator_id, status=0)
        if last_meet_this_team:
            time_meet = last_meet_this_team.last().time
            place_meet = last_meet_this_team.last().meet

        teams_cur.append({
            'number': this_team.number,
            'themes': this_team.themes,
            'leader': fio,
            'leader_id': leader.user_id,
            'time': date_in_text(time_meet),
            'place': place_meet,
        })

    context['teams_cur'] = teams_cur

    my_history_meet = Calendar_Meetings.objects.filter(curator_id=teacher_id)
    context['meets'] = list()

    for meet in my_history_meet:
        context['meets'].append({
            'fio': get_fio(meet.leader_id),
            'time': date_in_text(meet.time),
            'place': meet.meet,
            'desc': meet.description,
            'status': meet.status,
            'id_meet': meet.id,
            'who': f'Лидер - {get_fio(meet.leader_id)}',
            'who_sent': meet.who_sent,
        })

    paginator = Paginator(context['meets'], 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj

    if request.method == 'POST':

        req = request.POST

        if 'new_meet_team' in req:
            Calendar_Meetings.objects.create(leader_id=req['select'], curator_id=teacher_id, other_leader_id=-1, time=req['time'], meet=req['place'], description=req['desc'], status=-1, who_sent='curator')
        elif 'reject_meet' in req:
            Calendar_Meetings.objects.get(id=req['reject_meet']).delete()
        else:
            this_meet = Calendar_Meetings.objects.get(id=req['accept_meet'])
            this_meet.status = int(this_meet.status) + 1
            this_meet.save()

        # setattr(team_leader, key, elem)
        return redirect('teacher_meet_team')

    return render(request, "PersonalArea/teacher_meet_team.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['TEACHER'])
def teach_cal_meet(request):

    user = request.user
    teacher_id = user.user_id

    context = dict()
    context['header'] = 'История встреч'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_teacher)

    for elem in context['menu']:
        if elem['title'] == 'История встреч':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/project-white.svg'

    my_history_meet = Calendar_Meetings.objects.filter(curator_id=teacher_id)

    context['meets'] = list()

    for meet in my_history_meet:
        num_team = Team.objects.get(leader_id=meet.leader_id).number
        context['meets'].append({
            'fio': get_fio(meet.leader_id),
            'time': meet.time,
            'place': meet.meet,
            'desc': meet.description,
            'number': num_team
        })

    return render(request, "PersonalArea/teacher_history_meet.html", context=context)


# Все страницы, связанные с обычным студентом

menu_student = [
    {"title": "Профиль", "url_name": "student_profile", "pick": False,
        "show": True, "photo": 'PersonalArea/img/home.svg'},
    {"title": "Моя команда", "url_name": "student_team", "pick": False,
        "show": True, "photo": 'PersonalArea/img/team.svg'},
    {"title": "Приглашения", "url_name": "student_invite_all",
        "pick": False, "show": True, "photo": 'PersonalArea/img/invite.svg'},
    {"title": "Проект", "url_name": "student_project", "pick": False,
        "show": True, "photo": 'PersonalArea/img/project.svg'},
    {"title": "Найти команду", "url_name": "student_tap_team",
        "pick": False, "show": True, "photo": 'PersonalArea/img/list.svg'},
]


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_profile(request):

    student = request.user
    my_id = student.user_id

    context = dict()
    context['email'] = student.email
    context['fio'] = student.first_name + ' ' + student.last_name
    context['skills'] = get_all_competence(student.user_id)

    context['header'] = 'Профиль'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Профиль':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/home-white.svg'

    student_profile = StudentProfile.objects.get(user_id=student.user_id)

    context['group'] = student_profile.group
    context['desc'] = student_profile.desc

    denial = Denial_Application.objects.filter(student_id=student.user_id)
    context['denial_true'] = False

    if denial:
        context['denial_true'] = True
        context['denial_desc'] = denial[0].description

    if request.method == 'POST':
        req = request.POST

        if 'del_desc' in req:
            Denial_Application.objects.get(id=denial[0].id).delete()

            return redirect('student_profile')
        
        if 'save_setting' in req:

            change_group(my_id, req['group'])
            change_email(my_id, req['email'])
            change_fio(my_id, req['fio'])
            change_desc(my_id, req['desc'])
            
            return redirect('student_profile')

        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():

            image_form = form.save(commit=False)
            image_form.user_id = my_id

            my_images = Image.objects.filter(user_id=my_id)
            for elem in my_images:
                elem.delete()

            image_form.save()

            context['form'] = image_form
    else:
        form = ImageForm()

    context['form'] = form
    context['photo'] = ''

    my_image = Image.objects.filter(user_id=my_id)
    if my_image:
        context['photo'] = my_image[0].image

    return render(request, "PersonalArea/student_profile.html", context)


# Команда студента, в которой он состоит
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_team(request):

    student = request.user
    my_id = student.user_id

    context = dict()
    context['teams'] = list()

    context['header'] = 'Моя команда'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Моя команда':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/team-white.svg'

    my_team = get_my_team(my_id)
    teammates_info = list()

    # Сбор id тиммейтов если студент находится в команде
    if my_team:
        teammates_info = [
                    my_team.leader_id,
                    ]
        teammates_id = my_team.teammates.split(',')
        teammates_id.pop(-1)

        for teammate in teammates_id:
            teammates_info.append(teammate)

    for teammate in teammates_info:

        context['teams'].append({
                'fio': get_fio(teammate),
                'skills': get_all_competence(teammate)
            })

    return render(request, "PersonalArea/student_team.html", context=context)


# Список всех приглошений от лидера
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_invite_all(request):

    student = request.user
    my_id = student.user_id

    context = dict()

    context['header'] = 'Приглашения'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Приглашения':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/invite-white.svg'

    request_my = Request_Join_Team.objects.filter(
        Q(student_id=my_id) & Q(who_sent='LEADER'))
    context['invites'] = list()

    if request_my:
        for i in range(0, len(request_my)):

            if check_empty_place_team(request_my[i].leader_id):
                context['invites'].append({
                    'fio': get_fio(request_my[i].leader_id), 'id': request_my[i].leader_id
                })

    return render(request, "PersonalArea/student_invite_all.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_invite_team(request, student_id):

    student = request.user
    my_id = student.user_id

    context = dict()

    context['header'] = 'Приглашения'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Приглашения':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/invite-white.svg'

    leader_team = Team.objects.get(leader_id=student_id)
    context['url_space'] = leader_team.url_space

    # id всех студентов из команды
    id_teammates = get_all_id_in_team(student_id)

    team = list()
    for teammates in id_teammates:
        team.append({
            'fio': get_fio(teammates), 'id': teammates,
        })

    context['team'] = team

    if request.method == 'POST':
        if 'accept' in request.POST:

            add_student_in_team(student_id, my_id)

        if 'negative' in request.POST:
            Request_Join_Team.objects.get(Q(student_id=my_id) & Q(
                who_sent='LEADER') & Q(leader_id=student_id)).delete()
        return redirect('student_invite_all')

    return render(request, "PersonalArea/student_invite_team.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_project(request):

    student = request.user
    my_id = student.user_id

    context = dict()

    context['header'] = 'Проект'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Проект':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/project-white.svg'

    my_team = get_my_team(my_id)
    context['project_true'] = True if my_team else False

    if my_team:
        meet_with_cur = Calendar_Meetings.objects.filter(Q(status=0) & Q(other_leader_id=-1) & Q(leader_id=my_team.leader_id))

        context['time_curator'] = ''
        context['place_curator'] = 'Нет ближайших встреч'

        if meet_with_cur:
            context['time_curator'] = date_in_text(meet_with_cur.last().time)
            context['place_curator'] = meet_with_cur.last().meet

        my_curator = Curator_Team.objects.filter(leader_id=my_team.leader_id)
        context['curator_fio'] = 'Не назначен'
        context['curator_email'] = 'Не назначен'

        if my_curator:
            context['curator_fio'] = get_fio(my_curator[0].curator_id)
            context['curator_email'] = User.objects.get(user_id=my_curator[0].curator_id).email
        
        context['themes'] = my_team.themes if my_team.themes else 'Тема еще не назначена'
        context['desc'] = my_team.description_themes if my_team.description_themes else 'Описание еще не назначено'
        context['url_space'] = my_team.url_space if my_team.url_space else 'Рабочее пространство еще не назначено'
        context['customer_name'] = my_team.customer if my_team.customer else 'Заказчик еще не назначен'

        team_meet = Calendar_Meetings.objects.filter(leader_id=my_team.leader_id)

        meets = list()
        for meet in team_meet:
            status = 0
            who_text = 'С куратором' if meet.curator_id != -1  \
                        else (f'С {get_fio(meet.other_leader_id)}' if meet.other_leader_id != my_team.leader_id else f'С {get_fio(meet.leader_id)}')
            status_text = 'Ждет подтверждения' if meet.status == '-1' else \
                            ('Акутальная встреча' if meet.status == '0' else 'Встреча состоялась')

            meets.append(
                {
                    'time': date_in_text(meet.time),
                    'place': meet.meet,
                    'who': who_text,
                    'desc': meet.description,
                    'status': status,
                    'status_text': status_text
                }
            )
        
        paginator = Paginator(meets, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

    return render(request, "PersonalArea/student_project.html", context=context)


# Список всех доступных команд для подачи заявки на вступление
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_tap_team(request):
    student = request.user

    context = dict()
    context['teams'] = list()

    context['header'] = 'Найти команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Найти команду':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    # Получаем уже отправленные заявка лидерам
    req_sent = Request_Join_Team.objects.filter(
        student_id=student.user_id, who_sent='STUDENT')

    req_sent_id_leader = list()  # Список id leader кому уже отправлены заявки
    for elem in req_sent:
        req_sent_id_leader.append(elem.leader_id)

    if User_No_Team.objects.filter(user_id=student.user_id) and not Leader_Request.objects.filter(user_id=student.user_id):

        all_teams = Team.objects.all()
        teams = list()

        for team in all_teams:
            if team.leader_id not in req_sent_id_leader and check_empty_place_team(team.leader_id):
                id_teammates = get_all_id_in_team(team.leader_id)

                if '-' in id_teammates:
                    # Убираем все '-'
                    id_teammates = id_teammates[:id_teammates.index('-')]

                team_info = {
                    'leader_id': team.leader_id, 'leader': '', 'teammates': list(), 'themes': team.themes
                }

                team_info['leader'] = get_fio(id_teammates[0])

                for i in range(1, len(id_teammates)):
                    team_info['teammates'].append(get_fio(id_teammates[i]))

                if not len(team_info['teammates']):
                    team_info['teammates'].append('Напарников нет')

                teams.append(team_info)

        context['teams'] = teams

    if request.method == 'POST':
        req = request.POST
        Request_Join_Team.objects.create(leader_id=req['request_team'], student_id=student.user_id, who_sent='STUDENT')

        return redirect('student_tap_team')

    return render(request, "PersonalArea/student_tap_team.html", context=context)


# Тима лидера, к которому студент хочет постучать в команду
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_tap_team_leader(request, leader_id):

    context = dict()

    context['header'] = 'Найти команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Найти команду':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    leader_team = Team.objects.get(leader_id=leader_id)
    context['url_space'] = leader_team.url_space

    id_teammates = get_all_id_in_team(leader_id)

    team = list()
    for teammates in id_teammates:
        if teammates != '-':
            team.append({
                'fio': get_fio(teammates), 'id': teammates,
            })

    context['team'] = team
    context['id_leader'] = id_teammates[0]

    return render(request, "PersonalArea/student_tap_team_leader.html", context=context)


# Профиль студента из тимы лидера, к которому хочет постучаться
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_profile_tap_team(request, student_id):

    context = dict()

    context['header'] = 'Найти команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'Найти команду':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    student_profile = StudentProfile.objects.get(user_id=student_id)

    context['fio'] = get_fio(student_id)
    context['group'] = student_profile.group
    context['skills'] = get_all_competence(student_id)

    context['accept_button'] = False
    context['negative_button'] = False

    image = Image.objects.filter(user_id=student_id)
    if image:
        context['photo'] = image[0].image

    return render(request, "PersonalArea/student_profile_tap_team.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['STUDENT'])
def student_history_meet(request):

    user = request.user
    my_id = user.user_id

    context = dict()

    context['header'] = 'История встреч'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_student)

    for elem in context['menu']:
        if elem['title'] == 'История встреч':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    my_team = Team.objects.filter(teammates_in=my_id)

    my_history_meet = list()
    if my_team:
        my_history_meet = Calendar_Meetings.objects.filter(
            leader_id=my_team[0].leader_id)

    context['meets'] = list()

    for meet in my_history_meet:
        if meet.curator_id != -1:
            who = 'С куратором'
        else:
            who = f'С командой #{Team.objects.get(leader_id=meet.other_leader_id).number}, Лидер - {get_fio(meet.other_leader_id)}'
        context['meets'].append({
            'time': meet.time_curator,
            'place': meet.meet_point_curator,
            'desc': meet.description,
            'who': who
        })

    return render(request, "PersonalArea/student_history_meet.html", context=context)


# Все страницы, связанные с лидером

menu_leader = [
    {"title": "Профиль", "url_name": "leader_profile", "pick": False,
        "show": True, "photo": 'PersonalArea/img/home.svg'},
    {"title": "Моя команда", "url_name": "leader_team", "pick": False,
        "show": True, "photo": 'PersonalArea/img/team.svg'},
    {"title": "Собрать команду", "url_name": "leader_filter", "pick": False,
        "show": True, "photo": 'PersonalArea/img/invite.svg'},
    {"title": "Проект", "url_name": "leader_project", "pick": False,
        "show": True, "photo": 'PersonalArea/img/project.svg'},
    {"title": "Заявки на вступления", "url_name": "leader_request_member",
        "pick": False, "show": True, "photo": 'PersonalArea/img/list.svg'},
    #{"title": "История встреч", "url_name": "leader_history_meet", "pick": False, "show": True, "photo": 'PersonalArea/img/list.svg'},
]


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_profile(request):

    leader = request.user
    my_id = leader.user_id

    context = dict()
    context['fio'] = get_fio(my_id)
    context['email'] = leader.email
    context['skills'] = get_all_competence(my_id)

    context['header'] = 'Профиль'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'Профиль':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/home-white.svg'

    my_profile = StudentProfile.objects.get(user_id=my_id)

    context['desc'] = my_profile.desc
    context['group'] = my_profile.group

    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        req = request.POST

        if 'save_setting' in req:

            change_group(my_id, req['group'])
            change_email(my_id, req['email'])
            change_fio(my_id, req['fio'])
            change_desc(my_id, req['desc'])
            
            return redirect('leader_profile')

        if form.is_valid():

            image_form = form.save(commit=False)
            image_form.user_id = my_id

            my_images = Image.objects.filter(user_id=my_id)
            for elem in my_images:
                elem.delete()

            image_form.save()

            context['form'] = image_form
    else:
        form = ImageForm()

    context['form'] = form
    context['photo'] = ''

    my_image = Image.objects.filter(user_id=my_id)
    if my_image:
        context['photo'] = my_image[0].image

    return render(request, "PersonalArea/leader_profile.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_team(request):

    leader = request.user

    context = dict()
    context['team'] = list()

    context['header'] = 'Моя команда'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'Моя команда':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/team-white.svg'

    all_id_team = get_all_id_in_team(leader.user_id)

    num = 1
    for id in all_id_team:

        context['team'].append({
                'fio': get_fio(id),
                'skills': get_all_competence(id),
                'number': num
            })
        num += 1

    return render(request, "PersonalArea/leader_team.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_filter(request):

    context = dict()
    user = request.user

    context['header'] = 'Собрать команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'Собрать команду':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/invite-white.svg'

    context['backend'] = list()  # Список списков, в нем id и фио
    context['frontend'] = list()
    context['designer'] = list()
    context['student_no_team'] = list()

    context['full_team'] = not check_empty_place_team(user.user_id)  # Проверка на заполненость команды

    if not context['full_team']:

        # Все кого можно пригласить в команду
        users_no_team = User_No_Team.objects.all()

        for user in users_no_team:
            comp_user = get_all_competence(user.user_id)
            context['student_no_team'].append(user)
            del comp_user['soft']
            del comp_user['all_skills']
            del comp_user['role']

            if not Request_Join_Team.objects.filter(leader_id=request.user.user_id, student_id=user.user_id, who_sent='LEADER'):

                for key, elem in comp_user.items():
                    if elem:
                        context[key].append(
                            {'id': user.user_id, 'fio': user.fio})

    return render(request, "PersonalArea/leader_filter.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_filter_profile(request, student_id):

    context = dict()
    context['fio'] = get_fio(student_id)
    context['skills'] = get_all_competence(student_id)
    context['group'] = StudentProfile.objects.get(user_id=student_id).group
    context['id'] = student_id
    image = Image.objects.filter(user_id=student_id)
    if image:
        context['photo'] = image[0].image

    context['header'] = 'Собрать команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'Собрать команду':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/invite-white.svg'

    # Для отображения кнопок
    context['accept_button'] = True
    context['accept_button_text'] = 'Отправить приглашение'

    context['url_view'] = 'leader_filter_profile'

    if request.method == 'POST':
        if 'accept' in request.POST:
            Request_Join_Team.objects.create(
                leader_id=request.user.user_id, student_id=student_id, who_sent='LEADER')
        return redirect('leader_filter')

    return render(request, "PersonalArea/general_student_view.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_project(request):

    """
    
        У встречи в календаре есть status: 
            -1 - встреча ждет подтверждения другой стороной
            0 - встреча подтвержденна
            1 - встреча состоялась
    
    """

    context = dict()

    context['header'] = 'Проект'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'Проект':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/project-white.svg'

    leader = request.user
    my_id = leader.user_id

    my_team = Team.objects.get(leader_id=my_id)
    context['themes'] = my_team.themes if my_team.themes else 'Тема еще не назначена'
    context['desc'] = my_team.description_themes if my_team.description_themes else 'Описание еще не назначено'
    context['url_space'] = my_team.url_space if my_team.url_space else 'Рабочее пространство еще не назначено'
    context['customer_name'] = my_team.customer if my_team.customer else 'Заказчик еще не назначен'

    if not context['desc']:
        context['desc'] = 'Описание темы отсутствует'

    curator_my_team = Curator_Team.objects.filter(leader_id=my_id)
    context['calendar_see'] = False  # Чтобы без кураторный лидер не смог ничего назначить
    if curator_my_team:
        context['calendar_see'] = True
        curator_id = curator_my_team[0].curator_id

        curator = User.objects.get(user_id=curator_id)
        context['curator_fio'] = get_fio(curator.user_id)
        context['curator_email'] = curator.email
    
    # Формирование списка других команд для подачи им заявки на встречу
    other_teams = list()

    for elem in Team.objects.exclude(leader_id__in=[my_id, ]):
        other_teams.append(
            {
                'leader_id': elem.leader_id,
                'number': elem.number,
                'themes': elem.themes,
                'fio': get_fio(elem.leader_id)
            }
        )
    context['other_teams'] = other_teams

    # Отображение списка встреч из календаря
    my_history_meet = Calendar_Meetings.objects.filter(Q(leader_id=my_id) | Q(other_leader_id=my_id))
    meets = list()  # Список встреч из календаря

    for meet in my_history_meet:
        
        accept_my = True
        if meet.curator_id == -1 and meet.other_leader_id == -1:    # Встреча с заказчиком
            who_form = 'customer'
            who_text = 'Заказчик'
        elif meet.curator_id != -1:                                 # Встреча с куратором
            who_form = f'curator_id-{meet.curator_id}'
            who_text = f'Куратор {get_fio(meet.curator_id)}'

            if meet.who_sent == 'leader':  # Заявку послал лидер., он ее подтвердить не может
                accept_my = False
        else:
            if meet.other_leader_id != my_id:                       # Встреча с другим лидером
                who_form = f'other_leader_id-{meet.other_leader_id}'
                who_text = f'Лидер {get_fio(meet.other_leader_id)}'
                accept_my = False                                   # Заявка была моя --> подтверждать ее я не могу
            else:
                who_form = f'leader_id-{meet.leader_id}'
                who_text = f'Лидер {get_fio(meet.leader_id)}'
                accept_my = True

        meets.append({
            'time': date_in_text(meet.time),
            'place': meet.meet,
            'desc': meet.description,
            'status': meet.status,
            'who_form': who_form,
            'who_text': who_text,
            'id_meet': meet.id,
            'accept_my': accept_my,
        })
    context['meets'] = meets

    paginator = Paginator(meets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj

    meet_with_cur = Calendar_Meetings.objects.filter(Q(status=0) & Q(other_leader_id=-1) & Q(leader_id=my_id))

    context['time_curator'] = ''
    context['place_curator'] = 'Нет ближайших встреч'

    if meet_with_cur:
        context['time_curator'] = date_in_text(meet_with_cur.last().time)
        context['place_curator'] = meet_with_cur.last().meet

    if request.method == 'POST':
        req = request.POST

        team = Team.objects.get(leader_id=leader.user_id)
        
        if "save-url_space" in req:
            url = req['url_space']
            if url:
                team.url_space = url
                team.save()
        elif 'accept_meet' in req or 'reject_meet' in req:
            id_meet = req['accept_meet'] if 'accept_meet' in req else req['reject_meet']
            this_meet = Calendar_Meetings.objects.get(id=id_meet)
            
            if 'reject_meet' in req:
                this_meet.delete()
            else:
                this_meet.status = int(this_meet.status) + 1
                this_meet.save()
        else:
            place = req['place']
            desc = req['desc']
            time = req['time']
            if 'save_team' in req:
                other_leader = req['select']
                Calendar_Meetings.objects.create(leader_id=my_id, curator_id=-1, other_leader_id=other_leader, time=time, 
                                                    meet=place, description=desc, status=-1, who_sent='leader')
            if 'save_curator' in req:
                Calendar_Meetings.objects.create(leader_id=my_id, curator_id=curator.user_id, other_leader_id=-1, time=time, 
                                                    meet=place, description=desc, status=-1, who_sent='leader')
            if 'save_customer' in req:
                Calendar_Meetings.objects.create(leader_id=my_id, curator_id=-1, other_leader_id=-1, time=time, 
                                                    meet=place, description=desc, status=0, who_sent='leader')
        return redirect('leader_project')

    return render(request, "PersonalArea/leader_project.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_request_member(request):

    context = dict()

    context['header'] = 'Заявки на вступление в команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'Заявки на вступления':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    leader = request.user
    my_id = leader.user_id

    request_my = Request_Join_Team.objects.filter(
        Q(leader_id=my_id) & Q(who_sent='STUDENT'))
    context['invites'] = list()

    if check_empty_place_team(my_id) and request_my:
        for i in range(0, len(request_my)):

            context['invites'].append({
                'fio': get_fio(request_my[i].student_id), 'id': request_my[i].student_id
            })

    return render(request, "PersonalArea/leader_request_member.html", context=context)


# Профиль студента, отправившего заявку на вступление в команду
@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_req_member_profile(request, student_id):

    context = dict()
    context['fio'] = get_fio(student_id)
    context['skills'] = get_all_competence(student_id)
    context['group'] = StudentProfile.objects.get(user_id=student_id).group

    context['header'] = 'Заявки на вступление в команду'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)
    context['id'] = student_id

    image = Image.objects.filter(user_id=student_id)
    if image:
        context['photo'] = image[0].image

    # Для отображения кнопок
    context['accept_button'] = True
    context['accept_button_text'] = 'Принять заявку'

    context['negative_button'] = True
    context['negative_button_text'] = 'Отклонить заявку'

    context['url_view'] = 'leader_req_member_profile'

    if request.method == 'POST':
        my_id = request.user.user_id
        print(request.POST)

        if 'accept' in request.POST:
            
            add_student_in_team(my_id, student_id)

        if 'negative' in request.POST:
            req = request.POST

            reason = req['refusal_reason']

            Request_Join_Team.objects.get(
                student_id=student_id, who_sent='STUDENT').delete()
            Denial_Application.objects.create(
                student_id=student_id, description=reason)

        return redirect('leader_request_member')

    return render(request, "PersonalArea/general_student_view.html", context=context)


@login_required(login_url='home_auth')
@allowed_users(allowed_roles=['LEADER'])
def leader_history_meet(request):

    user = request.user
    my_id = user.user_id

    context = dict()

    context['header'] = 'История встреч'
    # Глубокое копирование для копирования внутренних элементов списка
    context['menu'] = copy.deepcopy(menu_leader)

    for elem in context['menu']:
        if elem['title'] == 'История встреч':  # Ищем раздел, отвечающих за страницу
            section = elem

    section['pick'] = True
    section['photo'] = 'PersonalArea/img/list-white.svg'

    my_history_meet = Calendar_Meetings.objects.filter(leader_id=my_id)
    context['meets'] = list()

    num = 0  # Для номера встречи, чтобы изменить описание у конкретной встречи
    for meet in my_history_meet:
        if meet.curator_id != -1:
            who = 'С куратором'
        else:
            who = f'С командой #{Team.objects.get(leader_id=meet.other_leader_id).number}, Лидер - {get_fio(meet.other_leader_id)}'

        context['meets'].append({
            'time': meet.time_curator,
            'place': meet.meet_point_curator,
            'desc': meet.description,
            'who': who,
            'id': num
        })
        num += 1

    if request.method == 'POST':

        for key, elem in request.POST.items():
            if key[0] == 'd':
                num_meet = key[-1]
                new_desc = elem

        for elem in context['meets']:
            if elem['id'] == int(num_meet):
                print(elem)
                this_meet = Calendar_Meetings.objects.get(Q(other_leader_id=my_id) | Q(leader_id=my_id),
                                                          time_curator=elem['time'], meet_point_curator=elem['place'], description=elem['desc'])
                this_meet.description = new_desc
                this_meet.save()

    return render(request, "PersonalArea/leader_history_meet.html", context=context)
