from django.conf.urls import url
from django.urls import path
from rest_framework import routers
from .views import APIViewSet,InvoiceAutoCaptureViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('segment-receive', APIViewSet, basename="Segment")
router.register('invoice', InvoiceAutoCaptureViewSet, basename="invoice")

urlpatterns = router.urls
