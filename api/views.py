from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from rest_framework.response import Response
from rest_framework_api_key.models import APIKey

import json
import razorpay
from . serializers import InvoiceSerializer
from coreapp.models import ProjectInvoice
from django.http import HttpResponse
# from coreapp import coreapp_global_logger

# view-logging
# vl = coreapp_global_logger.LogMe()
class APIViewSet(viewsets.ViewSet):
   
    def create(self, request, *args, **kwargs):
        jsondata = request.body
        data = json.loads(jsondata)
        print(data)
        return Response(request.data)

class InvoiceAutoCaptureViewSet(viewsets.ViewSet):
    serializer_class = InvoiceSerializer
    def create(self, request, *args, **kwargs):
        # vl.fullbari("invoiceapiView::post the invoice api request:", request.data)
        
        invoice_id = int(request.data['invoice_id'])
        amount = float(request.data['amount'])
        transaction_id = request.data['transaction_id']

        update = ProjectInvoice.objects.filter(pk=invoice_id).update(status='Paid',transaction_id=transaction_id)

        client = razorpay.Client(auth=("", ""))

        payment_amount =amount  #paisa int(request.data['amount'])
        resp = client.payment.capture(transaction_id, payment_amount)



        return HttpResponse("Successfully Created")

    