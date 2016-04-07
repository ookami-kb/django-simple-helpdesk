from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from helpdesk.models import Ticket, Project, State, Comment, HelpdeskProfile, MailAttachment, ProjectAlias


class AttachmentInline(GenericTabularInline):
    model = MailAttachment


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'state', 'priority', 'assignee')
    readonly_fields = ('created', 'updated')
    inlines = [AttachmentInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'title')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('machine_name', 'title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('created', 'author', 'ticket')


@admin.register(HelpdeskProfile)
class HelpdeskProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(ProjectAlias)
class ProjectAliasAdmin(admin.ModelAdmin):
    list_display = ('email', 'project')
