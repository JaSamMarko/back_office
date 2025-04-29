from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Department, Employee, AbsenceRecord


class AbsenceRecordInline(admin.TabularInline):
    model = AbsenceRecord
    extra = 1
    fields = ('start_date', 'end_date', 'absence_type', 'approved', 'reason')
    readonly_fields = ('created_at',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'position', 'department', 'user',
        'mentor', 'kpi', 'vacation_days', 'used_absence_days',
        'total_vacation_days', 'created_at'
    )
    search_fields = (
        'first_name', 'last_name', 'user__username', 'user__email',
        'personal_id', 'position', 'work_mail', 'private_email'
    )
    list_filter = ('department', 'vacation_days', 'permanent')
    ordering = ('last_name', 'first_name')
    inlines = [AbsenceRecordInline]

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'first_name', 'last_name', 'middle_name', 
                'personal_id', 'date_of_birth'
            )
        }),
        ('Contact Information', {
            'fields': (
                'work_mail', 'private_email', 'phone_number', 
                'city', 'current_address', 'permanent_address'
            )
        }),
        ('Employment Details', {
            'fields': (
                'position', 'department', 'permanent',
                'start_date', 'trial_end_date', 'end_date',
                'safety_training_date', 'work_safety_certificate'
            )
        }),
        ('Mentorship and KPIs', {
            'fields': ('mentor', 'kpi')
        }),
        ('Education', {
            'fields': ('education',)
        }),
        ('Benefits', {
            'fields': (
                'health_insurance', 'company_car', 'childcare_support',
                'gym_membership', 'mobile_phone_included',
                'remote_work_option', 'stock_options'
            )
        }),
        ('Vacation', {
            'fields': ('vacation_days', 'additional_vacation_days')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(AbsenceRecord)
class AbsenceRecordAdmin(SimpleHistoryAdmin):
    list_display = (
        'employee', 'start_date', 'end_date', 
        'absence_type', 'approved', 'created_at'
    )
    list_filter = ('absence_type', 'approved', 'start_date', 'end_date')
    search_fields = (
        'employee__first_name', 'employee__last_name', 'absence_type'
    )