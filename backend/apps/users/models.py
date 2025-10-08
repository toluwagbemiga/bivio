# apps/users/models.py
"""
User models for POS Financial Management App
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Designed for Nigerian micro-business owners and POS agents
    """
    
    USER_TYPES = [
        ('borrower', 'Borrower (Business Owner)'),
        ('lender', 'Lender (Bank/MFI)'),
        ('agent', 'POS Agent'),
        ('super_agent', 'Super Agent'),
        ('admin', 'System Admin'),
    ]
    
    VERIFICATION_STATUS = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?234[0-9]{10}$|^0[0-9]{10}$',
                message='Enter a valid Nigerian phone number'
            )
        ]
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='borrower')
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='unverified'
    )
    
    # Nigerian-specific identification
    bvn = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{11}$',
                message='BVN must be 11 digits'
            )
        ],
        help_text='Bank Verification Number'
    )
    nin = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{11}$',
                message='NIN must be 11 digits'
            )
        ],
        help_text='National Identification Number'
    )
    
    # Profile completion and activity
    is_profile_complete = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['bvn']),
            models.Index(fields=['user_type']),
            models.Index(fields=['verification_status']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_profile(self):
        """Get user's business profile"""
        try:
            return self.business_profile
        except BusinessProfile.DoesNotExist:
            return None
    
    def is_verified(self):
        """Check if user is verified"""
        return self.verification_status == 'verified'
    
    def can_take_loan(self):
        """Check if user can take a loan"""
        return (
            self.is_verified() and 
            self.user_type in ['borrower', 'agent'] and
            self.is_profile_complete
        )


class BusinessProfile(models.Model):
    """
    Business profile for users (borrowers, agents)
    """
    
    BUSINESS_TYPES = [
        ('retail', 'Retail Shop'),
        ('restaurant', 'Restaurant/Food'),
        ('pos_agent', 'POS Agent'),
        ('wholesale', 'Wholesale Trading'),
        ('services', 'Services'),
        ('manufacturing', 'Manufacturing'),
        ('agriculture', 'Agriculture'),
        ('other', 'Other'),
    ]
    
    BUSINESS_SIZES = [
        ('micro', 'Micro (1-10 employees)'),
        ('small', 'Small (11-50 employees)'),
        ('medium', 'Medium (51-200 employees)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='business_profile'
    )
    
    # Business Information
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    business_size = models.CharField(max_length=20, choices=BUSINESS_SIZES, default='micro')
    business_description = models.TextField(blank=True)
    
    # Location
    business_address = models.TextField()
    state = models.CharField(max_length=50)
    lga = models.CharField(max_length=100, help_text='Local Government Area')
    city = models.CharField(max_length=100)
    
    # Financial Information
    estimated_monthly_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Estimated monthly revenue in Naira'
    )
    years_in_business = models.PositiveIntegerField(default=0)
    
    # Documentation
    business_registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='CAC Registration Number'
    )
    tax_identification_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='TIN Number'
    )
    
    # POS-specific information
    pos_device_serial = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text='POS device serial number if applicable'
    )
    pos_provider = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='POS service provider (Moniepoint, OPay, etc.)'
    )
    
    # Credit Information
    credit_score = models.PositiveIntegerField(default=0, help_text='Calculated credit score 0-1000')
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('very_high', 'Very High Risk'),
        ],
        default='medium'
    )
    
    # Bank Account Information
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_code = models.CharField(max_length=10, blank=True, null=True)
    account_name = models.CharField(max_length=200, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?234[0-9]{10}$|^0[0-9]{10}$',
                message='Enter a valid Nigerian phone number'
            )
        ]
    )
    emergency_contact_relationship = models.CharField(max_length=100)
    
    # Verification and Status
    is_business_verified = models.BooleanField(default=False)
    verification_documents_uploaded = models.BooleanField(default=False)
    kyc_completed = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_profiles'
        verbose_name = _('Business Profile')
        verbose_name_plural = _('Business Profiles')
        indexes = [
            models.Index(fields=['business_type']),
            models.Index(fields=['state']),
            models.Index(fields=['credit_score']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['pos_device_serial']),
        ]
    
    def __str__(self):
        return f"{self.business_name} - {self.user.get_full_name()}"
    
    @property
    def is_complete(self):
        """Check if business profile is complete"""
        required_fields = [
            self.business_name,
            self.business_type,
            self.business_address,
            self.state,
            self.city,
            self.emergency_contact_name,
            self.emergency_contact_phone,
        ]
        return all(field for field in required_fields)
    
    def calculate_credit_score(self):
        """Calculate credit score based on various factors"""
        score = 500  # Base score
        
        # Years in business factor
        if self.years_in_business >= 5:
            score += 100
        elif self.years_in_business >= 2:
            score += 50
        
        # Revenue factor
        if self.estimated_monthly_revenue:
            if self.estimated_monthly_revenue >= 1000000:
                score += 150
            elif self.estimated_monthly_revenue >= 500000:
                score += 100
            elif self.estimated_monthly_revenue >= 200000:
                score += 50
        
        # Verification factors
        if self.is_business_verified:
            score += 100
        if self.kyc_completed:
            score += 50
        if self.business_registration_number:
            score += 25
        
        # Cap at 1000
        self.credit_score = min(score, 1000)
        return self.credit_score


class Guarantor(models.Model):
    """
    Guarantor information for loans
    """
    
    RELATIONSHIP_TYPES = [
        ('family', 'Family Member'),
        ('friend', 'Friend'),
        ('business_partner', 'Business Partner'),
        ('colleague', 'Colleague'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='guarantors'
    )
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?234[0-9]{10}$|^0[0-9]{10}$',
                message='Enter a valid Nigerian phone number'
            )
        ]
    )
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Identification
    bvn = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{11}$',
                message='BVN must be 11 digits'
            )
        ]
    )
    
    # Relationship
    relationship_to_borrower = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES
    )
    how_long_known = models.PositiveIntegerField(
        help_text='How long have you known the borrower (in years)?'
    )
    
    # Financial Information
    occupation = models.CharField(max_length=200)
    employer = models.CharField(max_length=200, blank=True, null=True)
    monthly_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Agreement
    has_agreed_to_guarantee = models.BooleanField(default=False)
    agreement_signed_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'guarantors'
        verbose_name = _('Guarantor')
        verbose_name_plural = _('Guarantors')
        unique_together = ['borrower', 'bvn']
        indexes = [
            models.Index(fields=['bvn']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['borrower']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - Guarantor for {self.borrower.get_full_name()}"