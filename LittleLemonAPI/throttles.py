from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class MenuUserThrottle(UserRateThrottle):
    scope = "menu_user"

class MenuAnonThrottle(AnonRateThrottle):
    scope = "menu_anon"

class HealthzThrottle(AnonRateThrottle):
    scope = "healthz"