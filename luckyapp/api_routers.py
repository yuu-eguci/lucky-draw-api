from rest_framework import routers

from attendee import view_sets as attendee_vs

# Register api routes here
router = routers.DefaultRouter()
router.register(r"attendee", attendee_vs.AttendeeViewSet)

# 末尾の / を省略した書き込みは APPEND_SLASH で 500 (DEBUG) や 301 になるため、
# / なしの URL も受け付けます。URL の逆引きは / 付きの router を使います
no_slash_router = routers.SimpleRouter(trailing_slash=False)
no_slash_router.register(
    r"attendee", attendee_vs.AttendeeViewSet, basename="attendee-no-slash"
)
