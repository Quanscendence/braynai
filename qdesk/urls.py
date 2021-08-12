from django.contrib import admin
from django.conf.urls import url,include
from django.urls import path
from .  import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
app_name = 'qdesk'





urlpatterns = [

url (r'^$', views.QDeskView.as_view(),name='qdesk'),
url(r'^ticket-details/(?P<pk>\d+)/$', views.TicketDetailsView.as_view(), name='ticket-details'),
url(r'^issue-details/(?P<pk>\d+)/(?P<tpk>\d+)/$', views.IssueDetailsView.as_view(), name='issue-details'),
url(r'^ticket-solution/(?P<pk>\d+)/(?P<tpk>\d+)/create$', views.TicketSolutionView.as_view(), name='ticket-solution-post'),
url(r'^supprt-ticket-details/(?P<pk>\d+)/$',views.AdminTicketDetailsView.as_view(),name='admin-ticket-details'),
url (r'^add-client/$', views.ClientView.as_view(),name='add-client'),
url(r'^ticket-status/(?P<pk>\d+)/$', views.TicketStatusChangeView.as_view(), name='ticket-status-change'),
url(r'^create-ticket/(?P<pk>\d+)/$',views.TicketCreateView.as_view(),name='create-ticket')
]
