from django.test import TestCase, Client
# myapp/tests.py

from django.test import override_settings
from django.urls import reverse
from django.apps import apps
from django.core.serializers import serialize
from django.http import HttpResponse
from views import export
import csv

class ViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def setUp(self):
        pass

    def tearDown(self):
        pass

class ExportViewTest(ViewTestCase):
    def test_export_view(self):
        with override_settings(ROOT_URLCONF='report.urls'):
            url = reverse('export_json')
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')

            self.assertTrue(response.content)

            self.assertTrue('Content-Disposition' in response)

            self.assertTrue('attachment' in response['Content-Disposition'])
            self.assertTrue('exported_data.json' in response['Content-Disposition'])

class ExportCSVViewTest(ViewTestCase):
    def test_export_csv_view(self):
        with override_settings(ROOT_URLCONF='report.urls'):

            url = reverse('export_csv')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            self.assertEqual(response['Content-Type'], 'text/csv')

            self.assertTrue(response.content)

            self.assertTrue('Content-Disposition' in response)

            self.assertTrue('attachment' in response['Content-Disposition'])

            self.assertTrue('exported_data.csv' in response['Content-Disposition'])
            csv_data = response.content.decode('utf-8').splitlines()
            csv_reader = csv.reader(csv_data)
            header_row = next(csv_reader)
            expected_header = [f"{model.__name__}_{field.name}" for model in apps.get_models() for field in model._meta.fields]
            self.assertEqual(header_row, expected_header)
            num_rows = len(list(csv_reader))
            expected_num_rows = sum(model.objects.count() for model in apps.get_models())
            self.assertEqual(num_rows, expected_num_rows)
