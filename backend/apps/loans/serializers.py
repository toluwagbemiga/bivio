# backend/apps/loans/serializers.py
"""
Loan serializers for loan management
"""

from rest_framework import serializers
from .models import LoanProduct, Loan, LoanRepayment


class LoanProductSerializer(serializers.ModelSerializer):
    """
    Serializer for loan products
    """
    
    class Meta:
        model = LoanProduct
        fields = [
            'id', 'name', 'description', 'min_amount', 'max_amount',
            'interest_rate', 'interest_type', 'processing_fee_rate',
            'min_tenure_days', 'max_tenure_days', 'repayment_frequency',
            'min_credit_score', 'min_monthly_revenue', 'min_business_age_months',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LoanSerializer(serializers.ModelSerializer):
    """
    Serializer for loan applications and management
    """
    loan_product_name = serializers.ReadOnlyField(source='loan_product.name')
    borrower_name = serializers.ReadOnlyField(source='borrower.get_full_name')
    is_overdue = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    next_payment_date = serializers.ReadOnlyField()
    
    class Meta:
        model = Loan
        fields = [
            'id', 'loan_number', 'borrower', 'borrower_name', 'loan_product',
            'loan_product_name', 'application_date', 'principal_amount',
            'interest_rate', 'tenure_days', 'processing_fee', 'total_interest',
            'total_amount', 'monthly_installment', 'amount_paid',
            'outstanding_balance', 'approved_date', 'disbursed_date',
            'first_repayment_date', 'final_repayment_date', 'status',
            'days_past_due', 'risk_level', 'collateral_type', 'collateral_value',
            'collateral_description', 'purpose', 'business_plan',
            'approval_notes', 'rejection_reason', 'enable_auto_deduction',
            'auto_deduction_percentage', 'is_overdue', 'completion_percentage',
            'next_payment_date', 'created_at'
        ]
        read_only_fields = [
            'id', 'loan_number', 'borrower_name', 'loan_product_name',
            'processing_fee', 'total_interest', 'total_amount', 'monthly_installment',
            'amount_paid', 'outstanding_balance', 'days_past_due',
            'is_overdue', 'completion_percentage', 'next_payment_date',
            'application_date', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['borrower'] = self.context['request'].user
        return super().create(validated_data)


class LoanRepaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for loan repayments
    """
    loan_number = serializers.ReadOnlyField(source='loan.loan_number')
    borrower_name = serializers.ReadOnlyField(source='loan.borrower.get_full_name')
    
    class Meta:
        model = LoanRepayment
        fields = [
            'id', 'loan', 'loan_number', 'borrower_name', 'payment_reference',
            'repayment_type', 'scheduled_amount', 'paid_amount', 'principal_amount',
            'interest_amount', 'penalty_amount', 'payment_method',
            'transaction_reference', 'due_date', 'payment_date', 'status',
            'days_late', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'loan_number', 'borrower_name', 'payment_reference',
            'days_late', 'created_at'
        ]


