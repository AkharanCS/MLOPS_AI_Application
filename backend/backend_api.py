# Importing Libraries
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Importing necessary functions from other scripts
from predict import prediction
from retrain_model import retrain

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Backend API
app = FastAPI()

@app.post("/predict")
async def predict_email(request: Request):
    try:
        data = await request.json()
        email_texts = data.get("emails")
        if not email_texts or not isinstance(email_texts, list):
            raise HTTPException(status_code=400, detail="Invalid or missing 'emails' list.")
        predictions = prediction(email_texts)
        logger.info("Prediction completed successfully.")
        return {"predictions": predictions}

    except HTTPException as http_exc:
        logger.warning(f"Client error during prediction: {http_exc.detail}")
        raise http_exc
    
    except Exception as e:
        logger.exception("Unexpected error during prediction.")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error during prediction."}
        )
    
@app.post("/train")
async def train(request: Request):
    try:
        data = await request.json()
        feedback_data = data.get("feedback_data")
        feedback_labels = data.get("feedback_labels")
        retrain(feedback_data,feedback_labels)
        logger.info("Model retrained successfully.")
        return {"message": "Model retrained successfully with feedback and different split"}
    except Exception as e:
        logger.exception("Error during model retraining.")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error during training."}
        )

uvicorn.run(app, host='0.0.0.0', port=6000) 