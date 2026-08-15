---
category: project
domain: machine_learning
project_name: Bitcoin Price Prediction
---
# Bitcoin Price Prediction

## Project Name

Bitcoin Price Prediction

## Category

Machine Learning, Financial Time-Series Prediction, Blockchain-Backed Data Storage

## Problem Statement

Predict Bitcoin price movement / price direction using historical Bitcoin data, technical patterns, and machine learning models. The project treats Bitcoin as a volatile digital asset and aims to identify useful predictive patterns rather than guarantee exact future prices.

## Technologies Used

- Python 3.7+
- NumPy
- Pandas
- Scikit-learn
- Statsmodels
- Matplotlib
- pmdarima
- Tkinter
- Web3
- Solidity
- Blockchain smart contract storage
- Windows, Linux, or Mac

## Dataset Information

- Dataset file in repository: `BitcoinPricePrediction/Dataset/Bitcoin-USD.csv`
- Resume reports 476 records.
- Repository workflow loads Bitcoin historical price data.
- Code uses the `Close` column as the target value.
- Code uses an 80/20 train-test split for SVM and Linear Regression workflows.
- ARIMA workflow sorts data by `Date`, sets `Date` as the index, and forecasts 48 test points.
- README states that Bitcoin data is stored and retrieved through blockchain technology.

## Model Architecture

This is a classical machine learning and time-series project, not a neural network project. It includes:

- Feature selection through SPCE / Subspace Learning
- MinMax scaling for selected features and target values
- Linear Regression model
- Support Vector Regression model
- ARIMA model
- Tkinter desktop interface for loading data, preprocessing, running SPCE, and executing each model
- Web3 interaction with a Bitcoin smart contract JSON artifact

## Algorithms Used

- Linear Regression
- Support Vector Machine / Support Vector Regression
- ARIMA
- auto_arima
- SPCE / Subspace Learning
- MinMaxScaler
- StandardScaler
- Mean Squared Error

## Key Features

- Loads Bitcoin data through a blockchain-backed workflow.
- Applies preprocessing to historical Bitcoin data.
- Applies SPCE to reduce feature dimensionality.
- Compares SVM, Linear Regression, and ARIMA predictions.
- Uses Mean Squared Error for model evaluation.
- Displays original and predicted Bitcoin prices.
- Visualizes actual vs predicted price series.
- Includes a Tkinter user interface with actions for data loading, preprocessing, SPCE, SVM, Linear Regression, and ARIMA.

## Results / Metrics

- Resume reports Linear Regression accuracy of 98%.
- Resume reports ARIMA accuracy of 96%.
- Resume reports SVM accuracy of 70%.
- Resume reports SPCE reduced features from 6 to 4.
- Resume reports SPCE improved accuracy by 12 percentage points and reduced dataset noise.
- README states that Logistic Regression consistently produced the most accurate predictions, but the repository code uses `LinearRegression`.

## Challenges Faced

- Bitcoin price movement is volatile and difficult to predict exactly.
- The project addressed irrelevant feature noise using SPCE / Subspace Learning.
- The project included blockchain integration for secure and transparent data handling.

## Learnings

- Historical financial data preprocessing.
- Feature selection with SPCE / Subspace Learning.
- Comparing regression and time-series algorithms.
- Evaluating financial predictions using Mean Squared Error and accuracy metrics.
- Using blockchain smart contract storage/retrieval in a data science workflow.

## GitHub Repository URL

https://github.com/vinay98485/Bitcoin-Price-Prediction
