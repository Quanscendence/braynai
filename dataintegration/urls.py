from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url
from dataintegration import views

app_name = 'dataintegration'

urlpatterns = [
    url(r'^list/(?P<pk>\d+)/$', views.IntegrationListView.as_view(),name="list"),
    url(r'^drive-details/(?P<pk>\d+)/$', views.DriveDetailsView.as_view(),name="drive-details"),
    url(r'^sheet-details/(?P<pk>\d+)/$', views.SheetDetailsView.as_view(),name="sheet-details"),
    url(r'^sheet-na-filling/(?P<pk>\d+)/$', views.SheetNnaFillView.as_view(),name="sheet-details-nan"),

    url(r'^dropbox-details/(?P<pk>\d+)/$', views.DropBoxDetailsView.as_view(),name="dropbox-details"),
    url(r'^onedrive-details/(?P<pk>\d+)/$', views.OneDriveDetailsView.as_view(),name="onedrive-details"),
    # url(r'^segment-details/(?P<pk>\d+)/$', views.SegmentDetailsView.as_view(),name="segment-details"),
    url(r'^segment-receive/$', views.SegmentDetailsView.as_view(),name="segment-receive"),
    url (r'^api-data/(?P<pk>\d+)/$',views.ApiDataRead.as_view(),name='api-data-add'),
    url (r'^api-data/(?P<pk>\d+)/nan-filling$',views.ApiNnaFillView.as_view(),name='api-data-nanfilling'),
    url (r'^sheet-project-create/(?P<pk>\d+)/$',views.ProjectGoogleSheetsView.as_view(),name='sheet-project-create')
]
