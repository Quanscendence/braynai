from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url
from login import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from login.views import ProfileUpdateView

app_name = 'login'

urlpatterns = [
    url(r'^signup/$', views.CustomerSignUpView.as_view(),name="signup"),
    url(r'^verify-contact-no/$', views.VerifyCustomerPhone,name="otp-send"),
    url(r'^login/$', views.LoginView.as_view(),name="login"),
    url(r'^login-permission/$', views.LoginPermission.as_view(),name="login-permission"),
    url(r'^updates/(?P<pk>\d+)/$',  views.ProfileUpdateView.as_view(), name='updates'),
    url(r'^password-reset/$', views.PasswordResetView.as_view(),name="password-reset"),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^signup-link/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.SignupUser.as_view(),name="signup-link"),
    url(r'^verify_email/$', views.verify_email,name="verify_email"),
    url(r'^starthere/$', views.BasicSignupView.as_view(),name="basic-signup"),
    url(r'^account_activation_sent/$',views.account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
]
