from rest_framework import serializers
from .models import Activity, Event, TeacherProfile, WeeklySlot

# 1. Сериализатор для Кружков и Направлений
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__' # Команда: Отдай фронту все поля из базы

# 2. Сериализатор для Афиши 
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

# 3. Сериализатор для Учителей
class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'

# 4. Сериализатор для Расписания
class WeeklySlotSerializer(serializers.ModelSerializer):
    # Если мы просто отдадим расписание, фронтенд получит: "activity: 1, teacher: 2".
    # Чтобы этого не произошло, мы пишем внутренний сериализатор 
    activity = ActivitySerializer(read_only=True) # для кружков
    teacher = TeacherProfileSerializer(read_only=True) # для учителей

    class Meta:
        model = WeeklySlot
        fields = '__all__'