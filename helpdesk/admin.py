# -*- encoding: utf-8 -*-
from django.contrib import admin
from helpdesk.models import Ticket, Project, State, Comment, HelpdeskProfile, TicketAttachment


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'state', 'priority', 'assignee')
    readonly_fields = ('created', 'updated')
    inlines = [TicketAttachmentInline]


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'title')


class StateAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'title')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('created', 'author', 'ticket')


class HelpdeskProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(HelpdeskProfile, HelpdeskProfileAdmin)