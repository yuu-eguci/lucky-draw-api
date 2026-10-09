from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    validate_email,
    validate_slug,
)
from django.db import models


class Attendee(models.Model):
    # properties
    MIN_NAME_LEN = 1
    MAX_NAME_LEN = 64
    MAX_PHONE_LEN = 10
    MIN_PHONE_LEN = 8

    name = models.CharField(
        max_length=MAX_NAME_LEN,
        validators=[
            MinLengthValidator(MIN_NAME_LEN),
            MaxLengthValidator(MAX_NAME_LEN),
        ],
    )
    email = models.EmailField(unique=True, validators=[validate_email])
    phone = models.CharField(
        unique=True,
        max_length=MAX_PHONE_LEN,
        validators=[
            validate_slug,
            MinLengthValidator(MIN_PHONE_LEN),
            MaxLengthValidator(MAX_PHONE_LEN),
        ],
    )

    class Meta:
        verbose_name = "attendee table"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
