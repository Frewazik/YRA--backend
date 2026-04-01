from rest_framework import serializers
from .models import Activity, Event, TeacherProfile, WeeklySlot, GalleryPhoto
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

# 1. Сериализатор для Кружков и Направлений
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__' 

# 2. Сериализатор для Афиши
class EventSerializer(serializers.ModelSerializer):
    # Перехватываем стандартную цену
    price = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.INT)
    def get_price(self, obj):
        if obj.price:
            return int(obj.price * 100) # Переводим рубли в копейки для фронта
        return 0

# 3. Сериализатор для Учителей 
class TeacherProfileSerializer(serializers.ModelSerializer):
    # Вытаскиваем данные из встроенной модели User
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = TeacherProfile
        # Лучше перечислить явно, чтобы подхватились новые поля
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'photo', 'bio'] 

# 4. Сериализатор для Расписания 
class WeeklySlotSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True) 
    teacher = TeacherProfileSerializer(read_only=True) 
    spots_available = serializers.SerializerMethodField()

    class Meta:
        model = WeeklySlot
        fields = '__all__'

    @extend_schema_field(OpenApiTypes.INT)
    def get_spots_available(self, obj):
        # TODO: Заменить на реальный подсчет, когда сделаем систему бронирования
        # Пока отдаем максимум мест, чтобы API не падало с ошибкой
        return obj.max_capacity
    
class GalleryPhotoSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source='image', read_only=True)
    thumbnail = serializers.ImageField(source='image', read_only=True) # Пока отдаем оригинал вместо миниатюры

    class Meta:
        model = GalleryPhoto
        fields = ['id', 'url', 'alt', 'thumbnail']   

class LeadCreateSerializer(serializers.Serializer):
    # Обязательные поля
    parent_name = serializers.CharField(max_length=255, help_text="Имя родителя")
    phone = serializers.CharField(max_length=20, help_text="Номер телефона родителя")
    child_name = serializers.CharField(max_length=255, help_text="Имя ребенка")
    
    # Необязательные поля 
    grade = serializers.CharField(max_length=50, required=False, help_text="Класс или возраст ребенка")
    dob = serializers.DateField(required=False, help_text="Дата рождения ребенка (в формате YYYY-MM-DD)")
    comments = serializers.CharField(required=False, help_text="Дополнительный комментарий")

class ActivityShortSerializer(serializers.ModelSerializer):
    "Специальный мини-сериализатор  для главной страницы"
    class Meta:
        model = Activity
        # Отдаем строго только то, что нужно для дизайна главной
        fields = ['id', 'title', 'description', 'slug', 'is_featured']    