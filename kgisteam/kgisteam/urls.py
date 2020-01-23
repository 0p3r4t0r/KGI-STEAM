"""kgisteam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from courses import views as courses_views
from courses.models import Syllabus
from kgisteam import views as kgisteam_views


# https://www.webforefront.com/django/admincustomlayout.html
admin.site.site_header = 'KGIsteam admin'
admin.site.site_title = 'KGIsteam admin'
admin.site.index_title = 'KGIsteam administration'

info_dict = {
    'queryset': Syllabus.objects.all(),
    'date_field': 'last_modified',
}

urlpatterns = [
    path('', courses_views.courses_home, name='home'),
    path('admin/', admin.site.urls),
    path('courses/', include('courses.urls')),
    path('info/', include('info.urls')),
    url(r'^markdownx/', include('markdownx.urls')),

    # Sitemap https://docs.djangoproject.com/en/3.0/ref/contrib/sitemaps/
    path('sitemap.xml', sitemap, {'sitemaps': {
            'courses': GenericSitemap(info_dict, priority=0.5)
            }
        },
        name='django.contrib.sitemaps.views.sitemap'
    ),

    # URLs for testing
    path('test/error404', kgisteam_views.error_404, name='error404'),
    path('test/error500', kgisteam_views.error_500, name='error500'),
]

# Error handlers
handler404 = kgisteam_views.error_404
handler500 = kgisteam_views.error_500

# https://docs.djangoproject.com/en/2.2/howto/static-files/#serving-files-uploaded-by-a-user-during-development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
