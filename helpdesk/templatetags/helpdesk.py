from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def assignee(context, ticket):
    return me_or_user(context, ticket.assignee)


@register.simple_tag(takes_context=True)
def me_or_user(context, user):
    if user == context['request'].user:
        return mark_safe('<strong>me</strong>')
    return user
