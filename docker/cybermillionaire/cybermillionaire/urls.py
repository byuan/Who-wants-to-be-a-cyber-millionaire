"""cybermillionaire URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import reverse
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^primary-school', views.start1, name='primary-school'),  # Static Primary School
    url(r'^secondary-school', views.start2, name='secondary-school'),  # Static Secondary School
    url(r'^college', views.start3, name='college'),  # Static College
    url(r'^expert', views.start4, name='expert'),  # Static Expert

    # Add dynamic URL patterns
    url(r'^dynamic-primary-school', views.dynamic_start1, name='dynamic-primary-school'),  # Dynamic Primary School
    url(r'^dynamic-secondary-school', views.dynamic_start2, name='dynamic-secondary-school'),  # Dynamic Secondary School
    url(r'^dynamic-college', views.dynamic_start3, name='dynamic-college'),  # Dynamic College
    url(r'^dynamic-expert', views.dynamic_start4, name='dynamic-expert'),  # Dynamic Expert

    url(r'^save-results/$', views.save_results, name='save_results'),
    
    url(r'', views.index, name='start-page'),
    ]

    
    
