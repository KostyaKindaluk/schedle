from django.urls import re_path

from . import views


urlpatterns = [
	re_path(r'^schedulings/?$', views.SchedulingViewSet.as_view({
		'get': 'list',
		'post': 'create'
	}), name='scheduling-list'),
	
	re_path(r'^schedulings/(?P<pk>\d+)/?$', views.SchedulingViewSet.as_view({
		'get': 'retrieve',
		'delete': 'destroy'
	}), name='scheduling-detail'),
]