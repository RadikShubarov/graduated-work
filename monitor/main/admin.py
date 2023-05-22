from django.contrib import admin
from .models import Host, SarData, PcaPeaks

# Register your models here.
admin.site.register(Host)
admin.site.register(SarData)
admin.site.register(PcaPeaks)
