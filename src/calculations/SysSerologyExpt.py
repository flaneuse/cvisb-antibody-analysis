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

    def __init__(self, fluorfile, plate_dict, expt_dict):
        # import data
        self.df = self.read_fluor(fluorfile)
        self.plate_dict = []
        self.expt_dict = []
        # self.expt_type = self._get_expttypes(expt_dict)
        # self.expt_id = "-".join(expt_dict.keys()) # if multiple, concat together
        # self.savedirs = self._get_exptdirs(expt_dict)
        #
        # # merge samples to their IDs
        # self._join_sampleids(plate_dict)
        #
        # # Calculate the score for each sample based on the function defined in the derived classes
        # self.calc_score()
        #
        # # Aggregate up to average for each sample
        # self.calc_mean()
        #
        # # Save
        # self.export_data()




# [1] Import the fluorescence data ------------------------------------------------------------------------
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

        # Rename the columns according to what's defined in "fluor_cols" (defined individually in the derived classes)
        self._rename_cols(df)
        return(df)

    # TODO: better error if no plate number
    # TODO: self, + pandas, re
    def _get_platenum(self, sheetname):
        plate_num = re.findall(r'\d+', sheetname)

        try:
            return int(plate_num[0])
        except:
            pass
            # TODO: fix
            # logfile.write("Unknown plate number in input file {fluorfile}. Please label worksheets as 'Plate 1', 'Plate 2', ...")

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
        df['row'] = df.well.apply(lambda x: re.search(r'[A-Z]', x).group(0)) # pull out the row letter
        df['col'] = df.well.apply(lambda x: int(re.search(r'\d{1,2}', x).group(0))) # pull out the row letter

        return df

    def _rename_cols(self, df):
        df.rename(columns = self.fluor_cols, inplace = True)

        for key, value in self.fluor_cols.items():
            df[value + "_source"] = key

        return df

# [2] Pull out expt metadata for saving -------------------------------------------------------------------
    def _get_expttypes(self, expt_dict):
        arr = []
        for expt in expt_dict.values():
            arr.append(expt['type'])
        return "-".join(set(arr))

    def _get_exptdirs(self, expt_dict):
        arr = []
        for expt in expt_dict.values():
            arr.append(expt['exptdir'])
        return set(arr)

    # [3] Join data with their sample IDs ---------------------------------------------------------------------
    def _join_sampleids(self, plate_dict):
        import pandas as pd

        # TODO: check all columns exist
        self.df = pd.merge(self.df, plate_dict, how='left', on = ['plate', 'well'])

# [4] Aggregate stats -------------------------------------------------------------------------------------
# TODO: check merge has been run.
    def calc_mean(self):
        grouping_cols = ['plate', 'sample_id', 'sample_type', 'experiment', 'expt_id', 'fluor_score_type']

        self.df['sample_mean'] = self.df.groupby(grouping_cols).fluor_score.transform('mean')
        self.df['sample_std'] = self.df.groupby(grouping_cols).fluor_score.transform('std')
        self.df['num_obs'] = self.df.groupby(grouping_cols).fluor_score.transform('count')

        # collapsed version
        self.summary = self.df.groupby(grouping_cols).agg({'fluor_score': ['mean', 'std', 'count', self._get_indivs]})

        self.summary.rename(columns = {'_get_indivs': 'indiv_scores', 'count': 'num_obs'}, inplace = True)

    def _get_indivs(self, arr):
        if(len(arr) == 1):
            return arr
        else:
            return tuple(arr)

# [5] Save data -------------------------------------------------------------------------------------------
    def export_data(self, excel = True):
        for savedir in self.savedirs:
            filename = f'{savedir}sysserology-{self.expt_type}-{self.expt_id}'
            if (excel):
                self.df.to_excel(filename + ".xlsx")
                self.summary.to_excel(filename + "_summary.xlsx")
                self.df.to_json(filename + ".json")
            else:
                self.df.to_csv(filename + ".csv")
                self.summary.to_csv(filename + "_summary.csv")
                self.df.to_json(filename + ".json")
