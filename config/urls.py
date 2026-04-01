from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # 1. Путь в нашу админку
    path('admin/', admin.site.urls),
    
    # 2. Главный рубильник для API. 
    # Говорит: "Все запросы, начинающиеся на /api/, в папке apps.services"
    path('api/', include('apps.services.urls')), 

    # 3. Выгружает схему API для Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 4. Для интерфейса Swagger
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# 3. Эта штука нужна, чтобы Джанго умел показывать картинки афиши 
# пока мы работаем на локальном компьютере
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)