---
category: project
domain: machine_learning
project_name: Enterprise eCommerce AI Retention Engine
---
# Enterprise E-Commerce AI and Retention Engine

## Project Name

Enterprise E-Commerce AI and Retention Engine

## Category

Machine Learning, Customer Retention, Customer Segmentation, Churn Prediction, CLTV Forecasting, Streamlit Dashboard

## Problem Statement

Traditional analytics often identify customers after they have already left. This engine is designed to proactively identify customers with behavioral signs of churn and help marketing teams intervene before customers are lost.

## Technologies Used

- Python 3.9+
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Streamlit
- Plotly Express
- GridSearchCV

## Dataset Information

- Dataset: UCI Online Retail / Kaggle E-Commerce Data.
- README states the dataset contains more than 540,000 raw retail transactions.
- Repository contains `data/ecommerce_data.csv`.
- README says the dataset should be saved as `ecommerce_data.csv` inside the `data/` folder.
- Data pipeline uses `unicode_escape` encoding.
- Rows without `CustomerID` are dropped.
- Returns and zero-dollar items are filtered out by requiring positive `Quantity` and positive `UnitPrice`.
- `Total_Price` is calculated as `Quantity * UnitPrice`.
- Transaction rows are aggregated into approximately 4,300 unique customer profiles.
- RFM fields include `Recency_Days`, `Frequency_Orders`, `CLTV`, and `Total_Items`.
- `Average_Order_Value` is calculated as `CLTV / Frequency_Orders`.
- Churn is defined as `Recency_Days > 90`.

## Model Architecture

- Phase 0: Data ingestion, cleaning, and RFM engineering.
- Phase 1: K-Means clustering for unsupervised customer segmentation.
- Phase 2: Random Forest Classifier for churn risk prediction.
- Phase 3: XGBoost Regressor with GridSearchCV for CLTV / revenue forecasting.
- Streamlit dashboard with tabs/screenshots for clustering, churn roster, and revenue forecast.

## Algorithms Used

- K-Means clustering
- Random Forest Classifier
- XGBoost Regressor
- GridSearchCV
- RFM engineering
- Train-test split
- R2 score
- Mean Absolute Error
- Accuracy score

## Key Features

- Full-stack modular ML engine.
- Processes large-scale retail transaction data.
- Aggregates transaction history into customer profiles.
- Segments customers into business personas such as VIP Whales and Core Shoppers.
- Predicts churn risk proactively.
- Forecasts customer lifetime value.
- Uses explicit feature isolation to avoid churn target leakage.
- Includes Streamlit dashboard visuals for clustering, churn, and revenue.

## Results / Metrics

- Processes more than 540,000 raw retail transactions.
- Aggregates transactions into approximately 4,300 customer profiles.
- README reports that the churn model initially reached 100% accuracy because of data leakage through `Recency_Days`.
- After isolating features, the churn model produced a more honest proactive accuracy of approximately 70%.
- Regression metrics used in code: R2 score and Mean Absolute Error.
- Exact R2 and MAE values are not specified in available sources.

## Challenges Faced

- Data leakage in churn prediction: initial models reached 100% accuracy because `Recency_Days` acted as a proxy for the 90-day churn definition.
- The fix was explicit feature selection using only `Frequency_Orders`, `Total_Items`, `Average_Order_Value`, and `Behavioral_Cluster` for churn prediction.
- Handling large transaction data and converting it into customer-level profiles.

## Learnings

- Building a multi-phase machine learning system.
- RFM engineering from transaction-level data.
- Combining unsupervised segmentation, supervised classification, and supervised regression.
- Detecting and fixing data leakage.
- Using GridSearchCV to tune XGBoost regression.
- Building a Streamlit command center for business-facing ML insights.

## GitHub Repository URL

https://github.com/vinay98485/enterprise-ml-engine

## Live Demo

https://enterprise-ml-engine-vinay-app.streamlit.app/
