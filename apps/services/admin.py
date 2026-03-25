from django.contrib import admin
from .models import (
    Parent, Student, TeacherProfile, Activity, Event, 
    SubscriptionPlan, WeeklySlot, ScheduleException,
    Enrollment, Attendance, Subscription, Transaction
)

#  КЛИЕНТЫ 

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    # Что показываем в списке
    list_display = ('full_name', 'phone')
    # По каким полям работает верхняя строка поиска
    search_fields = ('full_name', 'phone')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Добавили вывод родителя прямо в списке детей
    list_display = ('full_name', 'parent', 'school_grade', 'dob')
    # Фильтр справа (по классу)
    list_filter = ('school_grade',)
    # Поиск по имени ребенка или телефону родителя
    search_fields = ('full_name', 'parent__phone') 

#  КОМАНДА 

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name', 'display_order')
    search_fields = ('user__last_name', 'user__first_name')

#  ПРОДУКТЫ И АФИША 

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    # когда будете вводить название сам на лету сгенерирует английский URL 
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'price', 'is_active')
    list_filter = ('is_active', 'date_time')
    search_fields = ('title',)

#  РАСПИСАНИЕ И ЖУРНАЛ 

@admin.register(WeeklySlot)
class WeeklySlotAdmin(admin.ModelAdmin):
    list_display = ('activity', 'day_of_week', 'start_time', 'end_time', 'teacher')
    # Добавили фильтры справа, чтобы  можно быстро отфильтровать 
    # все уроки на "Понедельник" или все уроки "Английского"
    list_filter = ('day_of_week', 'activity', 'teacher')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'slot')
    list_filter = ('date', 'status', 'slot__activity')    