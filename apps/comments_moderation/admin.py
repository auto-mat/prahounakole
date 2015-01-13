from django.contrib.comments.moderation import CommentModerator, moderator
from cyklomapa.models import Poi
from comments_moderation.models import EmailFilter
from django.contrib import admin

class PoiModerator(CommentModerator):
    def moderate(self, comment, content_object, request):
        if EmailFilter.objects.filter(email = comment.user_email, active = True).count() > 0:
            return True
        email_filter = EmailFilter(email = comment.user_email, active = False)
        email_filter.save()
        return False

class BlacklistAdmin(admin.ModelAdmin):
    list_display = ('email', 'active')

admin.site.register(EmailFilter, BlacklistAdmin)
moderator.register(Poi, PoiModerator)
