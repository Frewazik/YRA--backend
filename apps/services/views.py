from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Parent, Transaction
from rest_framework import viewsets
from .models import Activity, Event, TeacherProfile, WeeklySlot
from .serializers import (
    ActivitySerializer, EventSerializer, 
    TeacherProfileSerializer, WeeklySlotSerializer
)

# Используем ReadOnlyModelViewSet. Она означает, что сайт сможет ТОЛЬКО ЧИТАТЬ список кружков. 
# Изменять или удалять их можно строго через админку.

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    # queryset - это команда базе данных: "Что именно достать?"
    # filter(is_active=True) означает, что скрытые кружки на сайт не попадут
    queryset = Activity.objects.filter(is_active=True)
    
    # serializer_class - указываем, сериализатор использовать
    serializer_class = ActivitySerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(is_active=True)
    serializer_class = EventSerializer


class TeacherProfileViewSet(viewsets.ReadOnlyModelViewSet):
    # Сортируем учителей по тому самому полю display_order, которое мы заложили в ТЗ
    queryset = TeacherProfile.objects.all().order_by('display_order')
    serializer_class = TeacherProfileSerializer


class WeeklySlotViewSet(viewsets.ReadOnlyModelViewSet):
    # Сортируем расписание: сначала понедельники (по времени), потом вторники и т.д.
    queryset = WeeklySlot.objects.all().order_by('day_of_week', 'start_time')
    serializer_class = WeeklySlotSerializer

class LeadCaptureView(APIView):
    # Метод POST означает, что мы ждем данные ОТ сайта
    def post(self, request):
        # Достаем данные, которые прислал фронтенд
        name = request.data.get('name')
        phone = request.data.get('phone')

        if not name or not phone:
            return Response(
                {'error': 'Имя и телефон обязательны'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Умный поиск: ищем родителя по номеру телефона. 
        # Если такого нет - создаем нового. Это спасет базу от дублей!
        parent, created = Parent.objects.get_or_create(
            phone=phone,
            defaults={'full_name': name}
        )

        # 2. Создаем новую заявку (Транзакцию) со статусом "Ожидает"
        Transaction.objects.create(
            parent=parent,
            amount=0, # Сумму Надежда обсудит по телефону
            status='PENDING'
        )

        return Response(
            {'message': 'Ура! Заявка успешно принята!'}, 
            status=status.HTTP_201_CREATED
        )    