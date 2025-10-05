# backend/apps/users/serializers.py
"""
User serializers for authentication and profile management
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, BusinessProfile, Guarantor


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'password', 'password_confirm', 'user_type'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'user_type', 'verification_status', 'bvn', 'nin',
            'is_profile_complete', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'verification_status', 'created_at']


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for business profile information
    """
    is_complete = serializers.ReadOnlyField()
    credit_score = serializers.ReadOnlyField()
    
    class Meta:
        model = BusinessProfile
        fields = [
            'id', 'business_name', 'business_type', 'business_size',
            'business_description', 'business_address', 'state', 'lga', 'city',
            'estimated_monthly_revenue', 'years_in_business',
            'business_registration_number', 'tax_identification_number',
            'pos_device_serial', 'pos_provider', 'credit_score', 'risk_level',
            'bank_account_number', 'bank_name', 'bank_code', 'account_name',
            'emergency_contact_name', 'emergency_contact_phone', 
            'emergency_contact_relationship', 'is_business_verified',
            'verification_documents_uploaded', 'kyc_completed', 'is_complete'
        ]
        read_only_fields = ['id', 'credit_score', 'risk_level', 'is_complete']
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        # Recalculate credit score when profile is updated
        instance.calculate_credit_score()
        return instance


class GuarantorSerializer(serializers.ModelSerializer):
    """
    Serializer for guarantor information
    """
    
    class Meta:
        model = Guarantor
        fields = [
            'id', 'full_name', 'phone_number', 'email', 'address', 'bvn',
            'relationship_to_borrower', 'how_long_known', 'occupation',
            'employer', 'monthly_income', 'has_agreed_to_guarantee',
            'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


