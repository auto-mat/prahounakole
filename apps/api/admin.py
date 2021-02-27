from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Scopes, ScopesDefinition

# Register your models here.


class ScopesDefinitionAdminInline(admin.TabularInline):
    model = Scopes.scopes.through


class GroupAdminInline(admin.TabularInline):
    model = Scopes.group.through


@admin.register(Scopes)
class ScopesAdmin(admin.ModelAdmin):
    list_display = ('get_scopes', 'description')
    exclude = ('group', 'scopes')
    inlines = (GroupAdminInline, ScopesDefinitionAdminInline,)

    def get_scopes(self, obj):
        return ' '.join(
            list(
                obj.scopes.all().values_list('scope', flat=True),
            ),
        )


@admin.register(ScopesDefinition)
class ScopesDefinitionAdmin(admin.ModelAdmin):
    list_display = ('scope', 'description')
