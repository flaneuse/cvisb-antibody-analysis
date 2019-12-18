from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from calculations.sysserology_helpers import read_plates, create_dirs
from calculations.adnp import ADNP
import pandas as pd
import os

# Initialize app; set up the settings
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
print(os.environ['APP_SETTINGS'])

# Create instance of API, to add views to app.
api = Api(app)
# required to get around Chrome blocking passing data b/w 2 localhosts
CORS(app, supports_credentials=True)

# [Connect to DB] ---------------------------------------------------------------------------------------
db = SQLAlchemy(app)
from server.models import FileRef, Plate, FluorTable

# [Views] -----------------------------------------------------------------------------------------------
@app.route("/")
def hello():
    return jsonify({'text':'Hello World!'})


# class Employees(Resource):
#     def get(self):
#         return {'employees': [{'id':1, 'name':'Balram'},{'id':2, 'name':'Tom'}]}, 201

class DownloadData(Resource):
    def get(self):
        return send_file("/Users/laurahughes/GitHub/cvisb-antibody-analysis/src/server/models.py") # works
        # return send_file("/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/ADNP_Tulane.acs", as_attachment=True) # works
        # return send_file("/Users/laurahughes/GitHub/cvisb-antibody-analysis/src/server/models.py", as_attachment=True) # works
        # return send_file("/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/BMGEXP568/metadata/ADNP-BMGEXP568_metadata.csv") # works: --> download .csv. Doesn't work for .xlsx (presumably anything non-text)
        # return {send_file('/Users/laurahughes/GitHub/cvisb-antibody-analysis/example_data/BMGEXP568/metadata/ADNP-BMGEXP568_metadata.csv', as_attachment=True)}, 201

# def read_plates(platefile):
#     meta_cols = ['plate', 'well', 'sample_id', 'sample_type',
#                'experiment', 'sample_dilution', 'cell_donor', 'expt_id']
#     print('reading plates')
#     print(platefile)
#     plate_dict = pd.read_excel(platefile, sheetname=None)
#
#     # combined across all plates
#     plates = pd.DataFrame()
#
#     # combine all the plates together
#     for name, plate in plate_dict.items():
#         if(name != 'lookup tables'):
#             # pull out the actual plate geometry
#             try:
#                 plates = plates.append(plate[meta_cols], ignore_index=True)
#             except:
#                 msg = f"Sheet '{name}' in {platefile} is missing 1+ columns of {meta_cols}. Rename the plate template columns to match."
#                 write_logfile(msg)
#
#     # pull out the experimental id for the given experiment
#     # expt_ids = dict of expt. ids and types
#     expt_ids = dict(zip(plates.expt_id, plates.experiment))
#
#     return(plates, expt_ids)

class Upload(Resource):
    # def get(self):
    #     return jsonify({'text':'Uploaded something.'})

    def post(self):
        print('called post')

        print(request.form) # params
        filetype = request.form['file']
        expt_type = request.form['expt']
        # print(filetype)
        f = request.files['file']

        if(filetype == "plates"):
            df, expt_dict = read_plates(f)
            print(df.head())
            try:
                df.to_sql(name='plate_dict', con=db.engine, index=False, if_exists='append')
                return jsonify({'text':'Saved result to database'})
            except Exception as err:
                print("Unable to add item to database.")
                print(err)
                return jsonify({'text':'Unable to save result'})
        elif(filetype == 'data'):

            if(expt_type == "ADCD"):
                print('ADCD')
                expt = ADNP(f, None, None)
            elif(expt_type == "ADCP"):
                print('ADCP')
                expt = ADNP(f, None, None)
            elif(expt_type == "ADNP"):
                print('ADNP')
                expt = ADNP(f, None, None)
            elif(expt_type == "NKD"):
                print('NKD')
                expt = ADNP(f, None, None)
            else:
                print("Unknown experiment type!")
            # print(expt.df)
            try:
                expt.df.to_sql(name='fluor', con=db.engine, index=False, if_exists='append')
                return jsonify({'text':'Saved result to database'})
            except Exception as err:
                print("Unable to add item to database.")
                print(err)
                return jsonify({'text':'Unable to save result'})
        # try:
        #     result = FileRef(
        #         file = f.read(),
        #         file_type = filetype,
        #         expt_id = request.form['expt_id'],
        #         expt_type = request.form['expt']
        #     )
        #     db.session.add(result)
        #     db.session.commit()
        #     return jsonify({'text':'Saved result to database'})
        # except:
        #     print("Unable to add item to database.")
        #     return jsonify({'text':'Unable to save result'})
        # return x.to_json(), 201


class FluorData(Resource):
    def get(self):
        print('retrieving data')
        # TODO: for now, hack to just read in the data and spit back out.  Extraordinarily unclever.
        df = pd.read_excel('/Users/laurahughes/GitHub/cvisb-antibody-analysis/src/server/testdata.xlsx')
        print(df)
        return df.to_json()

class Merge(Resource):
    def get(self):
        print('merging starting')
        # TODO: filters so only get data want.
        join_res = db.session.query(Plate, FluorTable).join(FluorTable, (FluorTable.well == Plate.well) & (FluorTable.plate == Plate.plate))
        # for _row in join_res:
        #     print(zip(_row.sample_id, _row.MFI))
        result = db.session.query(Plate).all()

        # x = pd.read_sql(result, db.session.bind)
        df = pd.read_sql(sql = join_res.statement,
                 con = db.session.bind)
        print(df.head())
        # for u in db.session.query(Plate).all():
        #     print(u.__dict__)
        # print(Plate.__table__.columns)
        res = []
        for x,y in join_res:
            # print(x.serialize())
            # # print(pd.DataFrame(x))
            # print(y.serialize())
            res.append({
            'sample_id': x.sample_id,
            'MFI': y.MFI})
        return jsonify(res)
        # return jsonify({'num returned': len(join_res)})

# api.add_resource(Employees, '/employees', methods=['GET']) # Route_1
api.add_resource(DownloadData, '/dwnload', methods=['GET']) # test download route; '/download' is reserved (?)
api.add_resource(Upload, '/upload', methods=['POST']) # suck up the data
api.add_resource(Merge, '/merge', methods=['GET']) # merge the data together for a particular experiment
api.add_resource(FluorData, '/fluordata', methods=['GET']) # retrieve processed data

if __name__ == '__main__':
     app.run(port = 5000)
