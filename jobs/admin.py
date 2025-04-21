from django.contrib import admin
from .models import Job, Application

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'salary', 'posted_date')
    search_fields = ['title', 'company_name', 'location']

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'applied_on')
    list_filter = ['applied_on']

admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)