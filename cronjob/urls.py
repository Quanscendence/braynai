from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url
from cronjob import views
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth import views as auth_views


app_name = 'cronjob'


urlpatterns = [
    url(r'^report/$', views.ProjectDashboardeEmail.as_view(), name="share-dashboard-view"),
    url(r'^five-minutes-cron/$', views.FiveMinutesCron.as_view(), name="five-minutes-cron"),
    url(r'^one-day-cron/$', views.OneDayCron.as_view(), name="one-day-cron"),
    url(r'^sub-df-update/',views.ProjectEndPointSubDfView.as_view(),name='sub-df-update'),

]