# backend/apps/ai_categorization/management/commands/train_categorizer.py
"""
Management command to train the category classification model
"""

from django.core.management.base import BaseCommand
from apps.ai_categorization.models import TrainingData, ModelPerformance
from apps.ai_categorization.services import AICategorizationService
import json
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Train the category classification model'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--export-data',
            action='store_true',
            help='Export training data to AI service',
        )
        parser.add_argument(
            '--train-model',
            action='store_true',
            help='Train the model using exported data',
        )
        parser.add_argument(
            '--evaluate-model',
            action='store_true',
            help='Evaluate model performance',
        )
    
    def handle(self, *args, **options):
        ai_service = AICategorizationService()
        
        if options['export_data']:
            self.export_training_data()
        
        if options['train_model']:
            self.train_model()
        
        if options['evaluate_model']:
            self.evaluate_model()
    
    def export_training_data(self):
        """Export training data to AI service"""
        self.stdout.write('Exporting training data...')
        
        # Get validated training data
        training_data = TrainingData.objects.filter(
            is_validated=True,
            status='validated'
        ).select_related('category')
        
        export_data = []
        for data in training_data:
            export_data.append({
                'text': data.processed_text or data.text_input,
                'category': data.category.category_type,
                'language': data.language,
                'features': data.features
            })
        
        try:
            response = requests.post(
                f"{settings.AI_SERVICE_URL}/ai/export-training-data",
                json={'data': export_data}
            )
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS(f'Exported {len(export_data)} training samples')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Export failed: {response.text}')
                )
                
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Export failed: {str(e)}')
            )
    
    def train_model(self):
        """Train the classification model"""
        self.stdout.write('Training model...')
        
        try:
            response = requests.post(
                f"{settings.AI_SERVICE_URL}/ai/train-model",
                json={'model_type': 'category_classifier'}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.stdout.write(
                    self.style.SUCCESS(f'Model trained successfully: {result}')
                )
                
                # Save performance metrics
                ModelPerformance.objects.create(
                    model_version=result.get('version', 'unknown'),
                    model_type='category_classifier',
                    accuracy=result.get('accuracy', 0),
                    precision=result.get('precision', 0),
                    recall=result.get('recall', 0),
                    f1_score=result.get('f1_score', 0),
                    training_samples=result.get('training_samples', 0),
                    validation_samples=result.get('validation_samples', 0),
                    training_time_seconds=result.get('training_time', 0),
                    hyperparameters=result.get('hyperparameters', {}),
                    confusion_matrix=result.get('confusion_matrix', {}),
                    class_metrics=result.get('class_metrics', {})
                )
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'Training failed: {response.text}')
                )
                
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Training failed: {str(e)}')
            )
    
    def evaluate_model(self):
        """Evaluate model performance"""
        self.stdout.write('Evaluating model...')
        
        try:
            response = requests.get(
                f"{settings.AI_SERVICE_URL}/ai/model-performance"
            )
            
            if response.status_code == 200:
                result = response.json()
                self.stdout.write('Model Performance:')
                self.stdout.write(f"  Accuracy: {result.get('accuracy', 0):.2%}")
                self.stdout.write(f"  Precision: {result.get('precision', 0):.2%}")
                self.stdout.write(f"  Recall: {result.get('recall', 0):.2%}")
                self.stdout.write(f"  F1 Score: {result.get('f1_score', 0):.2%}")
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'Evaluation failed: {response.text}')
                )
                
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Evaluation failed: {str(e)}')
            )