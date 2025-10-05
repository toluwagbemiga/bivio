# ai_services/api/main.py
"""
FastAPI AI Service for POS Financial Management App
Handles ML-powered transaction categorization for Nigerian market
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uvicorn
import os
import json
import logging
from datetime import datetime

from api.routes.categorization import router as categorization_router
from api.routes.predictions import router as predictions_router
from api.services.ml_service import MLService
from api.services.preprocessing_service import PreprocessingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="POS AI Services",
    description="AI-powered transaction categorization for Nigerian POS systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ml_service = MLService()
preprocessing_service = PreprocessingService()

# Request/Response Models
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

class CategorizationRequest(BaseModel):
    text_input: str = Field(..., min_length=1, max_length=500, description="Product text to categorize")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for categorization")
    user_id: Optional[str] = Field(default=None, description="User ID for personalized predictions")
    language: Optional[str] = Field(default="en", description="Language hint (en, ha, ig, yo, pidgin)")

class CategorizationResponse(BaseModel):
    predicted_category: Dict[str, Any]
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternatives: List[Dict[str, Any]] = Field(default=[])
    method: str
    processing_time_ms: int
    model_version: str

class BatchCategorizationRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class TrainingDataRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., min_items=1)
    model_type: str = Field(default="category_classifier")

class ModelTrainingRequest(BaseModel):
    model_type: str = Field(default="category_classifier")
    hyperparameters: Optional[Dict[str, Any]] = None
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Health check endpoint
@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        services={
            "ml_service": "active",
            "preprocessing": "active",
            "model_loaded": str(ml_service.is_model_loaded())
        }
    )

# Main categorization endpoint
@app.post("/ai/categorize", response_model=CategorizationResponse)
async def categorize_text(request: CategorizationRequest):
    """
    Categorize product text using AI models
    """
    try:
        start_time = datetime.now()
        
        # Validate input
        if not request.text_input or len(request.text_input.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Text input must be at least 2 characters long"
            )
        
        # Preprocess text
        processed_text = preprocessing_service.preprocess_text(request.text_input)
        features = preprocessing_service.extract_features(
            processed_text, 
            context=request.context,
            language=request.language
        )
        
        # Get prediction
        prediction = ml_service.predict_category(
            features, 
            user_id=request.user_id,
            context=request.context
        )
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return CategorizationResponse(
            predicted_category=prediction["category"],
            confidence=prediction["confidence"],
            alternatives=prediction.get("alternatives", []),
            method=prediction.get("method", "ml_model"),
            processing_time_ms=processing_time,
            model_version=prediction.get("model_version", "v1.0")
        )
        
    except Exception as e:
        logger.error(f"Categorization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

# Batch categorization endpoint
@app.post("/ai/batch-categorize")
async def batch_categorize(request: BatchCategorizationRequest):
    """
    Categorize multiple texts at once
    """
    try:
        start_time = datetime.now()
        results = []
        
        for text in request.texts:
            if len(text.strip()) < 2:
                results.append({
                    "text": text,
                    "error": "Text too short",
                    "confidence": 0.0
                })
                continue
            
            # Preprocess and predict
            processed_text = preprocessing_service.preprocess_text(text)
            features = preprocessing_service.extract_features(processed_text, request.context)
            prediction = ml_service.predict_category(features, request.user_id, request.context)
            
            results.append({
                "text": text,
                "predicted_category": prediction["category"],
                "confidence": prediction["confidence"],
                "method": prediction.get("method", "ml_model")
            })
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "results": results,
            "total_processed": len(request.texts),
            "processing_time_ms": processing_time
        }
        
    except Exception as e:
        logger.error(f"Batch categorization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch categorization failed: {str(e)}")

# Export training data endpoint
@app.post("/ai/export-training-data")
async def export_training_data(request: TrainingDataRequest, background_tasks: BackgroundTasks):
    """
    Export training data for model training
    """
    try:
        # Validate data format
        for item in request.data:
            if not all(key in item for key in ["text", "category"]):
                raise HTTPException(
                    status_code=400,
                    detail="Each training item must have 'text' and 'category' fields"
                )
        
        # Save training data
        training_file = f"data/training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(training_file), exist_ok=True)
        
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(request.data, f, ensure_ascii=False, indent=2)
        
        # Process data in background
        background_tasks.add_task(
            ml_service.process_training_data, 
            request.data, 
            request.model_type
        )
        
        return {
            "message": "Training data exported successfully",
            "data_points": len(request.data),
            "file": training_file,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Train model endpoint
@app.post("/ai/train-model")
async def train_model(request: ModelTrainingRequest, background_tasks: BackgroundTasks):
    """
    Train the categorization model
    """
    try:
        if not ml_service.has_training_data():
            raise HTTPException(
                status_code=400,
                detail="No training data available. Please export data first."
            )
        
        # Start training in background
        background_tasks.add_task(
            ml_service.train_model,
            model_type=request.model_type,
            hyperparameters=request.hyperparameters,
            validation_split=request.validation_split
        )
        
        return {
            "message": "Model training started",
            "model_type": request.model_type,
            "status": "training",
            "estimated_time_minutes": 5  # Estimate based on data size
        }
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

# Model performance endpoint
@app.get("/ai/model-performance")
async def get_model_performance():
    """
    Get current model performance metrics
    """
    try:
        performance = ml_service.get_model_performance()
        return performance
        
    except Exception as e:
        logger.error(f"Performance check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance check failed: {str(e)}")

# Category suggestions endpoint (autocomplete)
@app.get("/ai/suggestions")
async def get_category_suggestions(
    text: str,
    limit: int = 5,
    user_id: Optional[str] = None
):
    """
    Get category suggestions as user types (autocomplete)
    """
    try:
        if len(text.strip()) < 2:
            return {"suggestions": []}
        
        suggestions = ml_service.get_category_suggestions(text, limit, user_id)
        
        return {
            "suggestions": suggestions,
            "query": text
        }
        
    except Exception as e:
        logger.error(f"Suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")

# Model reload endpoint
@app.post("/ai/reload-model")
async def reload_model():
    """
    Reload the ML model (useful after training)
    """
    try:
        success = ml_service.reload_model()
        
        if success:
            return {
                "message": "Model reloaded successfully",
                "model_version": ml_service.get_model_version(),
                "status": "active"
            }
        else:
            raise HTTPException(status_code=500, detail="Model reload failed")
            
    except Exception as e:
        logger.error(f"Model reload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model reload failed: {str(e)}")

# Nigerian market insights endpoint
@app.get("/ai/market-insights")
async def get_market_insights(user_id: Optional[str] = None):
    """
    Get insights about Nigerian market categorization patterns
    """
    try:
        insights = ml_service.get_nigerian_market_insights(user_id)
        return insights
        
    except Exception as e:
        logger.error(f"Market insights error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Market insights failed: {str(e)}")

# Include additional routers
app.include_router(categorization_router, prefix="/api/v1", tags=["Categorization"])
app.include_router(predictions_router, prefix="/api/v1", tags=["Predictions"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize services on startup
    """
    logger.info("Starting POS AI Services...")
    
    # Initialize ML service
    try:
        ml_service.initialize()
        logger.info("ML Service initialized successfully")
    except Exception as e:
        logger.error(f"ML Service initialization failed: {str(e)}")
    
    # Initialize preprocessing service
    try:
        preprocessing_service.initialize()
        logger.info("Preprocessing Service initialized successfully")
    except Exception as e:
        logger.error(f"Preprocessing Service initialization failed: {str(e)}")
    
    logger.info("POS AI Services startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    logger.info("Shutting down POS AI Services...")
    
    # Cleanup ML service
    try:
        ml_service.cleanup()
        logger.info("ML Service cleanup complete")
    except Exception as e:
        logger.error(f"ML Service cleanup error: {str(e)}")
    
    logger.info("POS AI Services shutdown complete")

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )