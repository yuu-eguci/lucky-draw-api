from rest_framework import routers
from attendee import view_sets as attendee_vs

# Register api routes here
router = routers.DefaultRouter()
router.register(r'attendee', attendee_vs.AttendeeViewSet)