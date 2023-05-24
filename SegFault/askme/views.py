from .forms import LoginForm, RegistrationForm, ProfileEditForm, AskForm, AnswerForm
from .models import Profile, Question, Answer, Tag, User, QuestionLikes, AnswerLikes
from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django import forms


PAGINATE_BY = 4
LAST_QUESTIONS = 3
TOP_QUESTIONS = 2
THE_LATEST_QUESTION = 1


def pagination(object_list, request, per_page = 10):
    paginator = Paginator(object_list, per_page)

    page_number = request.GET.get('p', 1)
    page_obj = paginator.get_page(page_number)
    return page_obj

def makeQuestion_amountOfAnswersList(questions_to_view):
    ids = []
    for question in questions_to_view:
        ids.append(question.id)
    amount_of_ans = Question.objects.count_answers(ids)

    curr_result = {}
    for question, amount in zip(questions_to_view, amount_of_ans):
        curr_result[question] = amount
    
    pairs = [(k, curr_result[k]) for k in curr_result.keys()]

    return pairs

@require_GET
def index(request):
    questions_to_view = Question.objects.newest(LAST_QUESTIONS)

    pairs = makeQuestion_amountOfAnswersList(questions_to_view)

    context = {'p': pagination(pairs, request, PAGINATE_BY)}
    return render(request, 'index.html', context)


@require_http_methods(['GET', 'POST'])
def question(request, question_id):
    if (question_id == 0 or question_id > Question.objects.newest(THE_LATEST_QUESTION)[0].id):
        return HttpResponseNotFound("Error 404: Not Found")

    question_to_view = Question.objects.get(pk = question_id)

    if request.method == 'GET':
        answers_to_view = Answer.objects.find_by_question_id(question_id).order_by("-is_correct", "-rating", "created")
        answer_form = AnswerForm()
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer_form.save(username = request.user, question_id = question_id)

            answers_to_view = Answer.objects.find_by_question_id(question_id).order_by("-is_correct", "-rating", "created")
            page_with_curr_answer = Paginator(answers_to_view, PAGINATE_BY).num_pages
            return redirect(reverse('question', args = [question_id]) + f'?p={page_with_curr_answer}')

    context = {
        'question': question_to_view,
        'p': pagination(answers_to_view, request, PAGINATE_BY),
        'form' : answer_form
    }
    return render(request, 'question.html', context)


@require_http_methods(['GET', 'POST'])
@login_required(login_url = '/login/')
def ask(request):
    if request.method == 'GET':
        ask_form = AskForm()
    elif request.method == 'POST':
        ask_form = AskForm(request.POST)
        if ask_form.is_valid():
            question_id = ask_form.save(request)
            return redirect(reverse('question', args = [question_id]))

    return render(request, 'ask.html', context = {'form' : ask_form})


@require_http_methods(['GET', 'POST'])
def registration(request):
    if request.method == 'GET':
        user_form = RegistrationForm()
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            nickname = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']

            auth_user = authenticate(username = nickname, password = password)
            login(user = auth_user, request = request)
            return redirect(reverse('index'))

    return render(request, 'signup.html', context = {'form' : user_form})


@require_http_methods(['GET', 'POST'])
def log_in(request):
    if request.method == 'GET':
        login_form = LoginForm()

    elif request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            if user:
                login(request, user)
                next_url = request.GET.get('next')

                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(reverse('index'))
                
            login_form.add_error(None, "Invalid username or password!")

    return render(request, 'login.html', context = {'form' : login_form})


@require_GET
def tag(request, tag_name):
    questions_to_view = Question.objects.find_by_tag(tag_name)

    if (not questions_to_view):
        return HttpResponseNotFound("Error 404: Not Found")

    pairs = makeQuestion_amountOfAnswersList(questions_to_view)

    context = {
        'p': pagination(pairs, request, PAGINATE_BY),
        'tag_text' : tag_name
    }
    return render(request, 'tag.html', context)


@require_GET
def hot(request):
    questions_to_view = Question.objects.best(TOP_QUESTIONS)

    pairs = makeQuestion_amountOfAnswersList(questions_to_view)

    context = {'p': pagination(pairs, request, PAGINATE_BY)}
    return render(request, 'hot.html', context)


