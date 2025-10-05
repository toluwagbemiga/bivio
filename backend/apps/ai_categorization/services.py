# backend/apps/ai_categorization/services.py
"""
AI categorization service for intelligent transaction classification
Handles Nigerian product names, local languages, and context-aware predictions
"""

import re
import json
import time
import requests
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.core.cache import cache
from apps.inventory.models import ProductCategory
from .models import CategoryPrediction, TrainingData


class AICategorizationService:
    """
    Service for AI-powered category prediction
    """
    
    def __init__(self):
        self.ai_service_url = settings.AI_SERVICE_URL
        self.model_version = "v1.0"
        
        # Nigerian product mappings for common items
        self.nigerian_product_map = {
            # Food & Beverages
            'indomie': 'food_beverages', 'milo': 'food_beverages', 'peak_milk': 'food_beverages',
            'gala': 'food_beverages', 'meat_pie': 'food_beverages', 'plantain': 'food_beverages',
            'beans': 'food_beverages', 'garri': 'food_beverages', 'rice': 'food_beverages',
            'yam': 'food_beverages', 'bread': 'food_beverages', 'egg': 'food_beverages',
            'chicken': 'food_beverages', 'fish': 'food_beverages', 'palm_oil': 'food_beverages',
            'groundnut_oil': 'food_beverages', 'tomato': 'food_beverages', 'onion': 'food_beverages',
            'pepper': 'food_beverages', 'maggi': 'food_beverages', 'knorr': 'food_beverages',
            'coke': 'food_beverages', 'pepsi': 'food_beverages', 'sprite': 'food_beverages',
            'fanta': 'food_beverages', 'malt': 'food_beverages', 'water': 'food_beverages',
            
            # Electronics
            'phone': 'electronics', 'charger': 'electronics', 'battery': 'electronics',
            'memory_card': 'electronics', 'earpiece': 'electronics', 'speaker': 'electronics',
            'torch': 'electronics', 'radio': 'electronics', 'tv': 'electronics',
            'fan': 'electronics', 'iron': 'electronics', 'kettle': 'electronics',
            
            # Household Items
            'detergent': 'household', 'soap': 'household', 'sponge': 'household',
            'broom': 'household', 'bucket': 'household', 'plate': 'household',
            'spoon': 'household', 'cup': 'household', 'candle': 'household',
            'matchbox': 'household', 'kerosene': 'household', 'gas': 'household',
            
            # Cosmetics & Personal Care
            'cream': 'cosmetics', 'lotion': 'cosmetics', 'powder': 'cosmetics',
            'perfume': 'cosmetics', 'deodorant': 'cosmetics', 'toothpaste': 'cosmetics',
            'toothbrush': 'cosmetics', 'shampoo': 'cosmetics', 'hair_cream': 'cosmetics',
            'pomade': 'cosmetics', 'vaseline': 'cosmetics', 'bathing_soap': 'cosmetics',
            
            # Airtime & Data
            'airtime': 'airtime_data', 'recharge_card': 'airtime_data', 'data': 'airtime_data',
            'mtn': 'airtime_data', 'glo': 'airtime_data', 'airtel': 'airtime_data',
            '9mobile': 'airtime_data', 'etisalat': 'airtime_data',
            
            # Clothing
            'shirt': 'clothing', 'trouser': 'clothing', 'dress': 'clothing',
            'shoe': 'clothing', 'sandal': 'clothing', 'cap': 'clothing',
            'wrapper': 'clothing', 'ankara': 'clothing', 'lace': 'clothing',
            
            # Stationery
            'pen': 'stationery', 'pencil': 'stationery', 'book': 'stationery',
            'exercise_book': 'stationery', 'ruler': 'stationery', 'eraser': 'stationery',
            'paper': 'stationery', 'envelope': 'stationery',
        }
        
        # Pidgin and local language mappings
        self.local_language_map = {
            # Pidgin English
            'akara': 'food_beverages',  # Bean cake
            'suya': 'food_beverages',   # Spiced meat
            'boli': 'food_beverages',   # Roasted plantain
            'pap': 'food_beverages',    # Corn pudding
            'zobo': 'food_beverages',   # Hibiscus drink
            'kunu': 'food_beverages',   # Millet drink
            'fura': 'food_beverages',   # Millet balls
            'kilishi': 'food_beverages', # Dried meat
            'chin_chin': 'food_beverages',
            'puff_puff': 'food_beverages',
            
            # Hausa
            'dambu': 'food_beverages',  # Dried meat floss
            'tsire': 'food_beverages',  # Suya
            'masa': 'food_beverages',   # Rice cake
            
            # Yoruba
            'ewa': 'food_beverages',    # Beans
            'obe': 'food_beverages',    # Soup/stew
            'amala': 'food_beverages',  # Yam flour
            'ewedu': 'food_beverages',  # Jute leaves soup
            'gbegiri': 'food_beverages', # Bean soup
            'ogi': 'food_beverages',    # Corn pudding
            
            # Igbo
            'ugali': 'food_beverages',  # Corn meal
            'ofe': 'food_beverages',    # Soup
            'ji': 'food_beverages',     # Yam
            'ede': 'food_beverages',    # Cocoyam
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for better categorization
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Handle common variations and typos
        replacements = {
            'recharge': 'airtime',
            'phone card': 'airtime',
            'call card': 'airtime',
            'credit': 'airtime',
            'handset': 'phone',
            'mobile': 'phone',
            'cell phone': 'phone',
            'beverage': 'drink',
            'soft drink': 'drink',
            'mineral': 'water',
            'pure water': 'water',
            'sachet water': 'water',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def extract_features(self, text: str, context: Dict = None) -> Dict:
        """
        Extract features from text for ML model
        """
        preprocessed = self.preprocess_text(text)
        words = preprocessed.split()
        
        features = {
            'text': preprocessed,
            'word_count': len(words),
            'char_count': len(preprocessed),
            'has_numbers': any(char.isdigit() for char in preprocessed),
            'contains_naira': '₦' in text or 'naira' in text.lower(),
            'contains_brand': self._contains_known_brand(preprocessed),
            'language_hints': self._detect_language_hints(preprocessed),
        }
        
        # Add context features if available
        if context:
            features.update({
                'user_history': context.get('user_history', []),
                'time_of_day': context.get('time_of_day'),
                'location': context.get('location'),
                'previous_categories': context.get('previous_categories', []),
            })
        
        return features
    
    def _contains_known_brand(self, text: str) -> bool:
        """Check if text contains known Nigerian brands"""
        brands = [
            'mtn', 'glo', 'airtel', '9mobile', 'etisalat',
            'indomie', 'maggi', 'knorr', 'milo', 'peak',
            'coca_cola', 'pepsi', 'sprite', 'fanta',
            'samsung', 'tecno', 'infinix', 'itel'
        ]
        return any(brand in text for brand in brands)
    
    def _detect_language_hints(self, text: str) -> List[str]:
        """Detect language hints in the text"""
        hints = []
        
        # Check for local language words
        for word, category in self.local_language_map.items():
            if word in text:
                hints.append(f'local_{category}')
        
        # Check for pidgin patterns
        pidgin_patterns = ['wetin', 'how much', 'how far', 'no wahala', 'sha', 'abi']
        if any(pattern in text for pattern in pidgin_patterns):
            hints.append('pidgin')
        
        return hints
    
    def get_category_from_mapping(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Get category from predefined mappings with confidence score
        """
        preprocessed = self.preprocess_text(text)
        words = preprocessed.split()
        
        # Check exact matches first
        for word in words:
            if word in self.nigerian_product_map:
                category_type = self.nigerian_product_map[word]
                try:
                    category = ProductCategory.objects.get(category_type=category_type)
                    return (category, 0.95)  # High confidence for exact matches
                except ProductCategory.DoesNotExist:
                    continue
            
            if word in self.local_language_map:
                category_type = self.local_language_map[word]
                try:
                    category = ProductCategory.objects.get(category_type=category_type)
                    return (category, 0.90)  # Slightly lower for local language
                except ProductCategory.DoesNotExist:
                    continue
        
        # Check partial matches
        for product, category_type in self.nigerian_product_map.items():
            if product in preprocessed or any(product in word for word in words):
                try:
                    category = ProductCategory.objects.get(category_type=category_type)
                    return (category, 0.75)  # Lower confidence for partial matches
                except ProductCategory.DoesNotExist:
                    continue
        
        return None
    
    def call_ml_service(self, features: Dict) -> Optional[Dict]:
        """
        Call the ML service for category prediction
        """
        try:
            response = requests.post(
                f"{self.ai_service_url}/ai/categorize",
                json={'features': features},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except requests.RequestException:
            # Fallback if AI service is unavailable
            return None
    
    def predict_category(self, text: str, context: Dict = None, user=None) -> Dict:
        """
        Main method to predict product category
        """
        start_time = time.time()
        
        if not text or len(text.strip()) < 2:
            return {
                'error': 'Input text is too short',
                'confidence': 0.0
            }
        
        # Check cache first
        cache_key = f"category_prediction_{hash(text + str(context))}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Try predefined mappings first (fastest and most accurate for common items)
        mapping_result = self.get_category_from_mapping(text)
        if mapping_result:
            category, confidence = mapping_result
            result = self._format_prediction_result(
                category, confidence, text, [], 'mapping', 
                time.time() - start_time, user
            )
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
            return result
        
        # Extract features for ML model
        features = self.extract_features(text, context)
        
        # Try ML service
        ml_result = self.call_ml_service(features)
        if ml_result and ml_result.get('category'):
            try:
                category = ProductCategory.objects.get(id=ml_result['category'])
                confidence = ml_result.get('confidence', 0.5)
                alternatives = ml_result.get('alternatives', [])
                
                result = self._format_prediction_result(
                    category, confidence, text, alternatives, 'ml_model',
                    time.time() - start_time, user
                )
                cache.set(cache_key, result, timeout=1800)  # Cache for 30 minutes
                return result
                
            except ProductCategory.DoesNotExist:
                pass
        
        # Fallback: use similarity matching
        similarity_result = self.find_similar_category(text, user)
        if similarity_result:
            category, confidence = similarity_result
            result = self._format_prediction_result(
                category, confidence, text, [], 'similarity',
                time.time() - start_time, user
            )
            cache.set(cache_key, result, timeout=1800)
            return result
        
        # Last resort: return most common category
        default_category = ProductCategory.objects.filter(
            category_type='other', is_active=True
        ).first()
        
        if default_category:
            result = self._format_prediction_result(
                default_category, 0.3, text, [], 'default',
                time.time() - start_time, user
            )
            return result
        
        return {
            'error': 'No suitable category found',
            'confidence': 0.0,
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }
    
    def find_similar_category(self, text: str, user=None) -> Optional[Tuple[ProductCategory, float]]:
        """
        Find similar category using training data and user history
        """
        preprocessed = self.preprocess_text(text)
        words = set(preprocessed.split())
        
        # Check user's previous categorizations
        if user:
            user_predictions = CategoryPrediction.objects.filter(
                user=user,
                status__in=['accepted', 'auto_applied']
            ).order_by('-created_at')[:100]
            
            for prediction in user_predictions:
                pred_words = set(self.preprocess_text(prediction.input_text).split())
                similarity = len(words & pred_words) / len(words | pred_words) if words | pred_words else 0
                
                if similarity > 0.5:  # 50% word similarity
                    confidence = min(similarity * 0.8, 0.8)  # Max 80% confidence
                    return (prediction.actual_category or prediction.predicted_category, confidence)
        
        # Check global training data
        training_data = TrainingData.objects.filter(
            is_validated=True,
            status='validated'
        ).order_by('-validation_score')[:200]
        
        best_match = None
        best_similarity = 0.0
        
        for data in training_data:
            data_words = set(self.preprocess_text(data.text_input).split())
            similarity = len(words & data_words) / len(words | data_words) if words | data_words else 0
            
            if similarity > best_similarity and similarity > 0.3:
                best_similarity = similarity
                best_match = (data.category, similarity * 0.7)  # Max 70% confidence
        
        return best_match
    
    def _format_prediction_result(self, category: ProductCategory, confidence: float, 
                                input_text: str, alternatives: List, method: str,
                                processing_time: float, user=None) -> Dict:
        """
        Format the prediction result and optionally save to database
        """
        result = {
            'predicted_category': {
                'id': str(category.id),
                'name': category.name,
                'category_type': category.category_type
            },
            'confidence': round(confidence, 3),
            'alternatives': alternatives,
            'method': method,
            'processing_time_ms': int(processing_time * 1000),
            'input_text': input_text,
            'model_version': self.model_version
        }
        
        # Save prediction to database for learning
        if user and confidence > 0.5:  # Only save confident predictions
            try:
                prediction = CategoryPrediction.objects.create(
                    user=user,
                    input_text=input_text,
                    preprocessed_text=self.preprocess_text(input_text),
                    predicted_category=category,
                    confidence_score=confidence,
                    alternative_predictions=alternatives,
                    model_version=self.model_version,
                    processing_time_ms=int(processing_time * 1000),
                    context_data={'method': method},
                    status='auto_applied' if confidence > 0.8 else 'pending'
                )
                result['prediction_id'] = str(prediction.id)
                
            except Exception:
                pass  # Don't fail prediction if database save fails
        
        return result
    
    def learn_from_feedback(self, prediction_id: str, actual_category_id: str, 
                          user_feedback: str = "") -> bool:
        """
        Learn from user feedback to improve future predictions
        """
        try:
            prediction = CategoryPrediction.objects.get(id=prediction_id)
            actual_category = ProductCategory.objects.get(id=actual_category_id)
            
            # Update prediction with user feedback
            prediction.actual_category = actual_category
            prediction.status = 'accepted' if actual_category == prediction.predicted_category else 'rejected'
            prediction.user_feedback = user_feedback
            prediction.save()
            
            # Create training data from this feedback
            TrainingData.objects.create(
                text_input=prediction.input_text,
                processed_text=prediction.preprocessed_text,
                category=actual_category,
                source='feedback',
                is_validated=True,
                validation_score=1.0 if prediction.status == 'accepted' else 0.5,
                contributed_by=prediction.user
            )
            
            # Invalidate related cache
            cache_keys_pattern = f"category_prediction_*{hash(prediction.input_text)}*"
            # Note: In production, use Redis pattern deletion
            
            return True
            
        except (CategoryPrediction.DoesNotExist, ProductCategory.DoesNotExist):
            return False
    
    def batch_categorize(self, texts: List[str], user=None) -> List[Dict]:
        """
        Categorize multiple texts at once (more efficient)
        """
        results = []
        
        # Group similar texts to reduce API calls
        unique_texts = list(set(texts))
        prediction_cache = {}
        
        for text in unique_texts:
            result = self.predict_category(text, user=user)
            prediction_cache[text] = result
        
        # Map results back to original order
        for text in texts:
            results.append(prediction_cache[text])
        
        return results
    
    def get_category_suggestions(self, partial_text: str, limit: int = 5) -> List[Dict]:
        """
        Get category suggestions as user types (autocomplete)
        """
        if len(partial_text) < 2:
            return []
        
        preprocessed = self.preprocess_text(partial_text)
        suggestions = []
        
        # Check predefined mappings
        for product, category_type in self.nigerian_product_map.items():
            if product.startswith(preprocessed) or preprocessed in product:
                try:
                    category = ProductCategory.objects.get(category_type=category_type)
                    suggestions.append({
                        'text': product,
                        'category': {
                            'id': str(category.id),
                            'name': category.name,
                            'category_type': category.category_type
                        },
                        'confidence': 0.9
                    })
                except ProductCategory.DoesNotExist:
                    continue
        
        # Check local language mappings
        for word, category_type in self.local_language_map.items():
            if word.startswith(preprocessed) or preprocessed in word:
                try:
                    category = ProductCategory.objects.get(category_type=category_type)
                    suggestions.append({
                        'text': word,
                        'category': {
                            'id': str(category.id),
                            'name': category.name,
                            'category_type': category.category_type
                        },
                        'confidence': 0.85
                    })
                except ProductCategory.DoesNotExist:
                    continue
        
        # Sort by confidence and limit results
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:limit]
    
    def analyze_user_patterns(self, user) -> Dict:
        """
        Analyze user's categorization patterns for insights
        """
        predictions = CategoryPrediction.objects.filter(user=user).order_by('-created_at')
        
        if not predictions.exists():
            return {'message': 'No data available for analysis'}
        
        # Calculate accuracy
        correct_predictions = predictions.filter(
            predicted_category=models.F('actual_category')
        ).count()
        total_with_feedback = predictions.filter(actual_category__isnull=False).count()
        accuracy = (correct_predictions / total_with_feedback * 100) if total_with_feedback > 0 else 0
        
        # Most common categories
        category_counts = predictions.values(
            'predicted_category__name'
        ).annotate(count=models.Count('id')).order_by('-count')[:5]
        
        # Confidence distribution
        high_confidence = predictions.filter(confidence_score__gte=0.8).count()
        medium_confidence = predictions.filter(
            confidence_score__gte=0.5, confidence_score__lt=0.8
        ).count()
        low_confidence = predictions.filter(confidence_score__lt=0.5).count()
        
        return {
            'total_predictions': predictions.count(),
            'accuracy_percentage': round(accuracy, 1),
            'most_common_categories': list(category_counts),
            'confidence_distribution': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'avg_processing_time_ms': predictions.aggregate(
                avg_time=models.Avg('processing_time_ms')
            )['avg_time'] or 0,
            'feedback_rate': round(total_with_feedback / predictions.count() * 100, 1) if predictions.count() > 0 else 0
        }


