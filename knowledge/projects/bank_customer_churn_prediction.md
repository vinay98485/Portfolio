---
category: project
domain: deep_learning
project_name: Bank Customer Churn Prediction
---
# Bank Customer Churn Prediction

## Project Name

Bank Customer Churn Prediction using Artificial Neural Network (ANN)

## Category

Deep Learning, Customer Churn Prediction, Banking Analytics, Streamlit Deployment

## Problem Statement

Predict whether a bank customer is likely to leave the bank. The project is framed around helping banks improve retention, reduce revenue loss, create targeted marketing campaigns, and improve customer satisfaction.

## Technologies Used

- Python
- TensorFlow
- Keras
- NumPy
- Pandas
- Scikit-learn
- Matplotlib
- Streamlit
- Joblib

## Dataset Information

- Dataset file: `Churn_Modelling.csv`
- Total records: 10,000
- Target variable: `Exited`
- Target labels: `0` means customer stayed; `1` means customer left.
- Preprocessing removes `RowNumber`, `CustomerId`, and `Surname`.
- Gender is label encoded.
- Geography is one-hot encoded with `drop="first"` and `handle_unknown="ignore"`.
- Data is split into train and test sets with `test_size=0.2` and `random_state=42`.
- Features are scaled using `StandardScaler`.

## Model Architecture

- Input layer with 11 features
- Dense layer with 64 units and ReLU activation
- Dense layer with 32 units and ReLU activation
- Dense output layer with 1 unit and Sigmoid activation
- Optimizer: Adam
- Loss function: Binary crossentropy
- Metric: Accuracy

## Algorithms Used

- Artificial Neural Network
- Binary classification
- Label encoding
- One-hot encoding
- Standard scaling
- EarlyStopping

## Key Features

- End-to-end deep learning pipeline
- Data preprocessing
- Feature encoding
- Feature scaling
- ANN model training and evaluation
- EarlyStopping to reduce overfitting
- Saved model and preprocessing artifacts
- Streamlit live prediction app
- Accuracy, loss, confusion matrix, and ROC curve evaluation visuals

## Results / Metrics

- Training accuracy: 87.30%
- Validation accuracy: 85.50%
- Test accuracy: 85.95%
- EarlyStopping: Enabled

## Challenges Faced

- Preventing overfitting during ANN training.
- Preparing categorical and numerical customer data for deep learning through encoding and scaling.

## Learnings

- Building Artificial Neural Networks using TensorFlow/Keras.
- Data preprocessing for deep learning.
- Feature engineering.
- Binary classification using Sigmoid activation.
- Binary Crossentropy loss.
- Model training and evaluation.
- EarlyStopping callback.
- Saving and loading trained models.
- Deploying deep learning models with Streamlit.
- Organizing a machine learning project using a modular structure.

## GitHub Repository URL

https://github.com/vinay98485/bank-churn-prediction

## Live Demo

https://bank-churn-prediction-vinay-app.streamlit.app/
