from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import *

class PersonneAdmin(admin.ModelAdmin):
    search_fields= ('email', 'nom', 'prenom', 'telephone', 'role', 'image', 'is_verified', 'is_active', 'is_staff', 'banni')
    list_display= ('email', 'nom', 'prenom', 'role')
    form = UpdateUserForm

    fieldsets = (
        (None, {
            'fields': ('email', 'nom', 'prenom', 'telephone', 'role', 'is_verified', 'is_active', 'is_staff', 'banni')
        }),
    )




admin.site.register(Personne, PersonneAdmin)

admin.site.register(Categorie)
admin.site.register(Ouvrage)
admin.site.register(Exemplaire)
admin.site.register(Emprunter)
admin.site.register(Reservation)
admin.site.register(Gerer)
admin.site.register(Notification)
admin.site.register(Consulter)
admin.site.register(Signalement)
admin.site.register(CustomLogEntry)