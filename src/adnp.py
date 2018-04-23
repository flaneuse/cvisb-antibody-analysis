# @name:        adnp.py
# @summary:     Calculations for ADNP experiment
# @description: Imports fluorescence data from flow cytometry antibody-dependent neutrophil-mediated phagocytosis
# @sources:
# @depends:     pandas, numpy
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        17 April 2018

import pandas as pd
import numpy as np

# [Lookup table for the plate geometry, to map samples to wells] ----------------------------------------
platefile = ''

plate = pd.read_excel(platefile)

# pull out the actual plate geometry
plate = plate[['plate', 'cell', 'sample_id', 'sample_type', 'experiment', 'sample_dilution']]

plate.head
# [Import the fluorescence counts from FlowJo] ----------------------------------------------------------
fluorfile = '/Users/laurahughes/Dropbox (Scripps Research)/CViSB/Data/Systems Serology/Data for Laura from Bonnie/FlowJo Export Data from BMGEXP569 plate 1.xlsx'

fluor = pd.read_excel(fluorfile)

pd.read_excel(fluorfile, sheetname=None).keys()

# remove the mean / SD rows
fluor = fluor.drop(['Mean', 'SD'])

fluor = fluor.reset_index()


# Split the filename by "_" to get the well id of each sample
fluor['filename'] = fluor['index'].apply(lambda x: x.split('_'))
fluor.head

fluor['cell'] = fluor['filename'].apply(lambda x: x[2])


# [Merge together cell w/ sample ID] --------------------------------------------------------------------
fluor = pd.merge(fluor, plate, how='inner', on = 'cell', indicator=True)

# [Calculate ratios + average values] -------------------------------------------------------------------
# NOTE: where adjust calculations for different ratios
scale_factor = 1e4


fluor['phago_score'] = fluor['Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Freq. of Parent'] * fluor['Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Geometric Mean (Comp-Alexa Fluor 488-A)'] / scale_factor
fluor['calc'] = 'Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Freq. of Parent * Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Geometric Mean (Comp-Alexa Fluor 488-A) / 10,000'
fluor.head
# summary table
fluor.groupby(['plate', 'sample_id']).agg({'phago_score': ['mean', 'std', 'count']})

# merged
fluor['phago_mean'] = fluor.groupby(['plate', 'sample_id']).phago_score.transform('mean')
fluor['phago_std'] = fluor.groupby(['plate', 'sample_id']).phago_score.transform('std')
fluor['num_obs'] = fluor.groupby(['plate', 'sample_id']).phago_score.transform('count')

np.trapz(np.array([22.7493,	17.768735,	13.9848]), np.array([150, 750, 3750])) / np.trapz(np.array([86.765295,	94.033755,	25.95186]), np.array([150, 750, 3750]))

np.trapz(np.array([13.9848, 17.768735,	22.7493]), np.array([1/3750, 1/750, 1/150])) / np.trapz(np.array([25.95186, 94.033755,	86.765295]), np.array([1/3750, 1/750, 1/150]))

# background subtract
