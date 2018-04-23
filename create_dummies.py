import sys
import pandas as pd
import numpy as np

census = pd.read_csv(sys.stdin)

# create tag
census.loc[census['label'] == '- 50000.','label'] = 0
census.loc[census['label'] != 0,'label'] = 1

header = list(census.columns.values)
continuous_vars = ['id','age','wage_per_hour','capital_gains','capital_losses','dividends_from_stocks','instance_weight','num_persons_worked_for_employer','weeks_worked_in_year','year','label']
dummy_vars = [col for col in header if col not in continuous_vars]

census = pd.get_dummies(census, columns = dummy_vars)

census.to_csv(sys.stdout, index = False)
