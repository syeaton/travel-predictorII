## File of helper functions for handling data. Copied from various common modules. 

import os
import pandas as pd
import pickle
import logging
from skafossdk import DataSourceType, Skafos
from s3fs.core import S3FileSystem  
from .schema import SCORING_SCHEMA, METRIC_SCHEMA


# Data access functions

# Input data
S3_BUCKET = "skafos.example.data"
TRAINING_FILE_NAME = "TravelPrediction/travel_training_data.csv"
SCORING_FILE_NAME = "TravelPrediction/travel_scoring_data.csv"

# Project keyspace

### NEEDS TO BE UPDATED ####
# KEYSPACE = "6342e8556afc53a04c855f44"
KEYSPACE = "f06b460dd6e7b7cad8160ab4"
#with open("../metis.config.yml", "r") as infile:
#    yml = infile.read()
#KEYSPACE = yml.split("\n")[0].split(":")[-1].strip()

#-------------------Data Access Functions -----------------------

# Get input data from S3 -- specify training or scoring. 
def get_data(csvCols, whichData):  
    s3 = S3FileSystem(anon=True)
    if whichData == "training":
        path = f's3://{S3_BUCKET}/{TRAINING_FILE_NAME}'
    elif whichData == "scoring":
        path = f's3://{S3_BUCKET}/{SCORING_FILE_NAME}'
    # PUT ERROR CATCHING HERE FOR ERRORS IN INPUT FILES
    # Read in .csv file, but only for specified columns. 
    df = pd.read_csv(s3.open(f'{path}', mode='rb'), usecols=csvCols)
    for c in csvCols:
        if (df[c].dtype == 'object'):
            df = df[df[c].str.match(" ") == False]
    return df

# Save scores and metrics to Cassandra
def save_data(ska, data, schema):
    # Save data to Cassandra
    if schema == SCORING_SCHEMA:
        #Convert scoring data to list of objects
        dataToWrite = data.to_dict(orient='records')
    if schema == METRIC_SCHEMA:
        dataToWrite = data
        ska.log("Executing for METRIC_SCHEMA", labels=["Cassandra"])
    #Save to Cassandra
    ska.log("Saving to Cassandra", level=logging.INFO)
    ska.engine.save(schema, dataToWrite).result()
    
# Access metrics from Cassandra for plotting
def get_metrics(ska):
    view = "model_metrics"
    table_options = {
            "keyspace": KEYSPACE,
            "table": "model_metrics"
            }
    data_source = DataSourceType.Cassandra
    cv = ska.engine.create_view(view, table_options, data_source).result()
    print(f"ska.engine.create_view: {cv}\n", flush=True)
    rows = ska.engine.query(f"SELECT * FROM model_metrics").result().get('data')
    metric_df = pd.DataFrame(data=rows)
    return metric_df

#-------------------Data Manipulation Functions -----------------------

# Convert categorical variables to dummies
def dummify_columns(xVars, features):
    for column in features:
        if (xVars[column].dtype == 'object'):
            dvars = pd.get_dummies(xVars[column], prefix=xVars[column].name)
            # Remove one column from dvars to handle multi-collinearity
            dvars = dvars.drop(dvars.columns[[-1,]], axis=1)
            xVars = pd.concat([xVars, dvars], axis=1)
            # Remove original non-numeric column
            xVars = xVars.drop(column, axis=1)
    return xVars



