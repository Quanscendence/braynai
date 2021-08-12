from rest_framework import serializers
from coreapp import models

class InvoiceSerializer(serializers.Serializer):

    invoice_id     = serializers.CharField(max_length=30)
    amount         = serializers.FloatField()
    transaction_id = serializers.CharField(max_length=30) 

