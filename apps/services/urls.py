from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, EventViewSet, 
    TeacherProfileViewSet, WeeklySlotViewSet, LeadCaptureView
)

# Создаем роутер (автоматический генератор ссылок)
router = DefaultRouter()

# Регистрируем наши Вьюхи в роутере. 
# Первый аргумент - это то, как будет выглядеть ссылка в браузере.
router.register(r'activities', ActivityViewSet)
router.register(r'events', EventViewSet)
router.register(r'teachers', TeacherProfileViewSet)
router.register(r'schedule', WeeklySlotViewSet)

# Собираем все сгенерированные ссылки в один список
urlpatterns = [
    # include(router.urls) включает все пути, которые создал роутер
    path('', include(router.urls)),
    path('lead/', LeadCaptureView.as_view(), name='lead-capture'),
]

