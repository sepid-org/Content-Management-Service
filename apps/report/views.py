from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.file_storage.serializers.file_serializer import FileSerializer
from proxies.metabase.main import MetabaseProxy

url = settings.METABASE_URL

Metabase_proxy = MetabaseProxy()


def get_form_respondents_info_file(form_id):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "query": '{"database":2,"type":"query","query":{"source-table":60,"filter":["=",["field",779,null],' + f'{form_id}' + '],"joins":[{"fields":[["field",142,{"join-alias":"Accounts+User+-+User"}],["field",156,{"join-alias":"Accounts+User+-+User"}],["field",158,{"join-alias":"Accounts+User+-+User"}],["field",157,{"join-alias":"Accounts+User+-+User"}],["field",144,{"join-alias":"Accounts+User+-+User"}],["field",161,{"join-alias":"Accounts+User+-+User"}],["field",150,{"join-alias":"Accounts+User+-+User"}],["field",159,{"join-alias":"Accounts+User+-+User"}],["field",146,{"join-alias":"Accounts+User+-+User"}],["field",147,{"join-alias":"Accounts+User+-+User"}],["field",163,{"join-alias":"Accounts+User+-+User"}],["field",152,{"join-alias":"Accounts+User+-+User"}],["field",154,{"join-alias":"Accounts+User+-+User"}],["field",153,{"join-alias":"Accounts+User+-+User"}],["field",162,{"join-alias":"Accounts+User+-+User"}]],"source-table":32,"condition":["=",["field",443,null],["field",151,{"join-alias":"Accounts+User+-+User"}]],"alias":"Accounts+User+-+User"}],"fields":[["field",446,null],["field",444,null],["field",448,null],["field",447,null],["field",707,null]]},"middleware":{"js-int-to-string?":true,"add-default-userland-constraints?":true}}'
    }
    response = Metabase_proxy.post(f'{url}api/dataset/xlsx', headers, data)

    if response.status_code == 200:
        in_memory_file = SimpleUploadedFile("test.xlsx", response.content)
        file = FileSerializer(data={"file": in_memory_file})
        file.is_valid(raise_exception=True)
        file.save()
        return file.data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


def get_form_respondents_answers_file(form_id):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "query": '{"database":2,"type":"query","query":{"source-table":60,"joins":[{"fields":"none","source-table":35,"condition":["=",["field",446,null],["field",271,{"join-alias":"Fsm+Answersheet+-+Answersheet+Ptr"}]],"alias":"Fsm+Answersheet+-+Answersheet+Ptr"},{"fields":"none","source-table":106,"condition":["=",["field",271,{"join-alias":"Fsm+Answersheet+-+Answersheet+Ptr"}],["field",269,{"join-alias":"Fsm+Answer"}]],"alias":"Fsm+Answer"},{"fields":"none","source-table":96,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",449,{"join-alias":"Fsm+Smallanswer"}]],"alias":"Fsm+Smallanswer"},{"fields":"none","source-table":117,"condition":["=",["field",450,{"join-alias":"Fsm+Smallanswer"}],["field",430,{"join-alias":"Fsm+Problem+-+Problem"}]],"alias":"Fsm+Problem+-+Problem"},{"fields":"none","source-table":46,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",288,{"join-alias":"Fsm+Biganswer"}]],"alias":"Fsm+Biganswer"},{"fields":"none","source-table":107,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",466,{"join-alias":"Fsm+Uploadfileanswer"}]],"alias":"Fsm+Uploadfileanswer"},{"fields":"none","source-table":9,"condition":["=",["field",263,{"join-alias":"Fsm+Answer"}],["field",371,{"join-alias":"Fsm+Multichoiceanswer+Choices"}]],"alias":"Fsm+Multichoiceanswer+Choices"},{"fields":"none","source-table":66,"condition":["=",["field",372,{"join-alias":"Fsm+Multichoiceanswer+Choices"}],["field",300,{"join-alias":"Fsm+Choice+-+Choice"}]],"alias":"Fsm+Choice+-+Choice"},{"fields":"none","source-table":32,"condition":["=",["field",443,null],["field",151,{"join-alias":"Accounts+User+-+User"}]],"alias":"Accounts+User+-+User"}],"expressions":{"ans":["concat",["field",451,{"join-alias":"Fsm+Smallanswer"}],["field",290,{"join-alias":"Fsm+Biganswer"}],["field",467,{"join-alias":"Fsm+Uploadfileanswer"}],["field",303,{"join-alias":"Fsm+Choice+-+Choice"}]],"نام+و+نام+خانوادگی":["concat",["field",142,{"join-alias":"Accounts+User+-+User"}],"+",["field",156,{"join-alias":"Accounts+User+-+User"}]],"phone":["field",144,{"join-alias":"Accounts+User+-+User"}]},"fields":[["field",446,null],["expression","ans"],["expression","نام+و+نام+خانوادگی"],["expression","phone"]],"filter":["=",["field",779,null],'+f'{form_id}' + ']},"middleware":{"js-int-to-string?":true,"add-default-userland-constraints?":true}}'
    }
    response = Metabase_proxy.post(f'{url}api/dataset/xlsx', headers, data)

    if response.status_code == 200:
        in_memory_file = SimpleUploadedFile("test.xlsx", response.content)
        file = FileSerializer(data={"file": in_memory_file})
        file.is_valid(raise_exception=True)
        file.save()
        print("File created successfully:")
        return file.data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")


@api_view(["post"])
def get_form_respondents_info(request):
    form_id = request.data.get('form_id')
    file_content = get_form_respondents_info_file(form_id=form_id)
    return Response(file_content)


@api_view(["post"])
def get_form_respondents_answers(request):
    form_id = request.data.get('form_id')
    file_content = get_form_respondents_answers_file(form_id=form_id)
    return Response(file_content)
