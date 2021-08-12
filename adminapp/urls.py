from django.conf.urls import url
from adminapp import views
from django.contrib.auth.views import LoginView,LogoutView


app_name = 'adminapp'

urlpatterns = [

    url(r'^admin-dashboard/$', views.AdminDashboard.as_view(),name="admin-dashboard"),
    url(r'^conversion-inputs/$', views.ConversionTable.as_view(),name="conversion-inputs"),
    url(r'^conversion-table/$', views.ConversionTableView.as_view(),name="conversion-table"),
    url(r'^machine-learning/$', views.MachineLearningView.as_view(),name="machine-learning"),
    url(r'^project/(?P<pk>\d+)/$', views.SingleProjectDetails.as_view(),name="project"),
    url(r'^api-request/(?P<pk>\d+)/status/$', views.SingleMachineLearning.as_view(),name="api-request-status"),
    url(r'^project/pricing/delete/(?P<pk>\d+)/$', views.ProjectPricingDelete.as_view(),name="project-pricing-delete"),

    url(r'^actions/$',  views.AllActions.as_view(), name='actions'),
    url(r'^project-pricing/$',  views.ProjectPricingView.as_view(), name='project-pricing'),
    url(r'^single-project-pricing/$',  views.SingleProjectPricingCreate.as_view(), name='single-project-pricing'),

    url(r'^tax/$',  views.TaxView.as_view(), name='tax'),

    url(r'^project-invoice/$',  views.ProjectInvoiceView.as_view(), name='project-invoice'),
    url(r'^all_invoice/$',  views.all_invoice, name='all_invoice'),
    url(r'^customer-dashboard/$',  views.CustomerDashboard.as_view(), name='customer-dashboard'),
    url(r'^all-users/$',  views.all_users, name='all_users'),
    url(r'^all-projects/$',  views.all_projects, name='all-projects'),
    url(r'^', LoginView.as_view()),
    

]
