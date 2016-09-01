from django.contrib import admin

from models import SNSToken


class SNSTokenAdmin(admin.ModelAdmin):
    list_filter = ['platform']
    list_display = ('user', 'arn', 'registration_id', 'platform', 'created')
    raw_id_fields = ['user']


admin.site.register(SNSToken, SNSTokenAdmin)
