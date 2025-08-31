from django.contrib import admin
from .models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)} #this help to atuo write slug what written in category
    list_display = ('category_name', 'slug')



admin.site.register(Category, CategoryAdmin)