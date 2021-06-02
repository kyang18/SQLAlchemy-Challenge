from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np
import pandas as pd
from datetime import timedelta

#Database setup
engine  = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#Flask setup
app = Flask(__name__)

latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
latest_date = list(np.ravel(latest_date))[0]

latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')

latest_Year = int(dt.datetime.strftime(latest_date, '%Y'))
latest_Month = int(dt.datetime.strftime(latest_date, '%m'))
latest_Day = int(dt.datetime.strftime(latest_date, '%d'))

yearBefore = dt.date(latest_Year, latest_Month, latest_Day) - dt.timedelta(days=365)

#Flask Routes
#1.'/'& Home page. List all routes that are available.
@app.route("/")
def Home():
    return (
        f"Available routes<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/startdate <br/>"
        f"/api/v1.0/startdate/enddate<br/><br/><br/>"
    )

# 2. Convert the query results to a Dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def percipitation():

    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipData = []
    for result in results:
        precipData = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipData)

    return jsonify(precipData)

# 3. 
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

# 4.
@app.route("/api/v1.0/tobs")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

 #5.   
@app.route("/api/v1.0/temp/<start>")
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


#6.
@app.route("/api/v1.0/temp/<start>/<end>")
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


if __name__ == '__main__':
    app.run()


