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

# --- common helper functions ---
# TODO: fix paths
os.chdir('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src')
from sysserology_helpers import write_logfile, read_plates


wd = '/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/'
os.chdir(wd)
# def get_metadata():

# [setup] -----------------------------------------------------------------------------------------------
# --- inputs ---
# TODO: common input file
# template to match well locations to unique sample IDs
platefile = 'ADNP_PlateLayout.xlsx'

# zipped file from FlowJo containing the raw data files + gating info + metadata
fcsfile = 'ADNP_Tulane.acs'


# TODO: try/catch no data


def unzip_acs(fcsfile, tmpdir):
    # [Unzip the FlowJo .acs file to individual .fcs files] -------------------------------------------------
    acs_ref = zipfile.ZipFile(fcsfile, 'r')
    acs_ref.extractall(tmpdir)
    acs_ref.close()


def find_files(fcs_filelist, plate_num, well):
    fcs_string = f"{plate_num}\.\w+{well}\_.+\.fcs"
    gate_string = f"{plate_num}\_\w+{well}\_.+\.xml"

    datafile = find_file(fcs_filelist, fcs_string)
    gatefile = find_file(fcs_filelist, gate_string)
    # matched_files = filter(r.match, fcs_filelist)  # returns iterator
    # list(matched_files)

    if(len(datafile) == 0):
        write_logfile(
            f"Missing .fcs data file for well {well}, plate {plate_num}")

    if(len(gatefile) == 0):
        write_logfile(
            f"Missing .xml gating file for well {well}, plate {plate_num}")

    return({'datafile': datafile, 'gatefile': gatefile})


def find_file(filelist, search_string, exact_match=False):
    if(not exact_match):
        search_string = ".*" + search_string + ".*"

    search = re.compile(search_string)
    file = [x for x in filelist if search.match(x)]

    # if there's only one match, convert from array to string
    if (len(file) == 1):
        return file[0]
    return file

# [Move and rename the .fcs files] ----------------------------------------------------------------------


def rename_fcs(fcs_filelist, sample, md, datadir, gatingdir, tmpdir):
    well = sample.well
    plate_num = sample.plate

    result = find_files(fcs_filelist, plate_num, well)
    datafile = result['datafile']
    gatefile = result['gatefile']

    # [Pull out the metadata] -------------------------------------------------------------------------------
    # Read in FCS data to get the metadata
# TODO: check if datafile has > 1 arg.
    if len(datafile) == 0:
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
        os.rename(tmpdir + gatefile, f'{gatingdir}/{gate_filename}')
    except:
        # error should have already been recorded in the 'find_files' function; no need to log again
        pass
    return md


def process_files(platefile):
    # import in the plate lookup table
    plates = read_plates(platefile)

    # pull out the experimental id for the given experiment
    expt_ids = plates.expt_id.unique()

    for expt_id in expt_ids:
        # only grab the
        filtered_plates = plates[plates.expt_id == expt_id]
        expt_types = filtered_plates.experiment.unique()

        print(expt_id)
        for expt_type in expt_types:
            print(expt_type)
            process_expt(filtered_plates, expt_id, expt_type)


# TODO: create unique logfile
def process_expt(plates, expt_id, expt_type):
    # create output directories
    datadir, gatingdir, tmpdir, metadir = create_dirs(plates, expt_id)

    # unzip the .fcs files
    unzip_acs(fcsfile, tmpdir)

    # TODO: copy the FlowJo XLSX files

    # rename the .fcs files, pull out metadata
    fcs_filelist = os.listdir(tmpdir)

    md = pd.DataFrame()
    write_logfile("\n--- RENAMING FCS & GATING FILES ---")

    for idx, row in plates.iterrows():
        md = rename_fcs(fcs_filelist, row, md, datadir, gatingdir, tmpdir)

    md = pd.merge(plates, md, on=['plate', 'well', 'sample_id'])
    # export to .csv file
    md.to_csv(metadir + f"{expt_type}-{expt_id}_metadata.csv", sep=',')

    # remove temp directory
    rm_tmp(tmpdir)

def rm_tmp(tmpdir):
    # refresh the files in the working directory:
    fcs_filelist = os.listdir(tmpdir)
    # Remove the two extra files that always come along for the ride
    # FlowJo workspace file
    workspace_file = find_file(fcs_filelist, "\.wsp")
    os.remove(tmpdir + workspace_file)

    # FlowJo table of contents xml file, which seems worthless
    toc_file = find_file(fcs_filelist, "ToC.xml")
    os.remove(tmpdir + toc_file)

    try:
        os.rmdir(tmpdir)
    except:
        write_logfile(
            f"Warning: not all .fcs data files were processed. This often happens if you have two experimental IDs in the same .acs file. {os.listdir(tmpdir)} files remain")


x = process_files(platefile)
