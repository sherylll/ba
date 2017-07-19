# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import LED

# Register your models here.

#customize name...
admin.site.register(LED)


# @admin.register(LED)
# class PersonAdmin(admin.ModelAdmin):
     # list_display = ('name', 'users')
     
