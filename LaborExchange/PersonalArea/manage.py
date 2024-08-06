from lib2to3.pytree import Base
from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password, surname, name):
        user = self.model(email=email, password=password, name=name, surname=surname)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password, surname, name):
        user = self.create_user(email=email, password=password, name=name, surname=surname)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user
    
    def get_by_natural_key(self, email_):
        print(email_)
        return self.get(email=email_)