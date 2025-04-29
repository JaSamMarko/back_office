from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords


User = get_user_model()


class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee"
    )

    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True)
    personal_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True
    )

    # Benefits
    childcare_support = models.BooleanField(default=False)
    company_car = models.BooleanField(default=False)
    gym_membership = models.BooleanField(default=False)
    health_insurance = models.BooleanField(default=False)
    mobile_phone_included = models.BooleanField(default=False)
    remote_work_option = models.BooleanField(default=False)
    stock_options = models.BooleanField(default=False)
    vacation_days = models.IntegerField(default=24)
    additional_vacation_days = models.IntegerField(default=0)

    KPI_CHOICES = [(i, str(i)) for i in range(1, 6)]
    kpi = models.IntegerField(choices=KPI_CHOICES, null=True, blank=True)

    # Contact Information
    city = models.CharField(max_length=50, blank=True)
    current_address = models.CharField(max_length=100, blank=True)
    work_mail = models.EmailField(blank=True)
    private_email = models.EmailField(blank=True)
    permanent_address = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    EDUCATION_CHOICES = [
        ("OŠ", "Osnovna škola"),
        ("SSS", "Srednja stručna sprema"),
        ("VŠS", "Viša stručna sprema"),
        ("VSS", "Visoka stručna sprema"),
        ("BA", "Bachelor"),
        ("MA", "Magisterij humanističkih znanosti"),
        ("MSc", "Magisterij prirodnih znanosti"),
        ("PhD", "Doktorat"),
    ]
    education = models.CharField(
        max_length=3,
        choices=EDUCATION_CHOICES,
        default="VSS",
    )

    # Employment Details
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    permanent = models.BooleanField(default=False)
    position = models.CharField(max_length=50, blank=True)
    safety_training_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    work_safety_certificate = models.BooleanField(default=False)

    mentor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentees'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def total_vacation_days(self):
        return self.vacation_days + self.additional_vacation_days

    @property
    def used_absence_days(self):
        absences = self.absences.filter(approved=True)
        total = sum(
            (absence.end_date - absence.start_date).days + 1
            for absence in absences
        )
        return total

    class Meta:
        ordering = ['last_name', 'first_name']


class AbsenceRecord(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='absences'
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    ABSENCE_TYPE_CHOICES = [
        ('BLOOD_DONOR', 'Odsutnost zbog darivanja krvi'),
        ('BEREAVEMENT', 'Odsutnost zbog smrti člana obitelji'),
        ('FATHER_LEAVE', 'Očinski dopust'),
        ('PARENTAL_LEAVE', 'Roditeljski dopust'),
        ('PERSONAL', 'Osobni dan'),
        ('SICK', 'Bolovanje'),
        ('VAC', 'Godišnji odmor'),
        ('WEDDING', 'Osobno vjenčanje'),
        ('RELOCATION', 'Odsustvo zbog selidbe'),
    ]
    absence_type = models.CharField(
        max_length=50,
        choices=ABSENCE_TYPE_CHOICES
    )

    approved = models.BooleanField(default=False)
    reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date.')

    def __str__(self):
        return (
            f"{self.employee} - {self.get_absence_type_display()} "
            f"({self.start_date} - {self.end_date})"
        )