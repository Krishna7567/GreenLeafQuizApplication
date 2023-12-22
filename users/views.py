from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import ValidationError 

from .forms import ProductForm, RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm, StaffSignupForm, \
    QuizForm, QuestionForm, AnswerForm
from .models import Answer, Quiz, QuizResult, Question, QuizResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.contrib.auth.models import User


def home(request):
    return render(request, 'users/home.html')
 
 
class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'
 
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')
 
        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)
 
    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})
 
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
 
        if form.is_valid():
            form.save()
 
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            is_staff = False
            if email.endswith('@user.com'):     # creates superuser, if email ends with
                is_staff = True
            messages.success(request, f'Account created for {username}')
 
            return redirect(to='login')
 
        return render(request, self.template_name, {'form': form})
 
 
# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm
 
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
 
        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)
 
            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True
 
        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)
 
 
class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    # success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-profile')
 
 
# updates user profile
@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
 
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
 
    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})
 
 
@login_required
def quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = quiz.question_set.all()
    quiz_responses = QuizResponse.objects.filter(quiz=quiz)
    if quiz_responses:
        quiz_responses.delete()
    
    if request.user.is_staff:
        quiz_result = QuizResult.objects.filter(user=request.user,quiz_id=quiz_id).first()
        if quiz_result:
            quiz_result.delete()
    else:
        # Check if user has already taken the quiz
        quiz_result = QuizResult.objects.filter(user=request.user, quiz_id=quiz_id).first()
        if quiz_result:
            messages.error(request, 'You have already taken this quiz.')
            return redirect('results', quiz_id=quiz_id)
    
    if request.method == 'POST':
        score = 0
        quiz_responses = []

        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += question.marks
                quiz_response = QuizResponse(user=request.user, quiz=quiz, question=question, answer=selected_answer)
                quiz_responses.append(quiz_response)
            else:
                selected_answer = None
        
        if quiz_result:
            # Update existing quiz result if user is not staff
            quiz_result.score = score
            quiz_result.save()
        else:
            # Save new quiz result if user is not staff
            quiz_result = QuizResult(user=request.user, quiz=quiz, score=score)
            quiz_result.save()
        
        QuizResponse.objects.bulk_create(quiz_responses)

        # Redirect to results page
        return redirect('results', quiz_id=quiz_id)
    # Calculate the total marks for the quiz
    total_marks = sum(question.marks for question in questions)

    return render(request, 'users/quiz.html', {'quiz': quiz, 'questions': questions,'total_marks': total_marks})
 
 
@login_required
def results(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    quiz_responses = QuizResponse.objects.filter(quiz_id=quiz_id)
    quiz_results = QuizResult.objects.filter(user=request.user, quiz=quiz)
    questions = quiz.question_set.all()  # get all questions for the quiz
    # Calculate the total marks for the quiz
    total_marks = sum(question.marks for question in questions)
    # quiz_responses = QuizResponse.objects.filter(user=request.user, quiz=quiz)
    # if quiz_responses:
    #     quiz_responses.delete()
    
    return render(request, 'users/results.html', {'quiz': quiz, 'quiz_results': quiz_results, 'questions': questions, 'quiz_responses': quiz_responses,'total_marks': total_marks})
 
 
@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'users/quiz_list.html', {'quizzes': quizzes})
 
 
@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def custom_page(request):
    return render(request, 'users/custom_page.html')
 
 
