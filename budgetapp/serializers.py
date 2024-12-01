from rest_framework import serializers
from .models import PDFContent

class PDFContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDFContent
        fields = '__all__'
