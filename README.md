# CViSB antibody analysis
Python-based functions to convert flow cytometry fluorescence data into aggregated scores for [systems serology](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5740944/) measurements

## What this script does
1. imports a plate template, used to convert locations in a 96-well plate (or others) to a unique sample id
2. imports fluorescence measurements per sample, by experiment type
3. calculates [fluorescence score](#calcs), based on the assay type
4. calculates the mean fluorescence score + standard deviation across the replicates
5. calculates some basic flags for data that seems outside quality control
6. merges fluorescence score data with plate template, to connect sample id to fluroescence scores
* 7. renames raw .fcs files by sample id, rather than by well location
* 8. combines specific metadata from the experiment into a combined file

### Inputs
* [ADCD, ADCP, ADNP, or NKD]**PlateLayout.xlsx**: list mapping plate/well locations to unique sample ids + key metadata
* [ADCD, ADCP, ADNP, or NKD]**.acs**: exported, packaged layout from FlowJo containing raw .fcs files along with gating boundaries in .xml format
* [ADCD, ADCP, ADNP, or NKD]**.xlsx**: summarized fluorecence calculations for each sample replicate in an experiment

### Outputs
* **/metadata/**{expt\_type}**-**{expt\_id}**_metadata.csv**: all metadata parameters for a given experiment.
* **/input/fcs/**{sample\_id}**-plate**{plate\_number}**-**{well}**\_sysserology-{expt\_id}\_**{date}**.fcs**: raw flow cytometry data
* **/input/fcs/**{sample\_id}**-plate**{plate\_num}**-**{well}**\_sysserology-**{expt\_id}**\_**{fcs\_date}**\_gates.xml**: gating filters for each channel
* **/input/**{expt\_id}**\_**[ADCD, ADCP, ADNP, or NKD]**\_exported from FlowJo.xlsx**: fluorescence data per sample after gating, exported from FlowJo
* **sysserology-**[ADCD, ADCP, ADNP, or NKD]**\_**{expt_id}**\_**{date}**.csv**: fluorescence counts and scores per sample replicate
* **sysserology-ADCD**{ADCD expt_id}**-ADCP**{ADCP expt_id}**-ADNP**{ADNP expt_id}**-NKD**{NKD expt_id}**.csv**: combined, summarized score for each sample, after averaging and quality control
* {expt\_id}**\_**[ADCD, ADCP, ADNP, or NKD]**\_logfile.txt**: log files for any samples discarded or files not found during analysis

## <a name='calcs'> Calculations</a>
* **Background correction**: For each assay type, there is an option to background-correct the measurements. If this parameter is set to "true", the average background fluorescence from the "no fluorescence" samples (e.g. just buffer + reagents) from a particular plate will be subtracted before the fluorescence is calculated. By default, no background correction is done.

### ADCD
### ADCP

### Quality control checks

## How to run this script
* Copy the code to your hard drive
* Set working directory
* Set params
* Run script
