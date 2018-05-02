# @name:        adnp.py
# @summary:     Calculations for ADNP experiment
# @description: Imports fluorescence data from flow cytometry antibody-dependent neutrophil-mediated phagocytosis
# @sources:
# @depends:     pandas, numpy, scipy
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        17 April 2018


import pandas as pd
import numpy as np
import os
import re
from scipy.stats import percentileofscore
os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src')
from SysSerologyExpt import SysSerologyExpt
from sysserology_helpers import read_plates
# [Import the fluorescence counts from FlowJo] ----------------------------------------------------------
fluorfile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_data from FlowJo.xlsx'

def _get_platenum(sheetname):
    plate_num = [int(s) for s in sheetname.split() if s.isdigit()]

    try:
        return plate_num[0]
    except:
        write_logfile("Unknown plate number in input file {fluorfile}. Please label worksheets as 'Plate 1', 'Plate 2', ...")

def _clean_fluor(df, plate_num):
    # remove the mean / SD rows
    df = df.drop(['Mean', 'SD'])

    # convert the filename from an index
    df = df.reset_index()
    df.rename(columns = {'index': 'filename'}, inplace = True)

    df['plate'] = plate_num

    # Pull out the well ID for each sample from the filename using regular expression matching
    # Pulls out the first capitalized letter followed by 1-2 digits
    df['well'] = df.filename.apply(lambda x: re.search(r'[A-Z]\d{1,2}', x).group(0))

    return df

def read_fluor(filename):
    # Read in the fluorescence file. Multiple plates found on separate sheets
    fluor = pd.read_excel(fluorfile, sheetname=None)

    # Container for the combined results of all plates
    df = pd.DataFrame()

    # Loop over plates; pull out the fluroescence data and
    for sheetname in fluor.keys():
        plate_num = _get_platenum(sheetname)

        tmp = _clean_fluor(fluor[sheetname], plate_num)

        df = df.append(tmp)


    return(df)

fluor = read_fluor(fluorfile)



# [Calculate ratios + average values] -------------------------------------------------------------------
# NOTE: this is where you adjust the calculations
# Define a new class, inheriting from the common functions in SysSerologyExpt
class ADNP(SysSerologyExpt):

    # --- Adjust the columns within the Excel sheet ---
    # define which columns used in the calculations
    # format: {'column name in FlowJo spreadsheet': 'what to rename it to'}
    fluor_cols = {
    'Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Freq. of Parent': 'pct_fluor',
    'Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Geometric Mean (Comp-Alexa Fluor 488-A)': 'MFI'
    }

    def calc_score(self):
        # !!!! [2/3] CALCULATION DEFINITION !!!! Change as needed
        # Creates a new column called 'fluor_score' which calculates the fluorescence score
        self.df['fluor_score'] = self.df.MFI * self.df.pct_fluor / self.scale_factor
        self.df['fluor_score_type'] = 'phagocytotic score'

        self.run_qc()

        return self.df

# !!!! [3/3] Change QC !!!!
    def run_qc(self):
        """
        Function used to run some basic quality control on the fluorescence scores
        """
        self.df['fluor_percentile'] = self.df.fluor_score.apply(lambda x: percentileofscore(self.df.fluor_score, x))

    def __init__(self, fluorfile, platefile):
        super().__init__(fluorfile, platefile)


x = ADNP(fluor)
# x.export_data('test.xlsx')

platefile = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_PlateLayout.xlsx'
plate_dict = read_plates(platefile)


plate_dict
x.join_samplenames(plate_dict)
x.calc_mean()
x.df.head

x.export_data('sample_ADNP', excel = False)
# summary table

def get_indivs(arr):
    if(len(arr) == 1):
        return arr
    else:
        return list(arr)

fluor.groupby(['plate']).agg(get_indivs)
fluor.groupby(['plate', 'well']).agg({'pct_fluor': ['mean', 'std', 'count', get_indivs]})

# merged


# np.trapz(np.array([22.7493,	17.768735,	13.9848]), np.array([150, 750, 3750])) / np.trapz(np.array([86.765295,	94.033755,	25.95186]), np.array([150, 750, 3750]))
#
# np.trapz(np.array([13.9848, 17.768735,	22.7493]), np.log10([1/3750, 1/750, 1/150])) / np.trapz(np.array([25.95186, 94.033755,	86.765295]), np.log10([1/3750, 1/750, 1/150]))
#
# np.trapz(np.array([13.9848, 17.768735,	22.7493]), np.array([1/3750, 1/750, 1/150])) / np.trapz(np.array([25.95186, 94.033755,	86.765295]), np.array([1/3750, 1/750, 1/150]))
