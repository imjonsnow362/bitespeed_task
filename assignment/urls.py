from django.urls import path
from .views import identify_contact
#hello
urlpatterns = [
    path('identify/', identify_contact, name='identify-contact'),
]
