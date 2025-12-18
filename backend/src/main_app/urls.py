from django.urls import path, include


urlpatterns = [
	path('api/auth/', include('user_app.urls')),
	path('api/scheduling/', include('scheduling_app.urls')),
]