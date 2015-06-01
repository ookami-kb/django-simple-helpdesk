# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.4.2'

setup(
    name='django-simple-helpdesk',
    version=version,
    author='Kirill Bubochkin',
    author_email='ookami.kb@gmail.com',
    description='Simple HelpDesk for Django',
    packages=find_packages(),
    install_requires=['django'],
    include_package_data=True,
)
