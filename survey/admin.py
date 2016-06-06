# -- encoding=utf-8 --
from django.contrib import admin
from django.contrib.auth.models import User

from models import QuestionQA

class QuestionQAAdmin(admin.ModelAdmin):
    list_display = ('question','q_en','q_desc','q_desc_en','q_addon','q_addon_en','a_desc','a_desc_en',)
    fieldsets = (
        (None, {'fields': ( 'question','q_en','q_desc','q_desc_en','q_addon','q_addon_en','a_desc','a_desc_en',)}),
    )
    
    ordering = ['id',]
    #def save_model(self, request, obj, form, change):
    #    obj.user = request.user
    #    obj.save()

admin.site.register(QuestionQA, QuestionQAAdmin)
