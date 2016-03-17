# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.7.0'

setup(
    name='django-simple-helpdesk',
    version=version,
    author='Kirill Bubochkin',
    author_email='ookami.kb@gmail.com',
    description='Simple HelpDesk for Django',
    url='https://github.com/ookami-kb/django-simple-helpdesk',
    packages=find_packages(),
    install_requires=['django-bootstrap3', 'django-widget-tweaks', 'django-ckeditor'],
    include_package_data=True,
)