@login_required
@staff_member_required
def add_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, 'Quiz added successfully')
            return redirect('add-question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'users/add_quiz.html', {'form': form})
 
 
@login_required
@staff_member_required
def add_question(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added successfully')
            return redirect('add-answer', question.id)
    else:
        form = QuestionForm()
    return render(request, 'users/add_question.html', {'form': form, 'quiz': quiz})

@login_required
@staff_member_required
def add_quiz1(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            messages.success(request, 'Quiz added successfully')
            return redirect('add-question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'users/add_quiz.html', {'form': form})
 

@login_required
@staff_member_required
def add_answer1(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        for field_name in request.POST:
            if field_name.startswith('answer'):
                answer_text = request.POST[field_name]
                answer_id = field_name.replace('answer', '')
                is_correct = 'is_correct' + answer_id in request.POST
                answer = Answer(question=question, text=answer_text, is_correct=is_correct)
                answer.save()
        messages.success(request, 'Question and Answers added successfully')
        return redirect('quiz_list1')
    else:
        form = AnswerForm()
    return render(request, 'users/add_answer.html', {'form': form, 'question': question})


@login_required
@staff_member_required
def add_answer(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        for field_name in request.POST:
            if field_name.startswith('answer'):
                answer_text = request.POST[field_name]
                answer_id = field_name.replace('answer', '')
                is_correct = 'is_correct' + answer_id in request.POST
                answer = Answer(question=question, text=answer_text, is_correct=is_correct)
                answer.save()
        messages.success(request, 'Answers added successfully')
        return redirect('quiz_list')
    else:
        form = AnswerForm()
    return render(request, 'users/add_answer.html', {'form': form, 'question': question})
 

def staff_signup(request):
    if request.method == 'POST':
        form = StaffSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home') # replace 'home' with the name of your homepage URL
    else:
        form = StaffSignupForm()
    return render(request, 'users/staff_signup.html', {'form': form})

 
def leaderboard(request,):
    user_scores = QuizResult.objects.values('user') \
        .annotate(num_questions=Count('quiz_id'), total_score=Sum('score')) \
        .order_by('-total_score')
    # QuerySet of dictionaries with user_id, num_questions and total_score fields
    # sorted in descending order by total_score
    
    # Retrieve the User objects for each user_id in the leaderboard
    users = User.objects.in_bulk([user_score['user'] for user_score in user_scores])
    
    # Create a list of dictionaries that combines the User objects and their quiz results
    leaderboard_data = []
    for user_score in user_scores:
        user = users[user_score['user']]
        leaderboard_data.append({
            'username': user.username,
            'num_questions': user_score['num_questions'],
            'total_score': user_score['total_score'],
        })
 
    context = {'leaderboard_data': leaderboard_data}
    return render(request, 'users/leaderboard.html', context)
 
 
@login_required
@staff_member_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list')
    context = {'quiz': quiz}
    return render(request, 'users/quiz.html', context)
 
 
@login_required
@staff_member_required
def delete_quiz1(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        return redirect('quiz_list1')
    context = {'quiz': quiz}
    return render(request, 'users/quiz_list1.html', context)

 
@login_required
@staff_member_required
def delete_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    if request.method == 'POST':
        question.delete()
        return redirect('quiz' ,quiz_id=quiz.id)
    return render(request, 'users/delete_question.html', {'quiz': quiz, 'question': question})
 

@login_required
@staff_member_required
def delete_question1(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    if request.method == 'POST':
        question.delete()
        return redirect('quiz_list1')
    return render(request, 'users/quiz_list1.html', {'quiz': quiz, 'question': question})
 
  
@login_required
@staff_member_required
def quiz_list1(request):
    quizzes = Quiz.objects.all()
    quiz_question_dict = {}
    for quiz in quizzes:
        questions = Question.objects.filter(quiz=quiz)
        quiz_question_dict[quiz] = questions
    return render(request, 'users/quiz_list1.html', {'quiz_question_dict': quiz_question_dict})
 
 
@login_required
@staff_member_required
def edit_quiz(request, quiz_id):
    # Retrieve the quiz object with the specified ID, or return a 404 error if it doesn't exist
    quiz = get_object_or_404(Quiz, id=quiz_id)
 
    if request.method == 'POST':
        # If the request method is POST, the user has submitted the quiz edit form
        # Retrieve the new quiz name from the submitted form data
        new_name = request.POST.get('name')
        
        # Update the quiz object with the new name
        quiz.name = new_name
        quiz.save()
 
        # Redirect to the quiz detail page
        return redirect('quiz_list1')
    else:
        # If the request method is not POST, the user is requesting the quiz edit form
        # Display the quiz edit form with the current quiz name pre-filled
        return render(request, 'users/edit_quiz.html', {'quiz': quiz})


@login_required
@staff_member_required 
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
 
    if request.method == 'POST':
        # process form data and save question
        question.text = request.POST['question_text']
        question.marks = request.POST['question_marks']
        question.save()
 
        for answer in question.answer_set.all():
            answer.text = request.POST.get(f'answer_{answer.id}')
            answer.correct = request.POST.get(f'correct_{answer.id}') == 'on'
            answer.save()
 
        return HttpResponseRedirect(reverse('quiz_list1'))
 
    return render(request, 'users/edit_question.html', {'question': question})




def aboutpage(request):
    return render(request, 'users/about.html')

# testing
def aboutpage1(request):
    return render(request, 'users/about1.html')


def contact(request):
    return render(request, 'users/contact_us.html')


from django.shortcuts import render, redirect
from .models import Product, UserPrice
from .forms import UserPriceForm

def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'users/add_product.html', {'form': form})

def product_list_view(request):
    products = Product.objects.all()
    user_prices = None
    user_price_form = None

    if request.user.is_authenticated:
        if not request.user.is_staff:
            user_price_form = UserPriceForm(request.POST or None)

            if request.method == 'POST' and user_price_form.is_valid():
                user_price = user_price_form.cleaned_data['price']
                product = user_price_form.cleaned_data['product']
                UserPrice.objects.update_or_create(user=request.user, product=product, defaults={'price': user_price})
        else:
            user_prices = UserPrice.objects.filter(user__is_staff=False, product__in=products).values_list('product_id', 'price')

    return render(request, 'users/product_list.html', {'products': products, 'user_prices': user_prices, 'user_price_form': user_price_form})
