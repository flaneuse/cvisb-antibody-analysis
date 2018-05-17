# @name:        nkd.py
# @summary:     Calculations for NKD experiment
# @description: Imports fluorescence data from flow cytometry antibody-dependent natural killer cell activation
# @sources:
# @depends:     pandas, SysSerologyExpt
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        2 May 2018


import pandas as pd
import os
from scipy.stats import percentileofscore

# TODO: fix path
os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src')
from SysSerologyExpt import SysSerologyExpt

# TODO: fix the source info


# [Calculate ratios + average values] -------------------------------------------------------------------
# NOTE: this is where you adjust the calculations
# Define a new class, inheriting from the common functions in SysSerologyExpt
class NKD(SysSerologyExpt):

    # --- Adjust the columns within the Excel sheet ---
    # define which columns used in the calculations
    # format: {'column name in FlowJo spreadsheet': 'what to rename it to'}
    fluor_cols = {
    'Singlets/Cells/CD3, SSC-A subset | Geometric Mean (Comp-APC-Cy7-A)': 'CD16_MFI',
    'Singlets/Cells/CD3, SSC-A subset/CD56, CD16 subset/CD56, CD107a subset | Freq. of Parent': 'CD107a_MFI',
    'Singlets/Cells/CD3, SSC-A subset/CD56, CD16 subset/CD56, IFNg subset | Freq. of Parent': 'IFNg_MFI',
    'Singlets/Cells/CD3, SSC-A subset/CD56, CD16 subset/CD56, MIP-1b subset | Freq. of Parent': 'MIP-1b_MFI'
    }

    def calc_score(self):
        # !!!! [2/3] CALCULATION DEFINITION !!!! Change as needed
        # Creates a new column called 'fluor_score' which calculates the fluorescence score
        # For NKD, simply take the scores from fluor_cols and convert to a long format.
        import pandas as pd

        # TODO: Need to pivot 2x: once for source columns, once for the real data

        cols = self.df.columns
        pivot_cols = self.fluor_cols.values()
        keep_cols = set(cols) - set(pivot_cols) - set(pivot_cols.apply(lambda x: x + "_source"))


        self.df = pd.melt(self.df, id_vars=keep_cols)

        self.df.rename(columns={'variable': 'fluor_score_type', 'value': 'fluor_score'}, inplace=True)


        self.run_qc()

        return self.df

# !!!! [3/3] Change QC !!!!
    def run_qc(self):
        """
        Function used to run some basic quality control on the fluorescence scores
        """
        # self.df['fluor_percentile'] = self.df.fluor_score.apply(lambda x: percentileofscore(self.df.fluor_score, x))

    def __init__(self, fluorfile, platefile, expt_dict):
        super().__init__(fluorfile, platefile, expt_dict)
