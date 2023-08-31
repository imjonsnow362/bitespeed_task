# Create your models here.

from django.db import models

#This is contact model
class Contact(models.Model):
    phoneNumber = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    linkedId = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    linkPrecedence = models.CharField(max_length=10)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    deletedAt = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} - {self.phoneNumber}"

