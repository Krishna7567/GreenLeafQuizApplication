from django.urls import include, path
from .views import delete_question, delete_question1, delete_quiz, delete_quiz1, edit_question
from .views import home, leaderboard, profile, RegisterView, quiz_list1, staff_signup
from users import views
 
 
urlpatterns = [
    path('', views.home, name='home'),
    path('staff/signup/', staff_signup, name='staff_signup'),
    path('quiz1/', quiz_list1, name='quiz_list1'),
    path('quiz/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz, name='quiz'),
    path('results/<int:quiz_id>/', views.results, name='results'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('add-quiz/', views.add_quiz, name='add-quiz'),
    path('add-quiz1/', views.add_quiz1, name='add-quiz1'),
    path('add-question/<int:quiz_id>/', views.add_question, name='add-question'),
    path('add-answer/<int:question_id>/', views.add_answer, name='add-answer'),
    path('add-answer1/<int:question_id>/', views.add_answer1, name='add-answer1'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('delete_quiz/', delete_quiz, name='delete_quiz'),
    path('delete_quiz1/', delete_quiz1, name='delete_quiz1'),
    path('delete_quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('delete_quiz1/<int:quiz_id>/', views.delete_quiz1, name='delete_quiz1'),
    path('quiz/<int:quiz_id>/<int:question_id>/', delete_question, name='delete_question'),
    path('quiz1/<int:quiz_id>/<int:question_id>/', delete_question1, name='delete_question1'),
    path('edit_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('question/<int:pk>/edit/', edit_question, name='edit_question'),
    path('contact_us/', views.contact, name='contact'),
    path('about/', views.aboutpage, name='about'),

    path('products/', views.product_list_view, name='products'),
    path('products/add/', views.add_product_view, name='add_product'),
 
    # testing
    path('about1/', views.aboutpage1, name='about1'),
]