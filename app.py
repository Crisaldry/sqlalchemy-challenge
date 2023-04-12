from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np
import pandas as pd
from sqlalchemy.sql.expression import desc



engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


app = Flask(__name__)
#app.debug = True
#app.run(port=5001)



@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Find the most recent date in the data set.
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.date.fromisoformat(most_recent_date_str)
    one_year_from_recent_date = most_recent_date - dt.timedelta(days=365)
   
    # Perform a query to retrieve the data and precipitation scores
    precipitation_scores = session.query(Measurement.date, Measurement.prcp)\
   .filter(Measurement.date.between(one_year_from_recent_date, most_recent_date))\
   .all()
    precipitation_scores_DF = pd.DataFrame(precipitation_scores)
    precipitation_scores_DF.set_index('date', inplace=True)
    precipitation_scores_DF = precipitation_scores_DF.sort_index()
   
    return jsonify(precipitation_scores_DF.to_json())

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    stations_list = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        stations_list.append(station_dict)
    
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():    
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.date.fromisoformat(most_recent_date_str)
    one_year_from_recent_date = most_recent_date - dt.timedelta(days=365)

    active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(desc(func.count(Measurement.station))).\
        first()[0]
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_station).\
        filter(Measurement.date >= one_year_from_recent_date).\
        order_by(Measurement.date).all()
    temperatures_list = [t[1] for t in results]
    return jsonify(temperatures_list)

if __name__ == "__main__":
    app.run(host='0.0.0.0')