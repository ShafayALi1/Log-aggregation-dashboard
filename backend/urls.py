from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from views import LogSourceViewSet, LogViewSet, AlertRuleViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'sources', LogSourceViewSet, basename='logsource')
router.register(r'logs', LogViewSet, basename='log')
router.register(r'rules', AlertRuleViewSet, basename='alertrule')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
