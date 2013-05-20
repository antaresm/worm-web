# -*- coding: utf-8
from django.contrib.auth.models import User
from django.db import models


class WUser(User):
    avatar=models.CharField(max_length=64)
    token=models.CharField(max_length=64)
    token_time=models.DateTimeField()

    def __unicode__(self):
        return self.username