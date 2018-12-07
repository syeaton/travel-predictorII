# Modeling parameters for this job. 
# These can be modified to adjust the model

TARGET_VARIABLE = 'travel'
UNIQUE_ID = 'traveler_id'
MODEL_INPUT_FEATURES = ['gender', 'college_degree', 'payment_method', 'dependents', 'avg_cc_bill']
MODEL_TYPE = "LogisticRegression" 