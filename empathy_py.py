# -*- coding: utf-8 -*-
"""Empathy.py.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16pxfDDB4EQUvW_Q0wsktRKp1O6rQ8Dhc

First, I will start by importing the necessary libraries for data manipulation, visualization, and machine learning.
"""

#Importing Libraries
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

#Filtering Warnings
warnings.filterwarnings('ignore')

#Importing machine learning libraries
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

"""# Loading all dataset
We load the eye-tracking data from CSV files into a DataFrame and merge all participant data into a single DataFrame.
"""

data_path = "CE888/EyeT/"

participants = range(1, 61)
trial_num = 1

All_files = []

for participant in participants:
    participant_files = os.listdir(data_path)
    participant_files = [f for f in participant_files if f.endswith(f"_participant_{participant}_trial_{trial_num}.csv")]
    if len(participant_files) == 0:
        print(f"missing file for {participant}")
        continue
    All_files.append(os.path.join(data_path, participant_files[0]))
len(All_files)

All_data = []

for files in All_files:
  data = pd.read_csv(files)
  All_data.append(data)

data = pd.concat(All_data)
print(data.shape)

data.head()

"""# Loading Questionnaire Data
We also load the questionnaire data from a separate CSV file.
"""

question_Dataset = pd.read_csv("CE888/Questionnaire_datasetIA.csv", encoding= 'unicode_escape')

question_Dataset.head()

"""# Data Preprocessing
Now, we begin the data preprocessing steps to clean and prepare the eye-tracking data for analysis.
1. Dropping Unnecessary Columns

We start by dropping columns that are not required for our analysis, as they contain redundant or irrelevant information.
"""

data.info()

#Preprocesses eye-tracking data by dropping unnecessary columns
columns_dropped =['Timeline name', 'Export date',
                      'Recording date UTC', 'Mouse position X', 'Recording start time',
                      'Recording Fixation filter name', 'Presented Stimulus name',
                      'Recording software version', 'Original Media height', 'Presented Media width',
                      'Presented Media name', 'Recording date',
                      'Recording duration', 'Event value', 'Sensor', 'Recording name',
                      'Eye movement type index', 'Recording resolution width', 'Recording resolution height',
                       'Recording start time UTC', 'Original Media width',
                      'Presented Media position X (DACSpx)', 'Unnamed: 0', 'Event', 'Presented Media position Y (DACSpx)',
                      'Mouse position Y', 'Recording monitor latency', 'Project name', 'Presented Media height']

# drop the columns
data_preprocessed = data.drop(columns=columns_dropped)

"""2. Handling Missing Values

Next, we handle missing values in the dataset using linear interpolation. We replace missing values with interpolated values based on the linear relationship between adjacent data points.
"""

data_preprocessed.info()

# replacing all commas to dots in the number values
data_preprocessed = data_preprocessed.replace(to_replace=r',', value='.', regex=True)

replace = ['Gaze point left Y (DACSmm)', 'Gaze point right X (DACSmm)',
                          'Gaze point right Y (DACSmm)', 'Gaze point X (MCSnorm)', 'Gaze point Y (MCSnorm)', 'Gaze point left X (MCSnorm)',
                          'Gaze point left Y (MCSnorm)', 'Gaze point right X (MCSnorm)','Gaze direction left X', 'Gaze direction left Y', 'Gaze direction left Z', 'Gaze direction right X',
                          'Gaze direction right Y', 'Gaze direction right Z',
                          'Eye position left X (DACSmm)', 'Eye position left Y (DACSmm)', 'Eye position left Z (DACSmm)',
                          'Eye position right X (DACSmm)', 'Eye position right Y (DACSmm)', 'Eye position right Z (DACSmm)',
                          'Gaze point left X (DACSmm)', 'Gaze point right Y (MCSnorm)',
                          'Fixation point X (MCSnorm)', 'Fixation point Y (MCSnorm)']


data_preprocessed[replace] = data_preprocessed[replace].astype(float)

data_preprocessed.info()

data_interpolated = data_preprocessed.interpolate(method='linear', limit_direction='backward')
data_preprocessed = data_interpolated.fillna(method='bfill')

data_preprocessed.isnull().sum()

"""3. Encoding Categorical Variables

To prepare the data for machine learning models, we encode categorical variables using Label Encoding.
"""

from sklearn.preprocessing import LabelEncoder
convert_labels = ['Validity left','Validity right','Eye movement type','Pupil diameter left','Pupil diameter right']

# Create a LabelEncoder object
Le = LabelEncoder()

# Apply label encoding to 'convert_labels' columns
for i in convert_labels:
    data_preprocessed[i] = Le.fit_transform(data_preprocessed[i])

data_preprocessed.info()

