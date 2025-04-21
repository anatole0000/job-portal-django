from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('applications/', views.user_applications, name='user_applications'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('create/', views.create_job, name='create_job'),
    path('job/<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    
    path('profile/', views.user_profile, name='user_profile'),
    path('job/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('application/<int:application_id>/update_status/', views.update_application_status, name='update_application_status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
