"""
Serializers for bulk operations endpoints
"""

from rest_framework import serializers


class CSVImportSerializer(serializers.Serializer):
    """Serializer for CSV file upload"""
    csv_file = serializers.FileField()
    
    def validate_csv_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("File must be a CSV file.")
        return value


class ExcelExportSerializer(serializers.Serializer):
    """Serializer for Excel export parameters"""
    standard_id = serializers.IntegerField(required=False, allow_null=True)
    exam_id = serializers.IntegerField(required=False, allow_null=True)
    academic_year_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)


class BulkOperationResponseSerializer(serializers.Serializer):
    """Serializer for bulk operation responses"""
    created = serializers.IntegerField()
    updated = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.CharField())
