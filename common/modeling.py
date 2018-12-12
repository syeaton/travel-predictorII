# Modeling parameters for this job.
# These can be modified to adjust the model

TARGET_VARIABLE = 'travel'
UNIQUE_ID = 'traveler_id'
MODEL_INPUT_FEATURES = ['apt_lease_length', 'payment_method', 'dependents', 'tsa_pre']
MODEL_TYPE = "LogisticRegression"