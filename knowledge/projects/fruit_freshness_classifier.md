---
category: project
domain: deep_learning
project_name: Fruit Freshness Classifier
---
# Fruit Freshness Classifier

## Project Name

Fruit Freshness Classifier

## Category

Deep Learning, Computer Vision, Image Classification, Streamlit Deployment

## Problem Statement

Automate freshness detection for fruits and vegetables using deep learning. The project addresses the problem that manual inspection can be time-consuming and inconsistent, with potential use in food quality inspection, agriculture, inventory management, and smart retail systems.

## Technologies Used

- Python 3.9
- TensorFlow
- Keras
- NumPy
- Matplotlib
- Scikit-learn
- Streamlit
- Pillow / PIL

## Dataset Information

- Dataset source: Kaggle Fresh and Stale Classification dataset.
- Dataset URL: https://www.kaggle.com/datasets/swoyam2609/fresh-and-stale-classification
- Model trained on 14 classes:
  - Fresh Apples
  - Rotten Apples
  - Fresh Banana
  - Rotten Banana
  - Fresh Cucumber
  - Rotten Cucumber
  - Fresh Okra
  - Rotten Okra
  - Fresh Oranges
  - Rotten Oranges
  - Fresh Potato
  - Rotten Potato
  - Fresh Tomato
  - Rotten Tomato

## Model Architecture

- Input shape: 128 x 128 x 3
- Rescaling layer with scale `1./255`
- Convolutional block with 32 filters
- Convolutional block with 64 filters
- Convolutional block with 128 filters
- Convolutional block with 256 filters
- Each convolutional block uses Conv2D, BatchNormalization, ReLU activation, and MaxPool2D.
- Flatten layer
- Dense block with 128 units, BatchNormalization, ReLU, and Dropout
- Dense block with 64 units, BatchNormalization, ReLU, and Dropout
- Output Dense layer with 14 classes and Softmax activation
- Dropout: 0.3
- Optimizer: Adam
- Loss: sparse categorical crossentropy
- Training epochs configured: 50

## Algorithms Used

- Convolutional Neural Network
- Multiclass image classification
- Data augmentation
- Batch normalization
- Dropout regularization
- EarlyStopping
- ModelCheckpoint
- ReduceLROnPlateau

## Key Features

- Upload an image.
- Predict freshness status.
- Display confidence scores.
- Show top-3 predicted classes.
- Instant results through a Streamlit web interface.
- Saved Keras model artifact.
- Evaluation screenshots for confusion matrix, normalized confusion matrix, and sample predictions.

## Results / Metrics

- Test accuracy: 99.01%
- Test loss: 0.0304

## Challenges Faced

- Automating image-based freshness inspection across multiple fruit and vegetable categories.
- Managing overfitting risk using data augmentation, batch normalization, dropout, EarlyStopping, ModelCheckpoint, and learning-rate reduction.

## Learnings

- Building CNN image classifiers with TensorFlow/Keras.
- Preparing image datasets for multiclass classification.
- Applying regularization and training callbacks.
- Evaluating image classifiers with confusion matrices and sample predictions.
- Deploying a computer vision model through Streamlit.

## GitHub Repository URL

https://github.com/vinay98485/fruit-freshness-classifier

## Live Demo

https://fruit-freshness-classifier-vinay-app.streamlit.app/
