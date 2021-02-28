from django.contrib.auth.models import Group

from oauth2_provider.scopes import SettingsScopes

from api.models import Scopes


class CustomSettingsScopes(SettingsScopes):

    def _get_scopes(self, request):
        groups = request.user.groups.filter(
            name__in=Group.objects.all().values_list(
                'name', flat=True,
            ),
        )
        if groups.exists():
            return list(set(
                Scopes.objects.filter(group__in=groups).
                values_list('scopes__scope', flat=True)
            ))
        return []

    def get_available_scopes(
            self, application=None, request=None, *args, **kwargs,
    ):
        return self._get_scopes(request=request)


    def get_default_scopes(
            self, application=None, request=None, *args, **kwargs,
    ):
        return self._get_scopes(request=request)
