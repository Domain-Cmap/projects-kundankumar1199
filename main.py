from flask import Flask, request, render_template
import pandas as pd
import joblib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load model with proper error handling
def load_model(model_path):
    try:
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

# Load model at startup
MODEL_PATH = 'pipe8_3_model.pkl'
model = load_model(MODEL_PATH)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    error = None
    
    if request.method == 'POST':
        try:
            if model is None:
                raise Exception("Model not loaded")

            # Get and validate form data
            sample = pd.DataFrame({
                'Age': [float(request.form['age'])],
                'Experience': [float(request.form['experience'])],
                'Income': [float(request.form['income'])/12],  # Converting annual to monthly
                'Family': [float(request.form['family'])],
                'CCAvg': [float(request.form['ccavg'])],
                'Education': [float(request.form['education'])],
                'Mortgage': [float(request.form['mortgage'])],
                'Securities Account': [float(request.form['securities'])],
                'CD Account': [float(request.form['cd'])],
                'Online': [float(request.form['online'])],
                'CreditCard': [float(request.form['creditcard'])]
            })

            # Validate input ranges
            if not (1 <= float(request.form['education']) <= 3):
                raise ValueError("Education must be between 1 and 3")
            if not (0 <= float(request.form['age']) <= 100):
                raise ValueError("Age must be between 0 and 100")

            # Make prediction
            prediction = model.predict(sample)[0]
            logger.info(f"Prediction made successfully: {prediction}")

        except ValueError as ve:
            error = str(ve)
            logger.error(f"Validation error: {error}")
        except Exception as e:
            error = f"An error occurred: {str(e)}"
            logger.error(f"Prediction error: {error}")
    
    return render_template('index.html', prediction=prediction, error=error)

if __name__ == '__main__':
    app.run(debug=True)