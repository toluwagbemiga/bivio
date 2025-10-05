# backend/apps/savings/serializers.py
"""
Savings serializers for savings accounts and transactions
"""

from rest_framework import serializers
from .models import SavingsAccount, SavingsTransaction, SavingsGoal


class SavingsAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for savings accounts
    """
    progress_percentage = serializers.ReadOnlyField()
    remaining_to_target = serializers.ReadOnlyField()
    
    class Meta:
        model = SavingsAccount
        fields = [
            'id', 'account_number', 'account_name', 'account_type',
            'current_balance', 'minimum_balance', 'target_amount',
            'auto_save_enabled', 'auto_save_percentage', 'auto_save_minimum',
            'auto_save_maximum', 'interest_rate', 'total_interest_earned',
            'status', 'is_default', 'progress_percentage', 'remaining_to_target',
            'created_at'
        ]
        read_only_fields = [
            'id', 'account_number', 'current_balance', 'total_interest_earned',
            'progress_percentage', 'remaining_to_target', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SavingsTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for savings transactions
    """
    account_name = serializers.ReadOnlyField(source='savings_account.account_name')
    is_credit = serializers.ReadOnlyField()
    is_debit = serializers.ReadOnlyField()
    
    class Meta:
        model = SavingsTransaction
        fields = [
            'id', 'savings_account', 'account_name', 'transaction_reference',
            'transaction_type', 'amount', 'reference', 'source_transaction_id',
            'balance_before', 'balance_after', 'status', 'notes',
            'is_credit', 'is_debit', 'transaction_date'
        ]
        read_only_fields = [
            'id', 'account_name', 'transaction_reference', 'balance_before',
            'balance_after', 'is_credit', 'is_debit', 'transaction_date'
        ]


class SavingsGoalSerializer(serializers.ModelSerializer):
    """
    Serializer for savings goals
    """
    progress_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    account_name = serializers.ReadOnlyField(source='savings_account.account_name')
    
    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'savings_account', 'account_name', 'name', 'description',
            'target_amount', 'current_amount', 'target_date', 'monthly_target',
            'status', 'completed_date', 'progress_percentage', 'remaining_amount',
            'days_remaining', 'created_at'
        ]
        read_only_fields = [
            'id', 'account_name', 'current_amount', 'monthly_target',
            'completed_date', 'progress_percentage', 'remaining_amount',
            'days_remaining', 'created_at'
        ]