"""4. Merging with Questionnaire Data

Finally, we merge the preprocessed eye-tracking data with the questionnaire data to obtain empathy scores for each participant.
"""

data_preprocessed['Participant name'] = data_preprocessed['Participant name'].str[-2:].astype(int)
data_preprocessed.rename(columns={'Participant name': 'Participant nr'}, inplace=True)

#Merging with score dataset to get empathy score
data_preprocessed = data_preprocessed.merge(question_Dataset[['Participant nr','Total Score extended']],on = 'Participant nr',how ='inner')

data_preprocessed.head()

"""# Visualisation"""

data_preprocessed.hist(bins=60, figsize=(20, 15));

import seaborn as sns
plt.figure(figsize=(6, 3))
sns.scatterplot(x=data_preprocessed['Eyetracker timestamp'],y=data_preprocessed['Pupil diameter left'])
plt.xlabel('Time Stamp')
plt.ylabel('Pupil diameter left')
plt.title('Time Series Plot - Pupil diameter (left) vs Time Stamp')
plt.show()

import seaborn as sns
plt.figure(figsize=(6, 3))
sns.scatterplot(x=data_preprocessed['Eyetracker timestamp'],y=data_preprocessed['Pupil diameter right'])
plt.xlabel('Time Stamp')
plt.ylabel('Pupil diameter right')
plt.title('Time Series Plot - Pupil diameter (right) vs Time Stamp')
plt.show()

# ploting the correlation heatmap
corr = data_preprocessed.corr()
sns.set(style='white')
plt.figure(figsize=(30,30))
sns.heatmap(data_preprocessed.corr(), annot=True, cmap='coolwarm')
plt.show()

# Get a list of unique participant IDs
participant_ids = data_preprocessed['Participant nr'].unique()

# Iterate through each participant
for participant_id in participant_ids:
    # Extract data for the current participant
    participant_data = data_preprocessed[data_preprocessed['Participant nr'] == participant_id]

    # Example 1: Gaze Path Plot
    plt.figure(figsize=(8, 6))
    plt.plot(participant_data['Gaze point X'], participant_data['Gaze point Y'], '-o', markersize=3)
    plt.title(f'Gaze Path - Participant {participant_id}')
    plt.xlabel('Gaze X Coordinate')
    plt.ylabel('Gaze Y Coordinate')
    plt.show()

# Grouping the questionnaire data by Participant nr and summing their scores
participant_scores = question_Dataset.groupby('Participant nr')['Total Score extended'].sum().reset_index()

# Plotting the bar graph
plt.figure(figsize=(15, 6))
plt.bar(participant_scores['Participant nr'], participant_scores['Total Score extended'])
plt.title('Total Scores by Participant')
plt.xlabel('Participant Number')
plt.ylabel('Total Score')
plt.xticks(participant_scores['Participant nr'])
plt.grid(axis='y', linestyle='--')
plt.show()

"""# Time-Based Data Splitting for Time Series Analysis"""

import pandas as pd
from sklearn.model_selection import train_test_split

# Sort the data by the time column
data_sorted = data_preprocessed.sort_values(by='Recording timestamp')

# Define the percentage of data to be used for testing
test_size = 0.2  # You can adjust this based on your preference

# Calculate the index at which to split the data into training and testing sets
split_index = int(len(data_sorted) * (1 - test_size))

# Split the data into training and testing sets
train_data = data_sorted.iloc[:split_index]
test_data = data_sorted.iloc[split_index:]

# Separate the features (X) and target variable (y) in the training and testing sets
X_train = train_data.drop(columns=['Total Score extended'])
y_train = train_data['Total Score extended']

X_test = test_data.drop(columns=['Total Score extended'])
y_test = test_data['Total Score extended']

"""# LinearRegression"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Initialize lists to store results for each fold
mse_scores = []

# Initialize the Linear Regression model
model = LinearRegression()

# Fit the model on the training data
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Calculate Mean Squared Error (MSE) for this fold and store it in the list
mse = mean_squared_error(y_test, y_pred)
mse_scores.append(mse)
print(f"MSE: {mse}")

from sklearn.metrics import r2_score, mean_absolute_error

# Get the predicted scores from the model
y_pred = model.predict(X_test)

# Calculate R-squared (Coefficient of Determination)
r_squared = r2_score(y_test, y_pred)

# Calculate Mean Absolute Error (MAE)
mae = mean_absolute_error(y_test, y_pred)

print("R-squared:", r_squared)
print("Mean Absolute Error:", mae)

"""# RandomForest"""

from sklearn.ensemble import RandomForestRegressor

# Create a Random Forest Regressor object
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)

# Fit the model to the training data
rf_regressor.fit(X_train, y_train)

# Make predictions on the test data
y_pred = rf_regressor.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r_squared = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r_squared}")
print(f"Mean Absolute Error: {mae}")

