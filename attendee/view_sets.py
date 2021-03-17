from rest_framework import viewsets
from .models import Attendee
from .serializers import AttendeeSerializer

class AttendeeViewSet(viewsets.ModelViewSet):
    queryset = Attendee.objects.all()
    serializer_class = AttendeeSerializer