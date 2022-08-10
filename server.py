from http.client import INTERNAL_SERVER_ERROR
import json
from flask import Flask, render_template, request, redirect, flash, url_for, abort
from datetime import date, datetime
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CLUBS_PATH = os.path.join(ROOT_DIR, 'clubs.json')
COMPETITIONS_PATH = os.path.join(ROOT_DIR, 'competitions.json')

def load_clubs():   
    with open(CLUBS_PATH) as c:
         list_of_clubs = json.load(c)['clubs']
         return list_of_clubs


def load_competitions():
    with open(COMPETITIONS_PATH) as comps:
         list_of_competitions = json.load(comps)['competitions']
         return list_of_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

COMPETITIONS = load_competitions()
CLUBS = load_clubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/show-summary',methods=['POST'])
def show_summary():
    try:
        print(CLUBS)
        club = [club for club in CLUBS if club['email'] == request.form['email']][0] 
        return render_template('welcome.html', clubs=CLUBS, club=club, competitions=COMPETITIONS)
    except IndexError:
        abort(405)

@app.errorhandler(405)
def email_not_found(e):
    return render_template("email_not_found.html")

@app.route('/book/<comp_name>/<club_name>')
def book(comp_name,club_name):
    found_club = next((c for c in CLUBS if c['name'] == club_name), None)
    found_competition = next((c for c in COMPETITIONS if c['name'] == comp_name), None)
    if not found_club:
        return render_template('index.html')
    if not found_competition:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', clubs=CLUBS, club=found_club, competitions=COMPETITIONS)
    else:
        return render_template('booking.html', club=found_club, competition=found_competition)


@app.route('/purchase-places',methods=['POST'])
def purchase_places():
    competition = [c for c in COMPETITIONS if c['name'] == request.form['competition']][0]
    club = [c for c in CLUBS if c['name'] == request.form['club']][0]
    today = datetime.now()
    comp_date = datetime.strptime(competition["date"], '%Y-%m-%d %H:%M:%S')
    places_required = int(request.form['places'])
    club_points = int(club["points"])
    competition_places = int(competition['number_of_places'])
    if today < comp_date:
        if club_points >= places_required:
            if places_required <= 12:
                if int(places_required) <= competition_places:            
                    competition['number_of_places'] = competition_places - places_required
                    club["points"] = club_points - places_required
                    flash('Great-booking complete !')
                else:
                    flash("Sorry, you can't take more places that are available.")
            else:
                flash("Sorry, you can't take more than 12 places.")
        else:
            flash("Sorry, you can't take more places than you have points.")
    else: 
        flash(f"The competition has already taken place on this date : {comp_date}.")
    return render_template('welcome.html', clubs=CLUBS, club=club, competitions=COMPETITIONS)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))