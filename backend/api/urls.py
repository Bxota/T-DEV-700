from django.urls import path
from .views import hello, hello_authenticated

urlpatterns = [
    path("hello/", hello, name="hello"),
    path("hello-auth/", hello_authenticated, name="hello_authenticated"),
]