@require_http_methods(['GET', 'POST'])
@login_required(login_url='/login/')
def settings(request):
    if request.method == 'GET':
        settings_form = ProfileEditForm()
    elif request.method == 'POST':
        settings_form = ProfileEditForm(request.POST, files=request.FILES)
        if settings_form.is_valid():
            password = settings_form.cleaned_data['old_password']
            if (not User.objects.get(username = request.user).check_password(password)):
                settings_form.add_error(field = None, error = 'Incorrect current password')
            else:
                settings_form.save(request)
                return redirect(reverse('settings'))
        
    return render(request, 'settings.html', context = {'form' : settings_form})


@require_GET
@login_required(login_url='/login/', redirect_field_name = 'continue')
def log_out(request):
    logout(request)

    if request.GET.get('continue'):
        return redirect(request.GET.get('continue'))

    return redirect('index')


@login_required(login_url='/login/')
@require_POST
def vote_up(request):
    question_id = request.POST['question_id']
    
    question = Question.objects.get(id = question_id)
    
    if (not QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile).exists()):
        question.rating += 1

        like = QuestionLikes.objects.create(question_id = question, author_id = request.user.profile, value = True)
        like.save()
    elif (QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = True).exists()):
        question.rating -= 1

        QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile).delete()
    elif (QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = False).exists()):
        question.rating += 2

        QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = False).delete()
        like = QuestionLikes.objects.create(question_id = question, author_id = request.user.profile, value = True)
        like.save()

    question.save()

    return JsonResponse({
        'new_rating' : question.rating
    })


@login_required(login_url='/login/')
@require_POST
def vote_down(request):
    question_id = request.POST['question_id']
    
    question = Question.objects.get(id = question_id)
    
    if (not QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile).exists()):
        question.rating -= 1

        dislike = QuestionLikes.objects.create(question_id = question, author_id = request.user.profile, value = False)
        dislike.save()
    elif (QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = False).exists()):
        question.rating += 1

        QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = False).delete()
    elif (QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = True).exists()):
        question.rating -= 2

        QuestionLikes.objects.filter(question_id = question, author_id = request.user.profile, value = True).delete()
        dislike = QuestionLikes.objects.create(question_id = question, author_id = request.user.profile, value = False)
        dislike.save()
        
    question.save()

    return JsonResponse({
        'new_rating' : question.rating
    })


@login_required(login_url='/login/')
@require_POST
def set_correct(request):
    answer_id = request.POST['answer_id']

    answer = Answer.objects.get(id = answer_id)

    requester = request.user.profile
    question_author = answer.question_id.author_id

    if (requester == question_author):
        answer.is_correct = not answer.is_correct
        answer.save()

    return JsonResponse({
        'answer_status': answer.is_correct
    })


@login_required(login_url='/login/')
@require_POST
def vote_answer_up(request):
    answer_id = request.POST['answer_id']
    print(answer_id)
    answer = Answer.objects.get(id = answer_id)
    
    if (not AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile).exists()):
        answer.rating += 1

        like = AnswerLikes.objects.create(answer_id = answer, author_id = request.user.profile, value = True)
        like.save()
    elif (AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = True).exists()):
        answer.rating -= 1

        AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile).delete()
    elif (AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = False).exists()):
        answer.rating += 2

        AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = False).delete()
        like = AnswerLikes.objects.create(answer_id = answer, author_id = request.user.profile, value = True)
        like.save()

    answer.save()

    return JsonResponse({
        'new_rating' : answer.rating
    })  


@login_required(login_url='/login/')
@require_POST
def vote_answer_down(request):
    answer_id = request.POST['answer_id']
    
    answer = Answer.objects.get(id = answer_id)
    
    if (not AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile).exists()):
        answer.rating -= 1

        dislike = AnswerLikes.objects.create(answer_id = answer, author_id = request.user.profile, value = False)
        dislike.save()
    elif (AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = False).exists()):
        answer.rating += 1

        AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = False).delete()
    elif (AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = True).exists()):
        answer.rating -= 2

        AnswerLikes.objects.filter(answer_id = answer, author_id = request.user.profile, value = True).delete()
        dislike = AnswerLikes.objects.create(answer_id = answer, author_id = request.user.profile, value = False)
        dislike.save()
        
    answer.save()

    return JsonResponse({
        'new_rating' : answer.rating
    })