from django.contrib import admin
from .models import CustomUser, Product, Quiz, Question, Answer, QuizResult,Profile
 
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 5
 
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
 
# class QuizAdmin(admin.ModelAdmin):
#     filter_horizontal = ('users',)
 
 
admin.site.register(Profile)
admin.site.register(Quiz)
# admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
# admin.site.register(Answer)
admin.site.register(QuizResult)
admin.site.register(Product)

#



admin.site.register(CustomUser)

