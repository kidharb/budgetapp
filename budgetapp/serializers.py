from rest_framework import serializers
from .models import CSVContent

class CSVContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVContent
        fields = '__all__'
