from rest_framework import serializers
from . import models

class AttendeeSerializer(serializers.ModelSerializer):
    ''' Attendee serializer

    '''

    class Meta:
        model  = models.Attendee
        fields = ('__all__')
