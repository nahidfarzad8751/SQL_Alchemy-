import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Session (link) from Python to the database
session = Session(engine)

#Setup Flask
app = Flask(__name__)


#Flask routes

@app.route("/")
def home ():
    return (
    f'/api/v1.0/precipitation<br/>'
    f'/api/v1.0/stations<br/>'
    f'/api/v1.0/tobs<br/>'
    f'/api/v1.0/temp/start<br/>'
    f'/api/v1.0/temp/start/end'    
    )



@app.route("/api/v1.0/precipitation")
def precipitation():    
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
    date = session.query(Measurement.date).order_by((Measurement.date.desc())).first()[0]
    prev_year = dt.datetime.strptime(date , '%Y-%m-%d') - dt.timedelta(days=365)
    last_12_months = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
     
    prcp = list(np.ravel(last_12_months))
    return jsonify(prcp)
    


@app.route("/api/v1.0/stations")
def stations():
#Return a JSON list of stations from the dataset. 
    most_active = session.query(Station.station).all()                      
    
    sta = list(np.ravel( most_active))
    return jsonify(sta)



@app.route("/api/v1.0/tobs")
def tobs():
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
    date = session.query(Measurement.date).order_by((Measurement.date.desc())).first()[0]
    prev_year = dt.datetime.strptime(date , '%Y-%m-%d') - dt.timedelta(days=365)
    highest_station = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()
    
    temp_obv = list(np.ravel(highest_station))
    return jsonify(temp_obv)



@app.route("/api/v1.0/temp/<start>")
def start(start = None):
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    temp = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    min_max_avg = list(np.ravel(temp))
    return jsonify(min_max_avg)


@app.route('/api/v1.0/temp/<start>/<end>')
def startend(start = None, end = None ):
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    temp = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    min_max_avg = list(np.ravel(temp))
    return jsonify(min_max_avg)




if __name__ == '__main__':
    app.run(debug=True)