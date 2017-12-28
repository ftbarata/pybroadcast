"""pybroadcast URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from pybroadcast.core.views import home, login, logout, about, sendMessage, historico, getReverseDns,teste, configuracoes, deleteAuthorizedUser, ajaxRequestLdapUser,downloads


urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('downloads/', downloads, name='downloads'),
    path('sendmessage/', sendMessage, name='sendmessage'),
    path('logout/', logout, name='logout'),
    path('sobre/', about, name='about'),
    path('reversedns/', getReverseDns, name='reversedns'),
    path('historico/', historico, name='historico'),
    path('admin/', admin.site.urls),
    path('teste/<str:username>', teste, name='teste'),
    path('ajax/<str:username>', ajaxRequestLdapUser, name='ajax'),
    path('deleteauthorizeduser/<int:id>', deleteAuthorizedUser, name='deleteauthorizeduser'),
    path('configuracoes/', configuracoes, name='configuracoes')
]

