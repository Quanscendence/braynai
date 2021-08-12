"""dsaas URL Configuration

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
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from rest_framework_simplejwt import views as jwt_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import debug_toolbar

urlpatterns = [
    path('admin/doc/',include('django.contrib.admindocs.urls')),
    path('profiler/',include('silk.urls')), # comment when we deploy in production #TODO
    path('master/', admin.site.urls),
    path('api/v1/',include('api.urls')),
    path('qdesk/', include('qdesk.urls')),
    path('', include('coreapp.urls')),
    path('customer/', include('login.urls')),
    path('administrator/', include('adminapp.urls')),
    path('dataintegration/', include('dataintegration.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('seo/', include('seo_app.urls')),
    path('blog/', include('webapp.urls')),
    path('tasks/', include('cronjob.urls')),
    url(r'^captcha/', include('captcha.urls')),


    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include('django.contrib.auth.urls')),
    # path('debug/', include(debug_toolbar.urls)),
]
# urlpatterns += staticfiles_urlpatterns()
