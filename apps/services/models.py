from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import CheckConstraint, Q

# --- ЛЮДИ ---

class TeacherProfile(models.Model):
    # В Django уже есть таблица User (логин, пароль, админ или нет)
    # поэтому подключаем её, а всё чего не хватает прописывает сами
    # OneToOneField - это связя один к одному
    # У каждого юзера 1 профиль учителя
    # И 1 профиля учителя принадлежить только 1 юзеру
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,  # если удалить юзера, то удаляется и привязанный профиль
        related_name='teacher_profile', # чтоб подгружать опр-ный профиль опр-ному юзеру
        verbose_name="Пользователь (Логин/Пароль)") #как выглядит в админке
    # Отчества нет в user, добавляем сюда
    middle_name = models.CharField("Отчество", max_length=50, blank=True)
    # ImageField хранит не саму картинку, а путь к ней
    photo = models.ImageField("Фото", upload_to='teachers/', blank=True, null=True)
    # Большое текстовое поле без лимита
    bio = models.TextField("О себе / Биография", blank=True)
    # PositiveIntegerField - только целые положит-е числа
    display_order = models.PositiveIntegerField("Порядок отображения", default=1)
    class Meta:
        # имя таблицы для админки
        verbose_name = "Профиль учителя"
        verbose_name_plural = "Учителя"
        # правило сортировки
        ordering = ['display_order']
    # как назвать, то что выводиться в таблицу        
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name} {self.middle_name}"    

# КЛИЕНТЫ (РОДИТЕЛИ И ДЕТИ)

class Parent(models.Model):
    full_name = models.CharField("ФИО родителя", max_length=150)
    # unique=True - каждый родитель имеет уникальный номер телефона
    phone = models.CharField("Номер телефона", max_length=20, unique=True, db_index=True)
    # Сюда будут падать вопросы или комментарии, которые клиент пишет в форме на сайте
    comments = models.TextField("Комментарии / Вопросы с сайта", blank=True)

    class Meta:
        verbose_name = "Родитель"
        verbose_name_plural = "Родители"

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class Student(models.Model):
    parent = models.ForeignKey(
        Parent, 
        on_delete=models.CASCADE,
        #  свойство, чтобы достать детей родителя одной командой parent.children.all()      
        related_name='children',    
        verbose_name="Родитель"  # для админки     
    )
    
    full_name = models.CharField("ФИО ребенка", max_length=150)

    # Класс в школе (от 1 до 11). null=True - в БД может быть пустота, если пока не знаем
    school_grade = models.CharField("Класс", max_length=20, blank=True)

    # null=True: Разрешает самой базе данных хранить пустоту (NULL). 
    # В отличие от текста, дата не может быть "пустой строкой", она либо есть, либо NULL.
    # db_index=True: Создает внутренний справочник в БД. Позволяет мгновенно находить детей нужного возраста.
    dob = models.DateField("Дата рождения", blank=True, null=True, db_index=True)

    health_issues = models.TextField("Особенности здоровья", blank=True)

    class Meta:
        verbose_name = "Ученик"
        # Как называть раздел в админке в целом
        verbose_name_plural = "Ученики"

    def __str__(self): 
        # Если этого не написать, в списке учеников будут безликие "Student object (1)
        return self.full_name 
    
#  ПРОДУКТЫ И УСЛУГИ 

class Activity(models.Model): 
    # 'CLUB' - то, что хранится в бд
    # 'Кружок' - то, что видно в админке.
    CATEGORY_CHOICES = [
        ('CLUB', 'Кружок'), 
        ('SERVICE', 'Услуга') 
    ]
    
    name = models.CharField("Название", max_length=100)
    
    # SlugField - генерирует красивые ссылки для сайта.
    # Вместо site.ru/activity/1 будет site.ru/activity/english
    # unique=True гарантирует, что двух одинаковых ссылок не будет.
    slug = models.SlugField("URL (slug)", unique=True)
    
    # Поле выбора категории. Используем наши CATEGORY_CHOICES.
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES, default='CLUB')
    description = models.TextField("Описание")
    
    # Фотография. blank=True, null=True разрешает создать кружок, даже если фото еще не сделали.
    image = models.ImageField("Обложка", upload_to='activities/', blank=True, null=True)
    
    # Порядок вывода на сайте (кто выше, кто ниже). Начинаем с 1.
    order = models.PositiveIntegerField("Сортировка", default=1)
    
    price = models.IntegerField("Цена абонемента", default=0)

    # Переключатель (вкл/выкл), если уберет галочку, кружок пропадет с сайта,но в базе вся история останется.
    is_active = models.BooleanField("Активен на сайте", default=True)

    is_featured = models.BooleanField("Вывести на главную страницу", default=False)

    class Meta:
        verbose_name = "Направление (Кружок/Услуга)"
        verbose_name_plural = "Направления (Кружки и Услуги)"
        # Автоматическая сортировка в админке по нашему полю order
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class WeeklySlot(models.Model):
    DAYS = [
        (0, 'Понедельник'), (1, 'Вторник'), (2, 'Среда'), 
        (3, 'Четверг'), (4, 'Пятница'), (5, 'Суббота'), (6, 'Воскресенье')
    ]
    
    # Привязка к направлению. Если удалить кружок, удалится и его расписание.
    activity = models.ForeignKey(
        Activity, 
        on_delete=models.CASCADE, 
        related_name='slots', # Чтобы можно было сделать activity.slots.all()
        verbose_name="Направление"
    )
    
    # Привязка к учителю. Если учитель удалится, 
    # слот расписания останется, просто поле "Учитель" станет пустым.
    teacher = models.ForeignKey(
        TeacherProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Учитель"
    )
    
    day_of_week = models.IntegerField("День недели", choices=DAYS)
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Конец")
    
    # подгруппы
    group_name = models.CharField("Название группы", max_length=50, blank=True)
    
    # Лимит мест в группе. Защита от переполнения.
    max_capacity = models.PositiveIntegerField("Колличество мест", default=10)

    class Meta:
        verbose_name = "Слот расписания"
        verbose_name_plural = "Расписание"
        # Добавим сортировку, чтобы в админке слоты шли по порядку дней и времени
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        # get_day_of_week_display() превратит цифру 0 в слово "Понедельник"
        # strftime('%H:%M') отформатирует время, убрав лишние секунды (15:00 вместо 15:00:00)
        day = self.get_day_of_week_display()
        time = self.start_time.strftime('%H:%M')
        return f"{self.activity.name} — {day} в {time}"

