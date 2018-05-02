import pandas as pd
import os

import re

# TODO: double check all calcs correct
# --- common helper functions ---
# TODO: fix paths
# os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src')
# from sysserology_helpers import write_logfile, read_plates

class SysSerologyExpt:
    scale_factor = 1e4

    def __init__(self, fluorfile, platefile):
        self.df = self.read_fluor(fluorfile)

        # Rename the columns according to what's defined in "fluor_cols"
        self._rename_cols()

        self.calc_score()

    def _rename_cols(self):
        self.df.rename(columns = self.fluor_cols, inplace = True)

        for key, value in self.fluor_cols.items():
            self.df[value + "_source"] = key

        return self.df

    # TODO: better error if no plate number
    # TODO: self, + pandas, re
    def _get_platenum(self, sheetname):
        plate_num = [int(s) for s in sheetname.split() if s.isdigit()]

        try:
            return plate_num[0]
        except:
            write_logfile("Unknown plate number in input file {fluorfile}. Please label worksheets as 'Plate 1', 'Plate 2', ...")

    def _clean_fluor(self, df, plate_num):
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

    def read_fluor(self, filename):
        import pandas as pd
        # Read in the fluorescence file. Multiple plates found on separate sheets
        fluor = pd.read_excel(filename, sheetname=None)

        # Container for the combined results of all plates
        df = pd.DataFrame()

        # Loop over plates; pull out the fluroescence data and
        for sheetname in fluor.keys():
            plate_num = self._get_platenum(sheetname)

            tmp = self._clean_fluor(fluor[sheetname], plate_num)

            df = df.append(tmp)


        return(df)

    def export_data(self, filename, format="excel"):
        if (format == 'excel'):
            self.df.to_excel(filename)
        else:
            self.df.to_csv(filename)

x = SysSerologyExpt('/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_data from FlowJo.xlsx', '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_PlateLayout.xlsx')

y = New('/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_data from FlowJo.xlsx', '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_PlateLayout.xlsx')
y.fluor_cols
class New(SysSerologyExpt):
        # --- Adjust the columns within the Excel sheet ---
        # define which columns used in the calculations
        # format: {'column name in FlowJo spreadsheet': 'what to rename it to'}
        fluor_cols = {
        'Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Freq. of Parent': 'pct_fluor',
        'Granulocytes/CD14, CD3 subset/CD14, CD66b subset/beads, CD66b subset | Geometric Mean (Comp-Alexa Fluor 488-A)': 'MFI'
        }

        def calc_score(self):
            print('succcessssss')

        def __init__(self, ff, pf):
            super().__init__(ff, pf)
# Works fine

class SysSerologyExpt:
    scale_factor = 1e4

    def __init__(self, df):
        self.df = df

        # Rename the columns according to what's defined in "fluor_cols"
        self._rename_cols()

        self.calc_score()

    def _rename_cols(self):
        self.df.rename(columns = self.fluor_cols, inplace = True)

        for key, value in self.fluor_cols.items():
            self.df[value + "_source"] = key

        return self.df

    def export_data(self, filename, excel = True):
        if (excel):
            self.df.to_excel(filename + ".xlsx")
            self.summary.to_excel(filename + "_summary.xlsx")
        else:
            self.df.to_csv(filename + ".csv")
            self.summary.to_csv(filename + "_summary.csv")

    def join_samplenames(self, plate_dict):
        import pandas as pd



        # TODO: check all columns exist
        self.df = pd.merge(self.df, plate_dict, how='left', on = ['plate', 'well'])



    def _get_indivs(self, arr):
        if(len(arr) == 1):
            return arr
        else:
            return tuple(arr)

# TODO: check merge has been run.
    def calc_mean(self):
        grouping_cols = ['plate', 'sample_id', 'sample_type', 'experiment', 'expt_id']

        self.df['fluor_mean'] = self.df.groupby(grouping_cols).fluor_score.transform('mean')
        self.df['fluor_std'] = self.df.groupby(grouping_cols).fluor_score.transform('std')
        self.df['num_obs'] = self.df.groupby(grouping_cols).fluor_score.transform('count')

        # collapsed version
        self.summary = self.df.groupby(grouping_cols).agg({'fluor_score': ['mean', 'std', 'count', self._get_indivs]})

        self.summary.rename(columns = {'_get_indivs': 'indiv_scores', 'count': 'num_obs'})
