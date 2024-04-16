from django.core.management.base import BaseCommand
from apps.fsm.models import Iframe
from urllib.parse import urlparse


def get_domain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain

# usage:
# url = 'http://abc.hostname.com/somethings/anything/'
# print(get_domain(url))  # abc.hostname.com


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--first_domain', dest='first_domain',  type=str)
        parser.add_argument('--second_domain', dest='second_domain', type=str)

    def handle(self, *args, **options):
        first_domain = options['first_domain']
        second_domain = options['second_domain']

        for iframe in Iframe.objects.all():
            if get_domain(iframe.link) == first_domain:
                iframe.link = iframe.link.replace(first_domain, second_domain)
                iframe.save()
