# ai_services/api/services/ml_service.py
"""
Machine Learning Service for Nigerian Product Categorization
Handles model training, prediction, and Nigerian market-specific logic
"""

import os
import json
import pickle
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import joblib
from collections import Counter, defaultdict

# ML imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

logger = logging.getLogger(__name__)

class MLService:
    """
    Machine Learning service for product categorization
    """
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.model_version = "v1.0"
        self.model_path = "models/"
        self.is_initialized = False
        
        # Nigerian-specific categories and mappings
        self.nigerian_categories = {
            'food_beverages': {
                'keywords': [
                    'indomie', 'milo', 'peak', 'milk', 'gala', 'meat', 'pie', 'bread',
                    'rice', 'beans', 'garri', 'yam', 'plantain', 'egg', 'chicken', 'fish',
                    'palm_oil', 'groundnut_oil', 'tomato', 'onion', 'pepper', 'maggi',
                    'knorr', 'coke', 'pepsi', 'sprite', 'fanta', 'malt', 'water',
                    'akara', 'suya', 'boli', 'pap', 'zobo', 'kunu', 'fura', 'kilishi'
                ],
                'patterns': ['food', 'drink', 'beverage', 'eat', 'meal']
            },
            'electronics': {
                'keywords': [
                    'phone', 'charger', 'battery', 'memory', 'card', 'earpiece', 'speaker',
                    'torch', 'radio', 'tv', 'television', 'fan', 'iron', 'kettle',
                    'samsung', 'tecno', 'infinix', 'itel', 'nokia'
                ],
                'patterns': ['electronic', 'device', 'gadget', 'tech']
            },
            'airtime_data': {
                'keywords': [
                    'airtime', 'recharge', 'card', 'data', 'credit', 'mtn', 'glo',
                    'airtel', '9mobile', 'etisalat', 'call', 'sms', 'internet'
                ],
                'patterns': ['telecom', 'mobile', 'network']
            },
            'household': {
                'keywords': [
                    'detergent', 'soap', 'sponge', 'broom', 'bucket', 'plate', 'spoon',
                    'cup', 'candle', 'matchbox', 'kerosene', 'gas', 'cleaning'
                ],
                'patterns': ['home', 'house', 'clean', 'kitchen']
            },
            'cosmetics': {
                'keywords': [
                    'cream', 'lotion', 'powder', 'perfume', 'deodorant', 'toothpaste',
                    'toothbrush', 'shampoo', 'hair', 'pomade', 'vaseline', 'bathing'
                ],
                'patterns': ['beauty', 'care', 'skin', 'personal']
            },
            'clothing': {
                'keywords': [
                    'shirt', 'trouser', 'dress', 'shoe', 'sandal', 'cap', 'wrapper',
                    'ankara', 'lace', 'fabric', 'cloth'
                ],
                'patterns': ['wear', 'fashion', 'style']
            },
            'stationery': {
                'keywords': [
                    'pen', 'pencil', 'book', 'exercise', 'ruler', 'eraser', 'paper',
                    'envelope', 'notebook', 'biro'
                ],
                'patterns': ['school', 'office', 'write']
            }
        }
        
        # Initialize NLTK components
        self._initialize_nltk()
        
        # Performance tracking
        self.prediction_history = []
        self.model_performance = {}
    
    def _initialize_nltk(self):
        """Initialize NLTK components"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
        except Exception as e:
            logger.warning(f"NLTK initialization warning: {e}")
    
    def initialize(self):
        """Initialize the ML service"""
        try:
            # Create directories
            os.makedirs(self.model_path, exist_ok=True)
            os.makedirs("data", exist_ok=True)
            
            # Load existing model if available
            self.load_model()
            
            # Initialize with Nigerian product data if no model exists
            if not self.is_model_loaded():
                self._initialize_with_nigerian_data()
            
            self.is_initialized = True
            logger.info("ML Service initialized successfully")
            
        except Exception as e:
            logger.error(f"ML Service initialization failed: {e}")
            raise e
    
    def _initialize_with_nigerian_data(self):
        """Initialize with pre-defined Nigerian product data"""
        logger.info("Initializing with Nigerian product data...")
        
        # Create training data from Nigerian categories
        training_data = []
        for category, data in self.nigerian_categories.items():
            # Add keywords as training examples
            for keyword in data['keywords']:
                training_data.append({
                    'text': keyword,
                    'category': category,
                    'language': 'en'
                })
            
            # Add pattern-based examples
            for pattern in data['patterns']:
                training_data.append({
                    'text': pattern,
                    'category': category,
                    'language': 'en'
                })
        
        # Train initial model
        if training_data:
            self._train_model_with_data(training_data)
            logger.info(f"Initialized model with {len(training_data)} Nigerian product examples")
    
    def preprocess_text_for_ml(self, text: str, language: str = 'en') -> str:
        """Preprocess text specifically for ML model"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Handle Nigerian-specific preprocessing
        if language in ['pidgin', 'ha', 'ig', 'yo']:
            text = self._preprocess_nigerian_text(text, language)
        
        # Tokenize
        try:
            tokens = word_tokenize(text)
        except:
            tokens = text.split()
        
        # Remove stopwords (English)
        try:
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        except:
            tokens = [token for token in tokens if len(token) > 2]
        
        # Stem words
        try:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(token) for token in tokens]
        except:
            pass
        
        return ' '.join(tokens)
    
    def _preprocess_nigerian_text(self, text: str, language: str) -> str:
        """Preprocess Nigerian local language text"""
        # Language-specific mappings
        mappings = {
            'pidgin': {
                'wetin': 'what', 'how_much': 'price', 'how_far': 'how',
                'no_wahala': 'no_problem', 'abi': 'right', 'sha': 'just'
            },
            'ha': {  # Hausa
                'nawa': 'how_much', 'abinci': 'food', 'ruwa': 'water',
                'nama': 'meat', 'wake': 'beans'
            },
            'yo': {  # Yoruba
                'eelo': 'how_much', 'ounje': 'food', 'omi': 'water',
                'eran': 'meat', 'ewa': 'beans'
            },
            'ig': {  # Igbo
                'ego_ole': 'how_much', 'nri': 'food', 'mmiri': 'water',
                'anu': 'meat', 'agwa': 'beans'
            }
        }
        
        if language in mappings:
            for local_word, english_word in mappings[language].items():
                text = text.replace(local_word, english_word)
        
        return text
    
    def predict_category(self, features: Dict, user_id: Optional[str] = None, 
                        context: Optional[Dict] = None) -> Dict:
        """Predict category for given features"""
        try:
            text = features.get('text', '')
            
            if not text:
                return self._get_default_prediction()
            
            # Try rule-based prediction first (faster and more accurate for known items)
            rule_based = self._predict_with_rules(text, features)
            if rule_based and rule_based['confidence'] > 0.8:
                return rule_based
            
            # Use ML model if available
            if self.is_model_loaded():
                ml_prediction = self._predict_with_model(text, features)
                if ml_prediction and ml_prediction['confidence'] > 0.5:
                    return ml_prediction
            
            # Fallback to rule-based even with lower confidence
            if rule_based:
                return rule_based
            
            return self._get_default_prediction()
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._get_default_prediction()
    
    def _predict_with_rules(self, text: str, features: Dict) -> Optional[Dict]:
        """Rule-based prediction using Nigerian product mappings"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Direct keyword matching
        for category, data in self.nigerian_categories.items():
            # Check keywords
            for keyword in data['keywords']:
                if keyword in text_lower or any(keyword in word for word in words):
                    return {
                        'category': {
                            'name': category.replace('_', ' ').title(),
                            'category_type': category,
                            'id': f"rule_{category}"
                        },
                        'confidence': 0.9,
                        'method': 'rule_based',
                        'model_version': self.model_version,
                        'alternatives': self._get_alternative_categories(category)
                    }
            
            # Check patterns
            for pattern in data['patterns']:
                if pattern in text_lower:
                    return {
                        'category': {
                            'name': category.replace('_', ' ').title(),
                            'category_type': category,
                            'id': f"rule_{category}"
                        },
                        'confidence': 0.7,
                        'method': 'pattern_based',
                        'model_version': self.model_version,
                        'alternatives': self._get_alternative_categories(category)
                    }
        
        return None
    
    def _predict_with_model(self, text: str, features: Dict) -> Optional[Dict]:
        """ML model-based prediction"""
        try:
            if not self.model or not self.vectorizer:
                return None
            
            # Preprocess text for ML
            processed_text = self.preprocess_text_for_ml(
                text, 
                features.get('language', 'en')
            )
            
            if not processed_text:
                return None
            
            # Vectorize
            text_vector = self.vectorizer.transform([processed_text])
            
            # Get prediction
            prediction = self.model.predict(text_vector)[0]
            
            # Get confidence (probability)
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(text_vector)[0]
                confidence = max(probabilities)
                
                # Get alternatives
                if hasattr(self.model, 'classes_'):
                    class_probs = list(zip(self.model.classes_, probabilities))
                    class_probs.sort(key=lambda x: x[1], reverse=True)
                    alternatives = [
                        {
                            'category': {
                                'name': cls.replace('_', ' ').title(),
                                'category_type': cls,
                                'id': f"ml_{cls}"
                            },
                            'confidence': prob
                        }
                        for cls, prob in class_probs[1:4]  # Top 3 alternatives
                    ]
                else:
                    alternatives = []
            else:
                confidence = 0.6  # Default confidence for models without probability
                alternatives = []
            
            return {
                'category': {
                    'name': prediction.replace('_', ' ').title(),
                    'category_type': prediction,
                    'id': f"ml_{prediction}"
                },
                'confidence': float(confidence),
                'method': 'ml_model',
                'model_version': self.model_version,
                'alternatives': alternatives
            }
            
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return None
    
    def _get_alternative_categories(self, main_category: str) -> List[Dict]:
        """Get alternative categories for rule-based predictions"""
        alternatives = []
        
        # Related categories mapping
        related_categories = {
            'food_beverages': ['household', 'cosmetics'],
            'electronics': ['household', 'stationery'],
            'airtime_data': ['electronics', 'services'],
            'household': ['food_beverages', 'cosmetics'],
            'cosmetics': ['household', 'clothing'],
            'clothing': ['cosmetics', 'accessories'],
            'stationery': ['electronics', 'household']
        }
        
        for alt_category in related_categories.get(main_category, []):
            alternatives.append({
                'category': {
                    'name': alt_category.replace('_', ' ').title(),
                    'category_type': alt_category,
                    'id': f"alt_{alt_category}"
                },
                'confidence': 0.3
            })
        
        return alternatives[:2]  # Limit to 2 alternatives
    
    def _get_default_prediction(self) -> Dict:
        """Get default prediction when others fail"""
        return {
            'category': {
                'name': 'Other',
                'category_type': 'other',
                'id': 'default_other'
            },
            'confidence': 0.3,
            'method': 'default',
            'model_version': self.model_version,
            'alternatives': []
        }
    
    def train_model(self, model_type: str = "category_classifier", 
                   hyperparameters: Optional[Dict] = None,
                   validation_split: float = 0.2) -> Dict:
        """Train the categorization model"""
        try:
            # Load training data
            training_data = self._load_training_data()
            if not training_data:
                raise ValueError("No training data available")
            
            # Train model
            results = self._train_model_with_data(
                training_data, 
                hyperparameters,
                validation_split
            )
            
            # Save model
            self.save_model()
            
            logger.info("Model training completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise e
    
    def _train_model_with_data(self, training_data: List[Dict], 
                              hyperparameters: Optional[Dict] = None,
                              validation_split: float = 0.2) -> Dict:
        """Train model with provided data"""
        # Prepare data
        texts = []
        labels = []
        
        for item in training_data:
            processed_text = self.preprocess_text_for_ml(
                item['text'], 
                item.get('language', 'en')
            )
            if processed_text:
                texts.append(processed_text)
                labels.append(item['category'])
        
        if not texts or not labels:
            raise ValueError("No valid training data after preprocessing")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=validation_split, random_state=42, stratify=labels
        )
        
        # Create vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        # Transform texts
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train model (using Naive Bayes for prototype)
        if hyperparameters:
            self.model = MultinomialNB(**hyperparameters)
        else:
            self.model = MultinomialNB(alpha=0.1)
        
        start_time = datetime.now()
        self.model.fit(X_train_vec, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluate model
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get detailed metrics
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        conf_matrix = confusion_matrix(y_test, y_pred, labels=self.model.classes_)
        
        # Store performance
        self.model_performance = {
            'accuracy': float(accuracy),
            'precision': float(report['weighted avg']['precision']),
            'recall': float(report['weighted avg']['recall']),
            'f1_score': float(report['weighted avg']['f1-score']),
            'training_samples': len(X_train),
            'validation_samples': len(X_test),
            'training_time': training_time,
            'model_version': self.model_version,
            'timestamp': datetime.now().isoformat(),
            'confusion_matrix': conf_matrix.tolist(),
            'class_metrics': {
                cls: {
                    'precision': float(metrics['precision']),
                    'recall': float(metrics['recall']),
                    'f1_score': float(metrics['f1-score']),
                    'support': int(metrics['support'])
                }
                for cls, metrics in report.items()
                if cls not in ['accuracy', 'macro avg', 'weighted avg']
            }
        }
        
        logger.info(f"Model trained - Accuracy: {accuracy:.2%}")
        
        return self.model_performance
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            os.makedirs(self.model_path, exist_ok=True)
            
            # Save model
            model_file = os.path.join(self.model_path, 'category_classifier.pkl')
            joblib.dump(self.model, model_file)
            
            # Save vectorizer
            vectorizer_file = os.path.join(self.model_path, 'vectorizer.pkl')
            joblib.dump(self.vectorizer, vectorizer_file)
            
            # Save performance metrics
            performance_file = os.path.join(self.model_path, 'performance.json')
            with open(performance_file, 'w') as f:
                json.dump(self.model_performance, f, indent=2)
            
            logger.info("Model saved successfully")
            
        except Exception as e:
            logger.error(f"Model save failed: {e}")
            raise e
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            model_file = os.path.join(self.model_path, 'category_classifier.pkl')
            vectorizer_file = os.path.join(self.model_path, 'vectorizer.pkl')
            
            if os.path.exists(model_file) and os.path.exists(vectorizer_file):
                self.model = joblib.load(model_file)
                self.vectorizer = joblib.load(vectorizer_file)
                
                # Load performance metrics
                performance_file = os.path.join(self.model_path, 'performance.json')
                if os.path.exists(performance_file):
                    with open(performance_file, 'r') as f:
                        self.model_performance = json.load(f)
                
                logger.info("Model loaded successfully")
                return True
            else:
                logger.info("No existing model found")
                return False
                
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            return False
    
    def reload_model(self) -> bool:
        """Reload the model"""
        return self.load_model()
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.vectorizer is not None
    
    def get_model_version(self) -> str:
        """Get current model version"""
        return self.model_version
    
    def get_model_performance(self) -> Dict:
        """Get model performance metrics"""
        if not self.model_performance:
            return {
                'message': 'No performance data available',
                'model_loaded': self.is_model_loaded()
            }
        return self.model_performance
    
    def has_training_data(self) -> bool:
        """Check if training data is available"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            return False
        
        training_files = [f for f in os.listdir(data_dir) if f.startswith('training_data')]
        return len(training_files) > 0
    
    def _load_training_data(self) -> List[Dict]:
        """Load all training data"""
        data_dir = "data"
        all_data = []
        
        if not os.path.exists(data_dir):
            return all_data
        
        # Load all training data files
        training_files = [f for f in os.listdir(data_dir) if f.startswith('training_data')]
        
        for filename in training_files:
            file_path = os.path.join(data_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
            except Exception as e:
                logger.warning(f"Failed to load {filename}: {e}")
        
        return all_data
    
    def process_training_data(self, data: List[Dict], model_type: str):
        """Process and prepare training data"""
        try:
            # Validate and clean data
            cleaned_data = []
            
            for item in data:
                if 'text' in item and 'category' in item:
                    # Preprocess text
                    processed = self.preprocess_text_for_ml(
                        item['text'], 
                        item.get('language', 'en')
                    )
                    
                    if processed:
                        cleaned_data.append({
                            'text': item['text'],
                            'processed_text': processed,
                            'category': item['category'],
                            'language': item.get('language', 'en'),
                            'features': item.get('features', {})
                        })
            
            logger.info(f"Processed {len(cleaned_data)} training samples")
            
        except Exception as e:
            logger.error(f"Training data processing failed: {e}")
    
    def get_category_suggestions(self, text: str, limit: int = 5, 
                                user_id: Optional[str] = None) -> List[Dict]:
        """Get category suggestions for autocomplete"""
        suggestions = []
        text_lower = text.lower()
        
        # Search through Nigerian categories
        for category, data in self.nigerian_categories.items():
            # Check keywords
            matching_keywords = [
                kw for kw in data['keywords'] 
                if kw.startswith(text_lower) or text_lower in kw
            ]
            
            for keyword in matching_keywords[:3]:  # Limit per category
                suggestions.append({
                    'text': keyword,
                    'category': {
                        'name': category.replace('_', ' ').title(),
                        'category_type': category,
                        'id': f"suggest_{category}"
                    },
                    'confidence': 0.85,
                    'source': 'predefined'
                })
        
        # Sort by relevance (starts with query gets priority)
        suggestions.sort(
            key=lambda x: (not x['text'].startswith(text_lower), x['text'])
        )
        
        return suggestions[:limit]
    
    def get_nigerian_market_insights(self, user_id: Optional[str] = None) -> Dict:
        """Get insights about Nigerian market categorization"""
        insights = {
            'total_categories': len(self.nigerian_categories),
            'categories': {},
            'most_common_products': [],
            'language_support': ['English', 'Pidgin', 'Hausa', 'Yoruba', 'Igbo'],
            'model_info': {
                'version': self.model_version,
                'is_loaded': self.is_model_loaded(),
                'accuracy': self.model_performance.get('accuracy', 0) if self.model_performance else 0
            }
        }
        
        # Category details
        for category, data in self.nigerian_categories.items():
            insights['categories'][category] = {
                'name': category.replace('_', ' ').title(),
                'keywords_count': len(data['keywords']),
                'sample_products': data['keywords'][:5]
            }
        
        # Most common products across all categories
        all_keywords = []
        for data in self.nigerian_categories.values():
            all_keywords.extend(data['keywords'][:10])
        
        insights['most_common_products'] = all_keywords[:20]
        
        return insights
    
    def cleanup(self):
        """Cleanup resources"""
        self.model = None
        self.vectorizer = None
        self.prediction_history = []
        logger.info("ML Service cleaned up")


# ai_services/api/services/preprocessing_service.py
"""
Text preprocessing service for Nigerian context
"""

import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PreprocessingService:
    """
    Preprocessing service for Nigerian text data
    """
    
    def __init__(self):
        self.is_initialized = False
        
        # Common Nigerian English variations
        self.nigerian_variations = {
            'recharge': 'airtime',
            'phone_card': 'airtime',
            'call_card': 'airtime',
            'handset': 'phone',
            'torchlight': 'torch',
            'mineral': 'water',
            'pure_water': 'water',
            'sachet_water': 'water',
            'soft_drink': 'drink',
            'beverage': 'drink',
            'biro': 'pen',
            'jotter': 'notebook',
        }
        
        # Currency patterns
        self.currency_patterns = [
            r'₦[\d,]+',
            r'NGN[\d,]+',
            r'naira[\d,]+',
            r'N[\d,]+'
        ]
    
    def initialize(self):
        """Initialize preprocessing service"""
        self.is_initialized = True
        logger.info("Preprocessing Service initialized")
    
    def preprocess_text(self, text: str) -> str:
        """Main preprocessing function"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Apply Nigerian variations
        for variant, standard in self.nigerian_variations.items():
            text = text.replace(variant, standard)
        
        return text.strip()
    
    def extract_features(self, text: str, context: Optional[Dict] = None,
                        language: str = 'en') -> Dict:
        """Extract features from text"""
        features = {
            'text': text,
            'word_count': len(text.split()),
            'char_count': len(text),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_currency': self._has_currency_mention(text),
            'language': language,
            'contains_brand': self._contains_brand(text)
        }
        
        # Add context features
        if context:
            features.update({
                'context_provided': True,
                'user_history': context.get('user_history', []),
                'time_context': context.get('time_of_day'),
                'location_context': context.get('location')
            })
        
        return features
    
    def _has_currency_mention(self, text: str) -> bool:
        """Check if text contains currency mentions"""
        for pattern in self.currency_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _contains_brand(self, text: str) -> bool:
        """Check if text contains known brands"""
        brands = [
            'mtn', 'glo', 'airtel', '9mobile', 'indomie', 'milo',
            'peak', 'maggi', 'knorr', 'samsung', 'tecno', 'infinix'
        ]
        text_lower = text.lower()
        return any(brand in text_lower for brand in brands)
    
    def clean_dataset(self, data: List[Dict]) -> List[Dict]:
        """Clean a dataset"""
        cleaned = []
        
        for item in data:
            if 'text' in item:
                processed_text = self.preprocess_text(item['text'])
                if processed_text and len(processed_text) > 2:
                    item['processed_text'] = processed_text
                    cleaned.append(item)
        
        return cleaned