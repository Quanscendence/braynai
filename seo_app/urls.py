from django.urls import path,include
from seo_app import views
from django.conf.urls import url
from seo_app.views import SingleUpdateView

#writing urls for each page of the website
app_name = 'seo'
urlpatterns = [

    url(r'dashboard/',views.Dashboard.as_view(),name="dashboard"),
    url(r'seo_updates/',views.SeoUpdateView.as_view(),name="seo_updates"),
    url('^updates/(?P<pk>[\d]+)/$', SingleUpdateView.as_view(), name='updates'),


]
