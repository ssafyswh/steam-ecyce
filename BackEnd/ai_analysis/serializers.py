# ai_analysis/serializers.py

from rest_framework import serializers
from .models import AIAnalysisLog, ReviewSummary

class AIAnalysisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysisLog
        fields = ['gamer_type', 'analysis_text', 'recommendations', 'updated_at']
        

class ReviewSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewSummary
        fields = ['status', 'summary_text', 'last_updated_at']