from rest_framework.pagination import PageNumberPagination


class RegistrationReceiptSetPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000


class StandardPagination(PageNumberPagination):
    page_size = 12
