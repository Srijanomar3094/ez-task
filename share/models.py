from django.db import models
from django.contrib.auth.models import User
from user_auth.models import BaseModel

    
class File(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file_name = models.FileField(upload_to='', null=True)
    file_size_kb = models.BigIntegerField(null=True)
    last_opened = models.DateTimeField(auto_now=True)