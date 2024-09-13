from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from .models import User, UserWebsite, VerificationCode, UserWebsiteLogin, University, EducationalInstitute, School, SchoolStudentship, AcademicStudentship


@admin.register(UserWebsite)
class UserWebsiteAdmin(admin.ModelAdmin):
    model = UserWebsite
    list_display = ['user', 'website']
    list_filter = ['website']
    search_fields = ['user__username', 'website']


@admin.register(UserWebsiteLogin)
class UserWebsiteLoginsCustomAdmin(admin.ModelAdmin):
    list_display = ['user_website', 'datetime']
    list_filter = ['user_website__website']
    search_fields = ['user_website__user', 'user_website__website']


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    def verify_school_documents(self, request, queryset):
        # documents = queryset.exclude(
        #     Q(school_studentship__document__isnull=True) | Q(school_studentship__document__exact='')
        # ).values_list('school_studentship', flat=True)

        documents = queryset.values_list('school_studentship', flat=True)

        updated = SchoolStudentship.objects.filter(
            pk__in=documents).update(is_document_verified=True)
        self.message_user(
            request, f'{updated} document verified.', messages.SUCCESS)

    def school(self, obj):
        return obj.school_studentship.school

    model = User
    list_display = ['id', 'username', 'phone_number', 'national_code', 'first_name', 'last_name', 'gender', 'province',
                    'city', 'school']
    search_fields = ['id', 'username', 'phone_number',
                     'national_code', 'first_name', 'last_name']
    actions = [verify_school_documents]
    ordering = ['-date_joined']


@admin.register(School)
class CustomSchoolAdmin(admin.ModelAdmin):
    def merge_schools(self, request, queryset):
        schools = len(queryset)
        first = queryset.first()
        for school in queryset.exclude(id=first.id):
            for fsm in school.fsms.all():
                fsm.save()
            for program in school.programs.all():
                program.save()
            for studentship in school.students.all():
                studentship.school = first
                studentship.save()
            school.delete()

        self.message_user(
            request, f'{schools} schools merged.', messages.SUCCESS)

    model = School
    list_display = ['id', 'name', 'province', 'city',
                    'school_type', 'postal_code', 'address']
    actions = [merge_schools]
    search_fields = ['name', 'address']


@admin.register(University)
class UniversityCustomAdmin(admin.ModelAdmin):
    model = University
    list_display = ['id', 'name', 'province', 'city', 'postal_code', 'address']
    search_fields = ['name', 'city']


admin.site.register(EducationalInstitute)
admin.site.register(VerificationCode)
admin.site.register(SchoolStudentship)
admin.site.register(AcademicStudentship)


def export_selected_objects(model_admin, request, queryset):
    selected = queryset.values_list('pk', flat=True)
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect(
        f'/api/admin/export/?ct={ct.pk}&ids={",".join(str(pk) for pk in selected)}&name={ct.model}')


admin.site.add_action(export_selected_objects, 'export_selected')
