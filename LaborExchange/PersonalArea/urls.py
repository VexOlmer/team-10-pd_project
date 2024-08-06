from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    path("", home_hello, name="home_hello"),
    path("home", HomeAuth.as_view(), name="home_auth"),
    path('logout/', logout_user, name='logout'),

    path('teacher/register', TeacherRegister.as_view(), name='teacher_register'),
    path("teacher/profile", teach_profile, name="teacher_profile"),
    path("teacher/request_leader", teach_list_req_leader, name="teacher_list_req_leader"),
    path("teacher/team", teach_team, name="teacher_team"),
    path("teacher/meet_team", teach_meet_team, name="teacher_meet_team"),
    path("teacher/calendar_meet", teach_cal_meet, name="teacher_calendar_meet"),
    path("teacher/accept_req_leader/<int:student_id>", teach_accept_req_leader, name="accept_req_leader"),

    path('student/register', StudentRegister.as_view(), name='student_register'),
    path('student/register_soft_skills', StudentRegSkills, name='student_reg_skills'),
    path("student/profile", student_profile, name="student_profile"),
    path("student/team", student_team, name="student_team"),
    path("student/invite_all", student_invite_all, name="student_invite_all"),
    path("student/invite_team<int:student_id>", student_invite_team, name="student_invite_team"),
    path("student/project", student_project, name="student_project"),
    path("student/tap_team", student_tap_team, name="student_tap_team"),
    path("student/tap_team_leader/<int:leader_id>", student_tap_team_leader, name="student_tap_team_leader"),
    path("student/profile_tap_team/<int:student_id>", student_profile_tap_team, name="student_profile_tap_team"),
    path("student/history_meet", student_history_meet, name="student_history_meet"),

    path("leader/profile", leader_profile, name="leader_profile"),
    path("leader/team", leader_team, name="leader_team"),
    path("leader/filter", leader_filter, name="leader_filter"),
    path("leader/filter/profile/<int:student_id>", leader_filter_profile, name="leader_filter_profile"),
    path("leader/project", leader_project, name="leader_project"),
    path("leader/request_member", leader_request_member, name="leader_request_member"),
    path("leader/req_member_profile/<int:student_id>", leader_req_member_profile, name="leader_req_member_profile"),
    path("leader/history_meet", leader_history_meet, name="leader_history_meet"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
