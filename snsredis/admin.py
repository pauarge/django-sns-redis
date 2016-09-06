from django.contrib import admin

from .models import SNSToken


class SNSTokenAdmin(admin.ModelAdmin):
    list_filter = ['platform']
    list_display = ('user', 'platform', 'created')
    search_fields = ['user__username']
    raw_id_fields = ['user']


admin.site.register(SNSToken, SNSTokenAdmin)
