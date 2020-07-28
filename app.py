# import 
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

date_filter = Measurement.date >= '2016-08-23'
station_filter = Measurement.station == 'USC00519281'

###   Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home_page():
    """List all available api routes."""
    return (
        f"<h1>Available Routes:</h1><br>"
        f"<br>"
        f"<strong>/api/v1.0/precipitation</strong><br><br>"
        f"- - - - - Returns the most recent 12 months of precipitation data (2016-08-23 thru 2017-08-23)<br>"
        f"<br><br>"
        f"<strong>/api/v1.0/stations</strong><br><br>"
        f"- - - - - Returns all stations and observation count for each station<br>"
        f"<br><br>"
        f"<strong>/api/v1.0/tobs</strong><br><br>"
        f"- - - - - Returns the Min, Max, and Avg temperature recorded in the most recent 12 months by the most active station<br>"
        f"<br><br>"
        f"<strong>/api/v1.0/yyyy-mm-dd</strong><br><br>"
        f"- - - - - Returns the Min, Max, and Avg temperature recorded between the starting date <strong>yyyy-mm-dd</strong> and 2017-08-23<br>"
        f"<br><br>"
        f"<strong>/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</strong><br><br>"
        f"- - - - - Returns the Min, Max, and Avg temperature recorded between the starting date <strong>yyyy-mm-dd</strong> and end date <strong>yyyy-mm-dd</strong><br>"
        f"- - - - - Date range for available data:  2010-01-01 thru 2017-08-23"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return 12 months of precipitation data"""
    # Query the last 12 months of precipitation scores and sort by date
    results = session.query(Measurement.date, Measurement.prcp).filter(date_filter).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary for the precipitation data
    all_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_precip.append(prcp_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return Station data"""
    # Query and list all stations, observation count and sort by observation count descending
    results = session.query((Measurement.station), func.count(Measurement.station).label('station_count')).\
        group_by(Measurement.station).\
        order_by(desc('station_count')).all()

    session.close()

    # Create a dictionary for the station data
    all_stations = []
    for station, station_count in results:
        station_dict = {}
        station_dict["station_id"] = station
        station_dict["station_observation_count"] = station_count
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tobs data"""
    # Using the most active station from the stations query, list the lowest, highest, 
    # and average temperature over the last 12 months 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(station_filter).filter(date_filter).all()

    session.close()

    # Create a dictionary for the tobs data
    tobs_dict = {}
    tobs_dict["minimum_temp"] = results[0][0]
    tobs_dict["maximum_temp"] = results[0][1]
    tobs_dict["average_temp"] = results[0][2]

    return jsonify(tobs_dict)


@app.route("/api/v1.0/<start>")
def date_start(start):
    """list the lowest, highest, and average temperature starting at <start> date """
    start_date = start

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    start_dict = {}
    start_dict["_start_date"] = start_date
    start_dict["minimum_temp"] = results[0][0]
    start_dict["average_temp"] = results[0][1]
    start_dict["maximum_temp"] = results[0][2]
    
    return jsonify(start_dict)

    #return jsonify({"error": f"Start date {start_date} not found."}), 404


@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start,end):
    """list the lowest, highest, and average temperature starting at <start> date """
    start_date = start
    end_date = end
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    start_end_dict = {}
    start_end_dict["_end_date"] = end_date
    start_end_dict["_start_date"] = start_date
    start_end_dict["minimum_temp"] = results[0][0]
    start_end_dict["average_temp"] = results[0][1]
    start_end_dict["maximum_temp"] = results[0][2]
    
    return jsonify(start_end_dict)


if __name__ == '__main__':
    app.run(debug=True)
