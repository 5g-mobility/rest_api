from django.contrib import admin

from mobility_5g_rest_api.models import Event, Climate, DailyInflow

admin.site.register(Event)
admin.site.register(Climate)
admin.site.register(DailyInflow)

