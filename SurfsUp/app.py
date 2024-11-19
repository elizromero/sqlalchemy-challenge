##Flask api 

# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# **Sessions were created for each function def

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def welcome():
    """List all available routes."""
    return (
        f"This is my climate API!<br/>"
        f"The available routes are:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returning the last 12 months of precipitation data as JSON."""
    session = Session(engine)
    # Find the most recent date (max)
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    one_year_ago = recent_date - dt.timedelta(days=365)

    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert to dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

#Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Returning a JSON list of stations."""
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    # Ruturning result into a list
    stations_list = [station[0] for station in results]
    return jsonify(stations_list)


#Observations (tobs) route
@app.route("/api/v1.0/tobs")
def tobs():
    """Returning a JSON list of temperature observations for the previous year."""
    session = Session(engine)
    # Find the most active station
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )

    # Calculate the date 12 months ago from the last date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    one_year_ago = recent_date - dt.timedelta(days=365)

    # Query the data
    results = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )
    session.close()

    # Results into a list
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    return jsonify(tobs_data)


#statiscis from temperatures
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return min, avg, and max temperatures for a given date range."""
    session = Session(engine)

    # Creating the queries for statistics
    if not end:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        ).filter(Measurement.date >= start).all()
    else:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Returning results
    stats_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2],
    }
    return jsonify(stats_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)


