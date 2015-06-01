DEBUG = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'user@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
DEFAULT_FROM_EMAIL = 'user@gmail.com'

HELPDESK = {
    'username': EMAIL_HOST_USER,
    'password': EMAIL_HOST_PASSWORD,
    'from_email': DEFAULT_FROM_EMAIL,
    'mark_seen': False,
    'urlconf': 'urls',
    'host': 'http://127.0.0.1:8000'
}
