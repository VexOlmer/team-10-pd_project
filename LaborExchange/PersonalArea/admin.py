from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'role', 'username') # Вывод в строке записи                                       # Поля для гиперсылки
    search_fields = ('email', 'username')                                   # Поля для поиска


class TeamAdmin(admin.ModelAdmin):
    list_display = ("number", "themes", "description_themes")


class User_No_TeamAdmin(admin.ModelAdmin):
    list_display = ("fio", )


class Leader_RequestAdmin(admin.ModelAdmin):
    list_display = ("user_id", "fio")


admin.site.register(User, UserAdmin)
admin.site.register(Team, TeamAdmin)

admin.site.register(User_Skills)

admin.site.register(User_No_Team, User_No_TeamAdmin)
admin.site.register(Leader_Request, Leader_RequestAdmin)
admin.site.register(Request_Join_Team)
admin.site.register(Curator_Team)
# admin.site.register(Team_Time_Link)
admin.site.register(Denial_Application)
# admin.site.register(Meet_Other_Team)
admin.site.register(Calendar_Meetings)
