"""Application routes; existing quiz names and paths are preserved."""
from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$',views.login,name='login'),
    url(r'^primary-school', views.start_game, {"level": "1"}, name='primary-school'),  # Static Primary School
    url(r'^secondary-school', views.start_game, {"level": "2"}, name='secondary-school'),  # Static Secondary School
    url(r'^college', views.start_game, {"level": "3"}, name='college'),  # Static College
    url(r'^expert', views.start_game, {"level": "4"}, name='expert'),  # Static Expert

    url(r'^dynamic-primary-school', views.start_dynamic_game, {"level": "easy"}, name='dynamic-primary-school'),  # Dynamic Primary School
    url(r'^dynamic-secondary-school', views.start_dynamic_game, {"level": "medium"}, name='dynamic-secondary-school'),  # Dynamic Secondary School
    url(r'^dynamic-college', views.start_dynamic_game, {"level": "hard"}, name='dynamic-college'),  # Dynamic College
    url(r'^dynamic-expert', views.start_dynamic_game, {"level": "expert"}, name='dynamic-expert'),  # Dynamic Expert

    url(r'^save-results/$', views.save_results, name='save_results'),
    url(r'^get-results/$', views.get_results, name='get_results'),
    url(r'^ai-feedback/$', views.ai_feedback, name='ai_feedback'),
    url(r'^ai-feedback/(?P<session_id>[0-9]+)/$',views.ai_game_feedback,name="ai_game_feedback"),
    url(r'^get-question-queue/$',views.get_question_queue,name="get_question_queue"),
    url(r'^get-new-questions/$',views.get_new_questions,name="get_new_questions"),
    url(r'^topics/$', views.topics, name='topics'),
    url(r'^add-topic/', views.add_topic, name="add_topic"),
    url(r'^save-topics/$', views.save_topics, name='save_topics'),
    url(r'logout/', views.logout, name="logout"),

    url(r'', views.index, name='start-page'),
    ]