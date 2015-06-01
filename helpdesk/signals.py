# -*- encoding: utf-8 -*-
from django.dispatch import Signal

new_comment_from_client = Signal(providing_args=['comment', 'ticket'])

new_answer = Signal(providing_args=['ticket', 'answer'])

ticket_pre_created = Signal(providing_args=['sent_from', 'ticket'])

ticket_post_created = Signal(providing_args=['ticket'])

ticket_updated = Signal(providing_args=['ticket', 'updater', 'changed_data', 'changes'])
