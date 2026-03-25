from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Путь в нашу админку
    path('admin/', admin.site.urls),
    
    # 2. Главный рубильник для API. 
    # Говорит: "Все запросы, начинающиеся на /api/, ищи в папке apps.services"
    path('api/', include('apps.services.urls')), 
]

# 3. Эта штука нужна, чтобы Джанго умел показывать картинки (афиши) 
# пока мы работаем на локальном компьютере
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)