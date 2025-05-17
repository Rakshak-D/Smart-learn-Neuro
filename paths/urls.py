from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'paths', views.LearningPathViewSet)
router.register(r'user_paths', views.UserPathViewSet)

urlpatterns = [
    path('', views.path_list, name='path_list'),
    path('<int:pk>/', views.path_detail, name='path_detail'),
    path('api/', include(router.urls)),
]
