from django.contrib import admin
from ChatApp.models import Member,Groups,Report

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    
    list_display=('id','Name','Group','Role','ReportCount','isOnline')
admin.site.register(Member,MemberAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display=('id','Name','Limit','Password')

admin.site.register(Groups,GroupAdmin)

admin.site.register(Report)