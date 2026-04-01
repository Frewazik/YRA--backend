from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Parent, Transaction
from rest_framework import viewsets
from .models import Activity, Event, TeacherProfile, WeeklySlot,  Parent, Transaction, Student
from .serializers import (
    ActivitySerializer, EventSerializer, 
    TeacherProfileSerializer, WeeklySlotSerializer
)

# Используем ReadOnlyModelViewSet. Она означает, что сайт сможет ТОЛЬКО ЧИТАТЬ список кружков. 
# Изменять или удалять их можно строго через админку.

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    # queryset - это команда базе данных: что именно достать?
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
    def post(self, request):
        data = request.data
        
        # 1. Достаем все данные из запроса фронтенда
        parent_name = data.get('parent_name')
        phone = data.get('phone')
        child_name = data.get('child_name')
        grade = data.get('grade')
        dob = data.get('dob') # Может быть пустым
        comments = data.get('comments', '') # Комментарии и источник
        
        # 2. Проверяем обязательные поля 
        if not parent_name or not phone or not child_name or not grade:
            return Response(
                {'error': 'ФИО родителя, номер телефона, ФИО и  класс ребенка обязательны!'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Ищем или создаем Родителя (защита от дублей по телефону)
        parent, created_parent = Parent.objects.get_or_create(
            phone=phone,
            defaults={'full_name': parent_name}
        )

        # 4. Создаем карточку Ученика и привязываем к Родителю
        student, created_student = Student.objects.get_or_create(
            full_name=child_name,
            parent=parent,
            defaults={
                'school_grade': grade,
                # Если дату не передали, оставляем пустой, чтобы база не ругалась
                'dob': dob if dob else None 
            }
        )

        # 5. Создаем заявку (транзакцию в статусе PENDING)
        # для бронирования на 15 минут
        Transaction.objects.create(
            parent=parent,
            amount=0,
            status='PENDING'
        )

        return Response(
            {'message': 'Ура! Заявка с полными данными успешно принята!'}, 
            status=status.HTTP_201_CREATED
        )