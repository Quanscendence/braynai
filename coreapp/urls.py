from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url
from coreapp import views
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth import views as auth_views


app_name = 'coreapp'

urlpatterns = [
    path('', views.HomeView.as_view(),name="home"),
    url(r'^(?P<pk>\d+)/$', views.UserActivationSuccessView.as_view(),name="user-project-activate"),

    url(r'^about/$', views.AboutView.as_view(),name="about"),
    url(r'^blogs/$', views.BlogView.as_view(),name="blogs"),
    url(r'^privacy-policy/$', views.PrivacyPolicyView.as_view(),name="privacy-policy"),
    url(r'^terms-conditions/$', views.TermsConditionsView.as_view(),name="terms-conditions"),
    url(r'^services/$', views.ServicesView.as_view(),name="services"),
    url(r'^go-to/(?P<pk>\d+)/project/$', views.ProjectSupport.as_view(),name="go-to-project"),
    url(r'^project/$', views.AddProjectView.as_view(),name="project"),
    url(r'^project-endpoint/(?P<pk>\d+)/api/request/$', views.endpoint_ml_api,name="projectendpoint-api-request"),
    url(r'^project-endpoint/(?P<pk>\d+)/create$', views.ProjectEndPointCreateView.as_view(),name="projectendpoint-create"),
    url(r'^project/create/ajax/$', views.ProjectCreateAjax.as_view(),name="project-create-ajax"),
    url(r'^delete-project/(?P<pk>\d+)/$', views.DeleteProjectView.as_view(),name="delete-project"),
    url(r'^restore-projects/$', views.RestoreProjects.as_view(),name="restore-projects"),
    url(r'^restore-project/(?P<pk>\d+)/$', views.restore_project,name="restore-project"),
    url(r'^logout/', LogoutView.as_view(),name = 'logout'),
    url(r'^upload/(?P<pk>\d+)/$', views.FileUploadView.as_view(),name="upload"),
    url(r'^file/read/$', views.file_read_ajax,name="file-read"),
    url(r'^file/relationship/(?P<pk>\d+)/$', views.RelationCreate,name="file-relation-create"),
    url(r'^file/metadata/(?P<pk>\d+)/$', views.MetadataGet,name="file-metadata-create"),
    url(r'^file/upload/$', views.file_upload,name="file-upload"),
    url(r'^project-update/(?P<pk>\d+)/$',  views.ProjectUpdateView.as_view(), name='project-update'),
    url(r'^successful/(?P<pk>\d+)/$', views.OTPAuthenticate.as_view(),name="successful"),
    url(r'^single-project/(?P<pk>\d+)/$', views.ProjectDetailsView.as_view(),name="single-project"),
    url(r'^single-project-details/(?P<pk>\d+)/$', views.SingleProjectDetails.as_view(),name="single-project-details"),
    url(r'^delete-integration/(?P<pk>\d+)/$', views.DeleteIntegration.as_view(),name="integration-delete"),
    url(r'^delete-endpoint/(?P<pk>\d+)/$', views.ProjectEndPointDelete.as_view(),name="endpoint-delete"),
    url(r'^delete-dashboard/(?P<pk>\d+)/$', views.ProjectDashboardDelete.as_view(),name="dashboard-delete"),
    url(r'^file/relationship/delete/(?P<pk>\d+)/$', views.RelationDelete,name="relationdelete"),
    url(r'^search/$',  views.SearchView.as_view(), name='search'),
    url(r'^add-users/(?P<pk>\d+)/$',  views.AddUserView.as_view(), name='add-users'),
    url(r'^accept/(?P<pk>\d+)/$', views.accept_view,name="accept"),
    url(r'^update-user-permission/(?P<pk>\d+)/$', views.UpdateProjectUser.as_view(),name="update-user-permission"),
    url(r'^delete-user/(?P<pk>\d+)/$', views.ProjectUserDelete.as_view(),name="delete-user"),
    url(r'^test/(?P<pk>\d+)/$', views.TestView.as_view(),name="TestView"),
    url(r'^data-search/(?P<pk>\d+)/$', views.DataSearch.as_view(), name="data-search"),
    url(r'^dashboard/(?P<pk>\d+)/update/$', views.ProjectDashboardEditView.as_view(), name="dashboard-update"),
    url(r'^save-dashboard/(?P<pk>\d+)/$', views.DashboardSaveFormView.as_view(), name="save-dashboard"),
    url(r'^all-dashboards/(?P<pk>\d+)/$', views.AllDashboards.as_view(), name="all-dashboards"),
    url(r'^project-dashboard/(?P<pk>\d+)/$', views.ProjectDashboardView.as_view(), name="project-dashboard"),
    url(r'^check-email/(?P<pk>\d+)/$', views.check_email,name="check-email"),

    url(r'^updated-notification-read/$', views.update_notification_read, name="updated-notification-read"),
    # query urls
    url(r'^project-query/(?P<pk>\d+)/$', views.ProjectQueryView.as_view(), name="project-query"),
    url(r'^project/(?P<pk>\d+)/query/$', views.ProjectQueryDetails.as_view(),name="project-query-details"),
    url(r'^project-query/update/(?P<pk>\d+)/$', views.ProjectQueryUpdateView.as_view(), name="project-query-update"),
    url(r'^project-query/delete/$', views.ProjectQueryDeleteView.as_view(), name="project-query-delete"),
    #endpoint urls
    url(r'^endpoint/(?P<pk>\d+)/$', views.ProjectEndPointView.as_view(),name="project-end-point"),
    url(r'^endpoint/(?P<pk>\d+)/algorithm/prediction/$', views.MlPredictionView.as_view(),name="project-end-point-predictions"),
    url(r'^endpoint/(?P<pk>\d+)/algorithm/update/$', views.EndPointAlgorithmUpdateView.as_view(),name="project-end-point-update"),

    url(r'^endpoint/(?P<pk>\d+)/plot/$', views.EndPointPlotView.as_view(),name="project-end-point-plot"),
    url(r'^endpoint/(?P<pk>\d+)/algorithm/delete/$', views.MLDeleteView.as_view(),name="project-end-point-algorithm"),
    url(r'^endpoint/(?P<pk>\d+)/edit/$', views.ProjectEndpointEditView.as_view(),name="project-end-point-edit"),
    url(r'^endpoint/(?P<pk>\d+)/ml/$', views.EndPointAlgorithmView.as_view(),name="project-end-point-ml"),
    url(r'^endpoint/(?P<pk>\d+)/new-column-creation/$',views.EndpointNewColumnCreationView.as_view(),name='project-endpoint-newcolumn-creation'),

    #dashboard urls
    url(r'^dashboard/$', views.DashboardView.as_view(),name="dashboard"),
    url(r'^dashboard/create/(?P<pk>\d+)/$', views.DashboardCreateView.as_view(),name="dashboard-create"),
    url(r'^dashboard/query/algorithm/(?P<pk>\d+)/delete/$', views.DashboardQueryAlgorithmDeleteView.as_view(),name="dashboard-query-algorithm-delete"),
    # url(r'^dashboard/multiple/query/create/(?P<pk>\d+)/$', views.DashboardMultipleQueryCreate.as_view(),name="dashboard-multiple-query-create"),
    url(r'^project-dashboard/multiple/query/(?P<pk>\d+)/$', views.MultipleQueryDashbordView.as_view(), name="project-dashboard-multiple"),
    url(r'^multiple/query/dashboard/create/$', views.DashboardMultipleQueryCreate.as_view(), name="project-multiple-query-dashboard"),
    url(r'^project-query/legend/(?P<pk>\d+)/$', views.DashboardLegend.as_view(), name="query-legend"),
    url(r'^endpoint-query/legend/(?P<pk>\d+)/$', views.EndpointPlotLegend.as_view(), name="endpoint-legend"),
    url(r'^project/query/endpoint/(?P<pk>\d+)/$', views.ProjectQueryAlignmentView.as_view(), name="project-query-alignment"),
    url(r'^project/endpoint/alignment/(?P<pk>\d+)/$', views.ProjectEndpointAlignmentView.as_view(), name="project-end-point-alignment"),
    url(r'^endpoint/dashboard/(?P<pk>\d+)/create/$', views.EndPointDashboardCreateView.as_view(), name="end-point-dashboard-create"),
    url(r'^dashboard/autocomplete/$', views.DashboardAutocomplete.as_view(), name="dashboard-autocomplete"),
    url(r'^projectrow-col-data/(?P<pk>\d+)/$', views.ProjectRowColView.as_view(), name="project-rows-col-data"),
    url(r'^shared-dashboard/(?P<key>[\w-]+)/$', views.SharedDashboardView.as_view(), name="shared-dashboard-view"),
    url(r'^email-dashboard-link/(?P<pk>\d+)/$', views.ProjectDashboardeEmail.as_view(), name="share-dashboard-view"),
    url(r'^project-end-point/(?P<pk>\d+)/$', views.ProjectEndPointWindoowView.as_view(), name="endpoint-window-display"),
    url(r'^filtered-row-display/(?P<pk>\d+)/$', views.DataframeDisplayView.as_view(), name="data-df-disply"),
    url(r'^zest/(?P<pk>\d+)/$',views.Test.as_view(), name="test-permission"),
    url(r'^project-billing-update/(?P<pk>\d+)/$', views.ProjectBillingUpdateView.as_view(), name="project-billing-update"),
    url(r'^public-shared-dashboard/(?P<key>[\w-]+)/$', views.DashboardPublicView.as_view(), name="public-shared-dashboard-view"),
    url(r'^project-dashboard/(?P<pk>\d+)/refresh$', views.ProjectDashboardRefreshView.as_view(), name="project-dashboard-refresh"),
    url(r'^invoice/(?P<pk>\d+)/$',views.InvoiceView.as_view(),name="invoice"),
    url(r'^api/data/(?P<pk>\d+)/$', views.ApiDataView.as_view(), name='add-on'),
    url(r'^sitemap.xml/$', views.Sitemap, name='sitemap'),

    url (r'^add-on/(?P<pk>\d+)/$',views.AddOnFileView.as_view(),name='add-on'),
    url (r'^add-on/nan-fill/(?P<pk>\d+)/$',views.AddOnFileMultipleFilesView.as_view(),name='add-on-nan-fill'),
    url (r'^add-on/final/(?P<pk>\d+)/$',views.AddOnFileFinalView.as_view(),name='add-on-final'),





]
