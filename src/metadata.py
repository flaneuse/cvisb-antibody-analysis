# @name:        metadata.py
# @summary:     pulls metadata from an FCS experiment
# @description:
# @sources:
# @depends:
# @author:      Laura Hughes
# @email:       lhughes@scripps.edu
# @license:     Apache-2.0
# @date:        23 April 2018

# [Import dependencies] ---------------------------------------------------------------------------------
# --- data manipulation ---
import pandas as pd
import re  # regular expression / string matching

# --- file manipulation ---
import os
import zipfile

# --- flow cytometry ---
import FlowCytometryTools
from FlowCytometryTools import FCMeasurement

# def get_metadata():

# [setup] -----------------------------------------------------------------------------------------------
# --- inputs ---
wd = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/'

# template to match well locations to unique sample IDs
platefile = 'ADNP_PlateLayout.xlsx'

# zipped file from FlowJo containing the raw data files + gating info + metadata
fcsfile = 'ADNP_Tulane.acs'

# --- setup ---
os.chdir(wd)
# os.makedirs('log')
# TODO: make better header

logfile = 'logfile.txt'
with open(logfile, 'w') as mylog:
    mylog.write("LOGFILE FOR EXPERIMENT\n")

def write_logfile(msg, logfile = 'logfile.txt'):
    print(msg)
    with open(logfile, 'a') as mylog:
        mylog.write(msg + "\n")

# [Lookup table for the plate geometry, to map samples to wells] ----------------------------------------
def read_plates(platefile):
    meta_cols = ['plate', 'well', 'sample_id', 'sample_type',
               'experiment', 'sample_dilution', 'cell_donor', 'expt_id']
    plate_dict = pd.read_excel(platefile, sheetname=None)

    # combined across all plates
    plates = pd.DataFrame()

    # combine all the plates together
    for name, plate in plate_dict.items():
        if(name != 'lookup tables'):
            # pull out the actual plate geometry
            try:
                plates = plates.append(plate[meta_cols], ignore_index=True)
            except:
                msg = f"Sheet '{name}' in {platefile} is missing 1+ columns of {meta_cols}. Rename the plate template columns to match."
                write_logfile(msg)

    return(plates)


# TODO: try/catch no data

# [Define output directories] ---------------------------------------------------------------------------
def create_dirs(plates):
    # TODO: check for multiple expt ids
    # pull out the experimental id for the given experiment
    expt_id = plates.expt_id.unique()[0]

    datadir = f'{expt_id}/input/fcs'

    gatingdir = f'{expt_id}/input/gating'
    # temp
    tmpdir = f'{expt_id}/tmp/'

    # create output directories
    try:
        os.makedirs(datadir)
    except:
        write_logfile(f"{datadir} already exists -- no need to create")

    try:
        os.makedirs(gatingdir)
    except:
        write_logfile(f"{gatingdir} already exists -- no need to create")

    return([datadir, gatingdir, tmpdir])


def unzip_acs(fcsfile, tmpdir):
    # [Unzip the FlowJo .acs file to individual .fcs files] -------------------------------------------------
    acs_ref = zipfile.ZipFile(fcsfile, 'r')
    acs_ref.extractall(tmpdir)
    acs_ref.close()

# [Move and rename the .fcs files] ----------------------------------------------------------------------
# moves + renames
# def move_file(sample):



def find_files(fcsfiles, plate_num, well):
    fcs_string = f".*{plate_num}\.\w+{well}\_.+\.fcs"
    gate_string = f".*{plate_num}\_\w+{well}\_.+\.xml"

    fcs_search = re.compile(fcs_string)
    gate_search = re.compile(gate_string)
    datafile = [x for x in fcsfiles if fcs_search.match(x)]
    gatefile = [x for x in fcsfiles if gate_search.match(x)]
    # matched_files = filter(r.match, fcsfiles)  # returns iterator
    # list(matched_files)

    if(len(datafile) == 0):
        write_logfile(f"Missing .fcs data file for well {well}, plate {plate_num}")

    if(len(gatefile) == 0):
        write_logfile(f"Missing .xml gating file for well {well}, plate {plate_num}")

    return({'datafile': datafile, 'gatefile': gatefile})



def rename_fcs(fcsfiles, sample, md, datadir, gatingdir, tmpdir):
    well = sample.well
    plate_num = sample.plate

    result = find_files(fcsfiles, plate_num, well)
    datafile = result['datafile']
    gatefile = result['gatefile']

    # [Pull out the metadata] -------------------------------------------------------------------------------
    # Read in FCS data to get the metadata
# TODO: check if datafile has > 1 arg.
    try:
        datafile = datafile[0]
    except:
        # error should have already been recorded in the 'find_files' function
        print("datafile is empty")
    else:
        fcs_data = FCMeasurement(
            ID=well, datafile=tmpdir + datafile, readdata=False)
        fcs_date = pd.to_datetime(fcs_data.meta['$DATE'])
        fcs_date = fcs_date.strftime("%Y-%m-%d")

        # Create filenames
        fcs_filename = f'{sample.sample_id}-plate{plate_num}-{well}_sysserology-{sample.expt_id}_{fcs_date}.fcs'
        gate_filename = f'{sample.sample_id}-plate{plate_num}-{well}_sysserology-{sample.expt_id}_{fcs_date}_gates.xml'

        # Here's where it's defined which automatically saved info to pull from the fcs files.
        md = md.append({
            'sample_id': sample.sample_id,
            'plate': plate_num,
            'well': well,
            'original_file': fcs_data.meta['$FIL'],
            'renamed_file': fcs_filename,
            'expt_name': fcs_data.meta['EXPERIMENT NAME'],
            'sample_name': fcs_data.meta['$SRC'],
            'plate name': fcs_data.meta['PLATE NAME'],
            'sample_date': fcs_date,
            'flow_cytometer': fcs_data.meta['$CYT'],
            'fcs_version': fcs_data.meta['CREATOR'],
            'fcs_settings': fcs_data.meta['SETTINGS'],
            'username': fcs_data.meta['EXPORT USER NAME']
        }, ignore_index=True)

        # [Rename the data files] -------------------------------------------------------------------------------
        os.rename(tmpdir + datafile, f'{datadir}/{fcs_filename}')

    try:
        os.rename(tmpdir + gatefile[0], f'{gatingdir}/{gate_filename}')
    except:
        # error should have already been recorded in the 'find_files' function
        pass
    return md

def process_files(platefile):
    plates = read_plates(platefile)

    datadir, gatingdir, tmpdir = create_dirs(plates)

    unzip_acs(fcsfile, tmpdir)

    fcsfiles = os.listdir(tmpdir)

    md = pd.DataFrame()
    write_logfile("--- RENAMING FCS & GATING FILES ---\n")

    for idx, row in plates.iterrows():
        md = rename_fcs(fcsfiles, row, md, datadir, gatingdir, tmpdir)

    return md;

x = process_files(platefile)



    # TODO: merge metadata with core plate dictionary

    # TODO remove the temporary directory
    # TODO: check that no files remain
    # TODO: check 2 files / sample
