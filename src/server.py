from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
# from sysserology_helpers import read_plates, create_dirs
import pandas as pd

app = Flask(__name__)
api = Api(app)

CORS(app, supports_credentials=True)

# app.config['CORS_SUPPORTS_CREDENTIALS'] = 'True'

@app.route("/")
def hello():
    return jsonify({'text':'Hello World!'})


class Employees(Resource):
    def get(self):
        return {'employees': [{'id':1, 'name':'Balram'},{'id':2, 'name':'Tom'}]}, 201

def read_plates(platefile):
    meta_cols = ['plate', 'well', 'sample_id', 'sample_type',
               'experiment', 'sample_dilution', 'cell_donor', 'expt_id']
    print('reading plates')
    print(platefile)
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

    # pull out the experimental id for the given experiment
    # expt_ids = dict of
    expt_ids = dict(zip(plates.expt_id, plates.experiment))

    return(plates, expt_ids)

class Upload(Resource):
    # def get(self):
    #     return jsonify({'text':'Uploaded something.'})

    def post(self):
        print('called post')
        # print(request.form.get('expt'))
        # print(request.args.get('expt'))
        # print(request.get_data())
        # print(request.stream.read())
        # print(request.headers)

        # print(1)
        # print(request.data)
        # print(2)
        # print(request.args)
        # print(3)
        print(request.form)
        filetype = request.form['file']
        print(filetype)
        # print(request.files)
        # print(4)
        # print(request.values)
        # print(5)
        # print(request.get_json())
        f = request.files['file']
        print(f)


        # x = pd.read_excel(f)
        #
        # print(x.head())
        if(filetype == "plates"):
            print("data uploaded!")

            df = read_plates(f)
            print(df)
        # z = f.read()
        # print(z)
        return jsonify({'text':'Uploaded something.'})
        # return x.to_json(), 201


api.add_resource(Employees, '/employees', methods=['GET']) # Route_1
api.add_resource(Upload, '/upload', methods=['POST']) # suck up the data

if __name__ == '__main__':
     app.run(port = 5000)
