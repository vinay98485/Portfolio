---
category: project
domain: data_science
project_name: Customer Segmentation
---
# Intelligent Customer Segmentation Engine

## Project Name

Intelligent Customer Segmentation Engine

## Category

Unsupervised Machine Learning, Customer Analytics, Streamlit Dashboard

## Problem Statement

Discover hidden patterns in consumer behavior and group mall customers into actionable customer personas using age, annual income, and spending score.

## Technologies Used

- Python
- Pandas
- Scikit-learn
- K-Means
- Streamlit
- Plotly Express

## Dataset Information

- Dataset file in repository: `Mall_Customers.csv`
- Features used: `Age`, `Annual Income (k$)`, and `Spending Score (1-100)`.
- Additional hover/context field in the app: `Gender`.

## Model Architecture

- Streamlit dashboard loads `Mall_Customers.csv`.
- User can choose the number of clusters with a sidebar slider from 2 to 10, defaulting to 5.
- K-Means is trained with `random_state=42` and `n_init=10`.
- The Elbow Method calculates WCSS / inertia for K values from 1 to 10.
- The dashboard visualizes clusters on a 2D scatter plot of annual income vs spending score, with dot size representing age.

## Algorithms Used

- K-Means clustering
- Elbow Method
- Within-Cluster Sum of Squares / inertia

## Key Features

- Interactive Streamlit dashboard.
- Adjustable K value from 2 to 10.
- Mathematical proof panel using the Elbow Method.
- 2D customer cluster map.
- Persona labels when K=5.
- Raw data view with cluster assignments.
- CSV export of segmented data.

## Results / Metrics

- README states K=5 is the most mathematically sound choice from the Elbow Method.
- Five personas identified:
  - The VIPs: high spend / high income
  - The Frugal Wealthy: low spend / high income
  - The Impulse Buyers: high spend / low income
  - The Budget-Conscious: low spend / low income
  - The Core Base: average spend / average income

## Challenges Faced

- Avoiding arbitrary customer grouping by using WCSS and the Elbow Method.
- Translating numeric cluster labels into business-readable personas.

## Learnings

- Building an unsupervised learning dashboard.
- Applying K-Means to customer segmentation.
- Using the Elbow Method to justify cluster count.
- Visualizing customer behavior with Plotly.
- Exporting model-enriched data for business use.

## GitHub Repository URL

https://github.com/vinay98485/customer-segmentation

## Live Demo

https://customer-segmentation-vinay-app.streamlit.app/