class ScheduleException(models.Model):
    TYPE_CHOICES = [
        ('CANCELLATION', 'Отмена'), 
        ('RESCHEDULE', 'Перенос')
    ]
    
    # CASCADE: если навсегда удалить этот урок из расписания, история его отмен тоже очистится.
    slot = models.ForeignKey(
        WeeklySlot, 
        on_delete=models.CASCADE, 
        related_name='exceptions',
        verbose_name="Слот расписания"
    )
    
    # Дата, когда произошло изменение. 
    # db_index=True критичен, так как мы постоянно будем искать отмены по конкретной дате.
    date = models.DateField("Дата исключения", db_index=True)
    type = models.CharField("Тип изменения", max_length=20, choices=TYPE_CHOICES)
    
    # Это поле заполняется ТОЛЬКО если type == 'RESCHEDULE'.
    # Если это просто 'Отмена', поле останется пустым (null=True, blank=True).
    new_start_time = models.TimeField("Новое время (если перенос)", null=True, blank=True)

    class Meta:
        verbose_name = "Исключение из расписания (Отмена/Перенос)"
        verbose_name_plural = "Исключения из расписания"
        # Сначала показываем самые свежие изменения
        ordering = ['-date']

    def __str__(self):
        # Если это перенос, добавим в название новое время
        if self.type == 'RESCHEDULE':
            return f"Перенос: {self.slot.activity.name} ({self.date}) на {self.new_start_time.strftime('%H:%M')}"
        return f"Отмена: {self.slot.activity.name} ({self.date})"

#  ЖУРНАЛ И ЗАПИСЬ 

class Enrollment(models.Model):
    # Привязка к ребенку
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='enrollments', 
        verbose_name="Ученик"
    )
    
    # Привязка к расписанию
    slot = models.ForeignKey(
        WeeklySlot, 
        on_delete=models.CASCADE, 
        related_name='enrollments', 
        verbose_name="Слот расписания"
    )
    
    # Когда ребенка добавили в группу. timezone.now подставит текущую дату автоматически.
    date_enrolled = models.DateField("Дата записи", default=timezone.now)
    
    # Если ребенок перестал ходить, мы не удаляем запись (чтобы сохранить историю), 
    # а просто снимаем галочку "Активна". Освобождается место в группе.
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Запись в группу"
        verbose_name_plural = "Записи в группы"
        # ЗАЩИТА: База выдаст ошибку, если мы попытаемся дважды записать Сашу Иванова в одну и ту же группу.
        unique_together = ('student', 'slot')

    def __str__(self):
        # Покажет в админке: "Иванов Саша -> Английский — Понедельник в 15:00"
        return f"{self.student.full_name} -> {self.slot}"


class Attendance(models.Model):
    # Статусы посещения. Влияют на списание занятий с абонемента.
    STATUS_CHOICES = [
        ('PRESENT', 'Был (Списание)'), 
        ('ABSENT', 'Не был (Списание)'), 
        ('EXCUSED', 'Болел (Без списания)')
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='attendance_records', 
        verbose_name="Ученик"
    )
    
    # SET_NULL - если удалить урок из расписания, то не удалиться 
    # историю того, что ребенок туда ходил (это нужно для финансов).
    slot = models.ForeignKey(
        WeeklySlot, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Урок"
    )

    date = models.DateField("Дата занятия", default=timezone.now, db_index=True)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default='PRESENT')

    class Meta:
        verbose_name = "Отметка посещаемости"
        verbose_name_plural = "Журнал"
        # ЗАЩИТА ОТ ДУБЛЕЙ: Нельзя поставить Саше Иванову две разные отметки 
        # за один и тот же урок в одну и ту же дату.
        unique_together = ('student', 'slot', 'date')

    def __str__(self):
        return f"{self.student.full_name} - {self.date} ({self.get_status_display()})"

