# ai_analysis/serializers.py
from rest_framework import serializers
from .models import AIAnalysisLog

class AIAnalysisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisLog
        fields = ['gamer_type', 'analysis_text', 'recommendations', 'updated_at']