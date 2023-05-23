from django.contrib import admin
from django.urls import path
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
    path('logout', views.log_out, name = "logout")
]