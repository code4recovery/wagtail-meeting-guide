from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Region


admin.site.register(Region, MPTTModelAdmin)
