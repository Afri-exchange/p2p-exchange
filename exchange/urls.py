"""exchange URL Configuration

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
from offers import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from django.urls import path, re_path
from django.conf.urls import handler404

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    # path('new', views.new),
    path('new', views.CreateOfferView.as_view(), name='create_offer'),
    # path('offers', views.show, name='offers'),
    path('offers', views.UserOfferView.as_view(), name='offers'),
    # path('', views.showall, name='home'),
    path('', views.ShowOffersView.as_view(), name='home'),

    re_path(r'^signup/$', accounts_views.signup, name='signup'),
    re_path(r'^login/$',
            auth_views.LoginView.as_view(template_name='jinja/login.html'), name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),

    re_path(r'^reset/$',
            auth_views.PasswordResetView.as_view(
                template_name='jinja/password_reset.html',
                email_template_name='jinja/password_reset_email.html',
                subject_template_name='jinja/password_reset_subject.txt'
            ),
            name='password_reset'),
    re_path(r'^reset/done/$',
            auth_views.PasswordResetDoneView.as_view(
                template_name='jinja/password_reset_done.html'),
            name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(
                template_name='jinja/password_reset_confirm.html'),
            name='password_reset_confirm'),
    re_path(r'^reset/complete/$',
            auth_views.PasswordResetCompleteView.as_view(
                template_name='jinja/password_reset_complete.html'),
            name='password_reset_complete'),

    re_path(r'^settings/account/$',
            accounts_views.UserUpdateView.as_view(), name='my_account'),
    re_path(r'^settings/password/$', auth_views.PasswordChangeView.as_view(template_name='jinja/password_change.html'),
            name='password_change'),
    re_path(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='jinja/password_change_done.html'),
            name='password_change_done'),
    
    re_path(r'offer/(?P<id>\d+)/$', views.BidListView.as_view(), name='view_bids'),
    re_path(r'offer/(?P<id>\d+)/new/$',
            views.CreateBidView.as_view(), name='new_bid'),
    re_path(r'bid/(?P<bid_id>\d+)/edit/$',
            views.BidUpdateView.as_view(), name='edit_bid'),
    # path('edit/<int:id>', views.PostUpdateView.as_view()),
    path('update/<int:id>', views.OfferUpdateView.as_view(), name='update_offer'),
    # path('delete/<int:id>', views.destroy),
    path('delete/<int:id>', views.OfferDeleteView.as_view(), name='delete_offer'),
    re_path(r'bid/delete/(?P<id>\d+)/$', views.BidDeleteView.as_view(), name='delete_bid'),
]

handler404 = 'offers.views.error_404_view'
