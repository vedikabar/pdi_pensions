import pandas as pd
import numpy as np

FILE_PATH = "/Users/rebeccasonn-lees/Downloads/randhrs1992_2022v1_SAS/randhrs1992_2022v1.sas7bdat"
hrs = pd.read_sas(FILE_PATH, format = 'sas7bdat', encoding='latin1')
#print(hrs.head())
#print(hrs.columns)

weight_cols = [col for col in hrs.columns if "WT" in col]
#print(weight_cols)

#starting to try to apply survey weights - need to add the name i want for the column taht we're weighting
weighted_mean = np.average(hrs[''], weights=hrs['RwWTCRNH'])
