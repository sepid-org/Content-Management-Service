from django.shortcuts import render
# your_app/views.py
from django.http import HttpResponse
from django.core.serializers import serialize
from django.apps import apps
import csv


def export(request):
    app_models = apps.get_models()
    serialized_data_list = []
    for model in app_models:
        queryset = model.objects.all()
        serialized_data = serialize('json', queryset)
        serialized_data_list.append(serialized_data)

    exported_data = "[" + ",".join(serialized_data_list) + "]"

    response = HttpResponse(exported_data, content_type='application/json')

    response['Content-Disposition'] = 'attachment; filename=exported_data.json'

    return response


def export_csv(request):
    app_models = apps.get_models()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=exported_data.csv'
    csv_writer = csv.writer(response)
    for model in app_models:
        fields = [field.name for field in model._meta.fields]
        csv_writer.writerow([f"{model.__name__}_{field}" for field in fields])

    for model in app_models:
        queryset = model.objects.all()
        for row in queryset.values():
            csv_writer.writerow([row[field] for field in row])

    return response



# 1- send program id and give a excel of user that register this program
#1- done
# 2-send form

import requests

def create_session():
    url = "https://metabase.sepid.org/api/session"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": "sepid.platform@gmail.com",
        "password": "ThisIsSepidPassword4Metabase"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

session_data = create_session()
print(session_data)

import requests


def get_current_user(session_token):
    url = "https://metabase.sepid.org/api/dataset/"
    headers = {
        "Content-Type": "application/json",
        "X-Metabase-Session": session_token
    }
    data = {
            "database": 2,
            "query": {
                "source-table": 60,
                "filter": [
                    "and",
                    ["=", ["field", 448, None], True],
                    ["=", ["field", 444, None], "Accepted"],
                    ["=", ["field", 779, None], 1]
                ],
                "joins": [
                    {
                        "fields": [
                            ["field", 142, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 156, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 158, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 144, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 159, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 151, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 146, {"join-alias": "Accounts+User+-+User"}],
                            ["field", 147, {"join-alias": "Accounts+User+-+User"}]
                        ],
                        "source-table": 32,
                        "condition": ["=", ["field", 443, None],
                                      ["field", 151, {"join-alias": "Accounts+User+-+User"}]],
                        "alias": "Accounts+User+-+User"
                    }
                ]
            },
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    if response.status_code == 202:
        return response.json()
    else:
        response.raise_for_status()

session_token = session_data.get("id")
current_user = get_current_user(session_token)
print(current_user)

import requests
def export_excel(form_id):
    url = "https://metabase.sepid.org/api/dataset/json"
    headers = {
        "X-Metabase-Session": session_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    query='{"source-table":60,"filter":["and",["=",["field",448,null],true],["=",["field",444,null],"Accepted"],'+f'["=",["field",779,null],{form_id}]]'+',"joins":[{"fields":[["field",142,{"join-alias":"Accounts User - User"}],["field",156,{"join-alias":"Accounts User - User"}],["field",158,{"join-alias":"Accounts User - User"}],["field",144,{"join-alias":"Accounts User - User"}],["field",159,{"join-alias":"Accounts User - User"}],["field",151,{"join-alias":"Accounts User - User"}],["field",146,{"join-alias":"Accounts User - User"}],["field",147,{"join-alias":"Accounts User - User"}]],"source-table":32,"condition":["=",["field",443,null],["field",151,{"join-alias":"Accounts User - User"}]],"alias":"Accounts User - User"}]},"type":"query","middleware":{"js-int-to-string?":true,"add-default-userland-constraints?":true}}'
    data = {
        "query": '{"database":2,"query":'+ f'{query}'+',"type":"query","middleware":{"js-int-to-string?":true,"add-default-userland-constraints?":true}}'
    }
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        with open('output.json', 'wb') as f:
            f.write(response.content)
        print("CSV file saved successfully.")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.text)

export_excel(form_id=307)