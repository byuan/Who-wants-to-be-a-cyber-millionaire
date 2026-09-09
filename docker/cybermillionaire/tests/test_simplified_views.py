"""Behavioral coverage for shared views and existing public routes."""
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import test_regressions  # Configure isolated Django settings.
from django.http import HttpResponse
from django.template import Context, Engine
from django.test import RequestFactory, override_settings
from django.urls import resolve, reverse
from cybermillionaire import views

LEVELS = [('primary-school', '1', 'easy'), ('secondary-school', '2', 'medium'),
          ('college', '3', 'hard'), ('expert', '4', 'expert')]

class SharedViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_all_eight_game_urls_preserve_payload_and_csrf(self):
        questions = [{'question': 'Test?', 'content': ['A', 'B', 'C', 'D'], 'correct': 0}]
        payload = {'games': [{'questions': questions}]}
        for slug, static_level, dynamic_level in LEVELS:
            for dynamic in (False, True):
                name = ('dynamic-' if dynamic else '') + slug
                path = '/' + name
                with self.subTest(path=path):
                    self.assertEqual(reverse(name), path)
                    route = resolve(path)
                    request = self.factory.get(path)
                    request.session = {'user_id': 7}
                    with patch.object(views.e, 'export_questions', return_value=payload) as export, \
                         patch.object(views, 'generate_initial_questions', return_value=questions) as initial, \
                         patch.object(views, 'start_question_generation') as start, \
                         patch.object(views, 'render', return_value=HttpResponse()) as render:
                        response = route.func(request, **route.kwargs)
                        self.assertEqual(response.status_code, 200)
                        self.assertIn('csrftoken', response.cookies)
                        render.assert_called_once_with(request, 'game.html', {'game_data': payload})
                        if dynamic:
                            initial.assert_called_once_with(dynamic_level, 7, 5)
                            start.assert_called_once_with(dynamic_level, 7)
                            export.assert_not_called()
                        else:
                            export.assert_called_once_with(static_level)
                            initial.assert_not_called()
                            start.assert_not_called()

    def test_all_protected_routes_redirect_without_login(self):
        paths = ['/', '/topics/', '/save-topics/', '/add-topic/', '/save-results/',
                 '/get-results/', '/ai-feedback/', '/ai-feedback/1/',
                 '/get-question-queue/', '/get-new-questions/']
        paths += ['/' + prefix + slug for slug, _, _ in LEVELS for prefix in ('', 'dynamic-')]
        for path in paths:
            with self.subTest(path=path):
                route = resolve(path)
                request = self.factory.get(path)
                request.session = {}
                response = route.func(request, **route.kwargs)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response['Location'], '/login/')

    @override_settings(STATIC_URL='/static/')
    def test_topic_form_preserves_labels_names_and_selections(self):
        selected = {key: ['Passwords'] for _, _, key in LEVELS}
        request = self.factory.get('/topics/')
        request.session = {'user_id': 7, 'is_admin': False}
        with patch.object(views, 'get_topic_settings', return_value=selected), \
             patch.object(views, 'get_available_topics', return_value=['Passwords', '<Other>']), \
             patch.object(views, 'render', return_value=HttpResponse()) as render:
            views.topics(request)
        context = render.call_args.args[2]
        template = Path(__file__).parents[1] / 'templates/topics.html'
        engine = Engine(libraries={'static': 'django.templatetags.static'})
        html = engine.from_string(template.read_text()).render(Context(context))
        for _, _, key in LEVELS:
            self.assertEqual(html.count('name="' + key + '_topics"'), 2)
        self.assertEqual(html.count('checked'), 4)
        self.assertIn('&lt;Other&gt;', html)
        for label in ['Primary School', 'Secondary School', 'College', 'Expert']:
            self.assertIn('<h2>' + label + '</h2>', html)

    def test_topic_save_keeps_all_difficulty_fields(self):
        request = self.factory.post('/save-topics/', {'easy_topics': ['Passwords', 'Phishing'], 'expert_topics': ['Cryptography']})
        request.session = {'user_id': 7}
        with patch.object(views, 'save_topic_settings') as save, \
             patch.object(views, 'index', return_value=HttpResponse()):
            views.save_topics(request)
        save.assert_called_once_with(7, {'easy': ['Passwords', 'Phishing'], 'medium': [], 'hard': [], 'expert': ['Cryptography']})
