import django_filters
from ..models import Student, Teacher
from django.db.models import Q

#import models

class StudentFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(method='filter_full_name')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    phone = django_filters.CharFilter(field_name='phone', lookup_expr='icontains')
    
    
    def filter_full_name(self, queryset, name, value):
        # Split the search by spaces
        parts = value.strip().split()
        
        # Build Q objects dynamically
        q = Q()
        for part in parts:
            q &= (Q(first_name__icontains=part) | Q(last_name__icontains=part)) | Q(middle_name__icontains=part)
        
        return queryset.filter(q)
        
    class Meta:
        model = Student
        fields = [
            'id', 'gender', 'admission_number'
        ]
        
class TeacherFilter(django_filters.FilterSet):
    # Full name filter using method
    full_name = django_filters.CharFilter(method='filter_full_name')
    
    # Direct filters on real DB fields
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    phone = django_filters.CharFilter(field_name='phone', lookup_expr='icontains')
    
    # Optional: filter by status or designation
    designation = django_filters.CharFilter(field_name='designation', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    
    def filter_full_name(self, queryset, name, value):
        """
        Search full name including first, middle, last names.
        Handles multi-word search strings like "Aaron Jeffery Jones".
        """
        parts = value.strip().split()
        q = Q()
        for part in parts:
            q &= (Q(first_name__icontains=part) |
                  Q(middle_name__icontains=part) |
                  Q(last_name__icontains=part))
        return queryset.filter(q)
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'status', 'designation'
        ]