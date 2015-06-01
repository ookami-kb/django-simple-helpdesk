from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from tastypie.api import Api

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include('helpdesk.urls')),
    url(r'^ckeditor', include('ckeditor.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