#  ФИНАНСЫ (ТАРИФЫ И АБОНЕМЕНТЫ) 

class SubscriptionPlan(models.Model):
    name = models.CharField("Название тарифа", max_length=100)
    
    # DecimalField - специальный тип для ДЕНЕГ. 
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    # Сколько уроков входит в этот тариф (например: 4, 8, 12).
    sessions_count = models.PositiveIntegerField("Количество занятий")
    # Привязка тарифа к конкретному направлению. 
    # blank=True, null=True: если оставить пустым, тариф будет считаться "Общим" для всех кружков.
    activity = models.ForeignKey(
        Activity, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Привязка к кружку"
    )

    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        ordering = ['activity', 'price'] # Группируем по кружкам и цене

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"


class Subscription(models.Model):
    # Кто купил абонемент. CASCADE: удалили ребенка - удалились его абонементы.
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name="Ученик"
    )
    # Если попытаемся удалить тариф "8 занятий", а у ученика он сейчас активен, 
    # база данных ВЫДАСТ ОШИБКУ и не даст этого сделать. 
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.PROTECT,
        verbose_name="Тариф"
    )
    
    # Срок действия абонемента.
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    # Текущий остаток занятий. Будет уменьшаться, когда учитель отмечает присутствие в журнале.
    remaining_sessions = models.PositiveIntegerField("Осталось занятий")
    # Галочка активности (чтобы в админке легко фильтровать "Активные" и "Завершенные").
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Абонемент ученика"
        verbose_name_plural = "Абонементы учеников"
        
        #  Баланс никогда не уйдет в минус
        constraints = [
            CheckConstraint(
                condition=Q(remaining_sessions__gte=0), 
                name='positive_remaining_sessions'
            )
        ]

    def __str__(self):
        # Покажет: "Иванов Саша - Английский (Осталось: 3)"
        return f"{self.student.full_name} - {self.plan.name} (Остаток: {self.remaining_sessions})"

#  ФИНАНСЫ (ТРАНЗАКЦИИ / ЗАЯВКИ С САЙТА) 

class Transaction(models.Model):
    comment = models.TextField("Комментарий (и откуда узнали)", blank=True, null=True)
    STATUS_CHOICES = [
        ('PENDING', 'Ожидает оплаты'), 
        ('CONFIRMED', 'Оплачен (Подтвержден)'), 
        ('REJECTED', 'Отклонен / Ошибка'),
    ]
    
    # on_delete=models.SET_NULL: Если карточку родителя удалят, транзакция не удалится.
    # Поле parent просто станет пустым (null), чтобы не ломать финансовую статистику.
    parent = models.ForeignKey(
        'Parent', # Название модели в кавычках, чтобы вызвать ниже в коде
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Родитель"
    )
    
    student = models.ForeignKey(
        'Student', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Ученик"
    )
    
    plan = models.ForeignKey(
        'SubscriptionPlan', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Тариф"
    )
    
    amount = models.DecimalField("Сумма", max_digits=8, decimal_places=2)
    
    # auto_now_add=True заставит Джанго автоматически записать точные дату и время, когда заявка упала с сайта.
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        verbose_name = "Заявка на оплату"
        verbose_name_plural = "Заявки на оплату"
        # Сортировка по убыванию времени: новые заявки будут сверху списка
        ordering = ['-created_at'] 

    def __str__(self):
        # Если родителя удалили (parent = None), чтобы сервер не упал с ошибкой, пишем "Удаленный клиент"
        parent_name = self.parent.full_name if self.parent else "Удаленный клиент"
        return f"Заявка #{self.id} - {parent_name} ({self.get_status_display()})"
    
    # АФИША (Разовые мероприятия) 
class Event(models.Model):
    title = models.CharField("Название события", max_length=150)
    date_time = models.DateTimeField("Дата и время начала")
    price = models.IntegerField("Цена билета", default=0)
    image = models.ImageField("Обложка", upload_to='events/')
    description = models.TextField("Описание", blank=True)
    is_active = models.BooleanField("Показывать на сайте", default=True)

    class Meta:
        verbose_name = "Событие (Афиша)"
        verbose_name_plural = "Афиша (События)"
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.title} - {self.date_time.strftime('%d.%m.%Y %H:%M')}"
    
class GalleryPhoto(models.Model):
    image = models.ImageField("Фотография", upload_to='gallery/')
    alt = models.CharField("Описание", max_length=255, blank=True, help_text="Текст для слепых и SEO")
    
    class Meta:
        verbose_name = "Фото галереи"
        verbose_name_plural = "Галерея"

    def __str__(self):
        return f"Фото {self.id} - {self.alt[:20]}"

