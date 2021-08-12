from django.urls import path,include
from django.conf.urls import url
from webapp import views
from .views import BlogUpdateView,BlogDeleteView


app_name = 'webapp'
urlpatterns = [
    url(r'^blog/', views.DashBoard.as_view(),),
    url(r'^edit_delete_blogs/', views.AllBlogChangeView.as_view(),name="edit_delete_blogs"),
    url(r'^updates/(?P<pk>[\d]+)$', BlogUpdateView.as_view(), name='updates'),
    url(r'^delete/(?P<pk>[\d]+)$', BlogDeleteView.as_view(), name='delete'),
    url(r'^all-blogs/$',views.AllBlogView.as_view(),name="all_blogs"),
    path('<slug:title_slug>/',views.SingleBlogView.as_view(),name="single_blog")


]
