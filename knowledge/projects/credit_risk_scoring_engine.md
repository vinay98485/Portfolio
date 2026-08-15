---
category: project
domain: machine_learning
project_name: Credit Risk Scoring Engine
---
# End-to-End Credit Risk Scoring Engine

## Project Name

End-to-End Credit Risk Scoring Engine

## Category

Machine Learning, Credit Risk, Financial Technology, Django REST API

## Problem Statement

Predict the probability that a customer will default on a loan and return an approval or denial decision through a web API. The README frames the project around minimizing financial risk from false negatives, such as approving bad loans.

## Technologies Used

- Python
- Pandas
- Scikit-learn
- XGBoost
- Joblib
- Django
- Vanilla HTML/JavaScript

## Dataset Information

- Specific source dataset name is not specified in available sources.
- The API expects financial and credit profile fields including age, income, employment length, loan amount, interest rate, loan percent income, credit history length, home ownership fields, loan intent fields, loan grade fields, and prior default flag.
- README states missing data is handled through median imputation and categorical variables are one-hot encoded.

## Model Architecture

- Data engineering layer using Pandas and Scikit-learn.
- XGBoost Classifier for credit default prediction.
- Serialized model artifact: `api/xgboost_credit_risk_model.pkl`
- Serialized scaler artifact: `api/credit_risk_scaler.pkl`
- Django backend with `/api/predict/` endpoint.
- Frontend interface in HTML/JavaScript.
- API accepts JSON, reindexes to expected feature columns, scales the input, predicts class, predicts default probability, and returns a risk score plus approval/denial decision.

## Algorithms Used

- XGBoost Classifier
- Median imputation
- One-hot encoding
- Standard scaling
- Precision, Recall, and ROC-AUC focused evaluation

## Key Features

- End-to-end ML pipeline and REST API.
- Real-time JSON prediction endpoint.
- Risk score returned as probability percentage.
- Approval/denial decision logic.
- Feature importance analysis.
- Production-style serialization with Joblib.
- Lightweight frontend UI.

## Results / Metrics

- README states the model is optimized for Precision, Recall, and ROC-AUC.
- README identifies strongest default predictors as `loan_percent_income` and `loan_grade` C and D.
- Example API response returns risk score `38.49` and decision `APPROVED`.
- Exact Precision, Recall, ROC-AUC, or test accuracy values are not specified in available sources.

## Challenges Faced

- Standard accuracy can be misleading on highly imbalanced financial datasets.
- The project addresses false-negative risk by focusing on Precision, Recall, and ROC-AUC instead of simple accuracy.
- The project bridges raw financial data and production-ready software by serving the trained model through Django.

## Learnings

- Building a credit risk model with XGBoost.
- Handling imbalanced financial classification problems.
- Using feature importance to interpret credit risk drivers.
- Serializing ML models and scalers with Joblib.
- Serving predictions through a Django REST-style endpoint.

## GitHub Repository URL

https://github.com/vinay98485/credit-risk-engine
