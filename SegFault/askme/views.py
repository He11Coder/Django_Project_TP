from .models import Profile, Question, Answer, Tag
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.core.paginator import Paginator


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

def index(request):
    questions_to_view = Question.objects.newest(LAST_QUESTIONS)

    pairs = makeQuestion_amountOfAnswersList(questions_to_view)

    context = {'p': pagination(pairs, request, PAGINATE_BY)}
    return render(request, 'index.html', context)


def question(request, question_id):
    if (question_id == 0 or question_id > Question.objects.newest(THE_LATEST_QUESTION)[0].id):
        return HttpResponseNotFound("Error 404: Not Found")

    question_to_view = Question.objects.get(pk = question_id)
    answers_to_view = Answer.objects.find_by_question_id(question_id).order_by("-is_correct", "-rating")

    context = {
        'question': question_to_view,
        'p': pagination(answers_to_view, request, PAGINATE_BY)
    }
    return render(request, 'question.html', context)


def ask(request):
    return render(request, 'ask.html')


def registration(request):
    return render(request, 'signup.html')


def login(request):
    return render(request, 'login.html')


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


def hot(request):
    questions_to_view = Question.objects.best(TOP_QUESTIONS)

    pairs = makeQuestion_amountOfAnswersList(questions_to_view)

    context = {'p': pagination(pairs, request, PAGINATE_BY)}
    return render(request, 'hot.html', context)


def settings(request):
    return render(request, 'settings.html')
