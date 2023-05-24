from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from askme import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('admin/', admin.site.urls),
    path('question/<int:question_id>/', views.question, name = "question"),
    path('ask/', views.ask, name = "ask"),
    path('registration/', views.registration, name = "signup"),
    path('login/', views.log_in, name = "login"),
    path('tag/<str:tag_name>/', views.tag, name = "tag"),
    path('hot/', views.hot, name = "hot"),
    path('settings/', views.settings, name = "settings"),
    path('logout', views.log_out, name = "logout"),
    path('vote_up/', views.vote_up, name = "vote_up"),
    path('vote_down/', views.vote_down, name = "vote_down"),
    path('vote_answer_up/', views.vote_answer_up, name = "vote_answer_up"),
    path('vote_answer_down/', views.vote_answer_down, name = "vote_answer_down"),
    path('set_correct/', views.set_correct, name = "set_correct")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)