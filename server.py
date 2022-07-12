from http.client import INTERNAL_SERVER_ERROR
import json
from flask import Flask, render_template, request, redirect, flash, url_for, abort
from datetime import date, datetime


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
print("IN APP CLUBS", clubs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST']) # post ou get ?
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html',clubs=clubs, club=club, competitions=competitions)
    except IndexError:
        abort(405)

@app.errorhandler(405)
def email_not_found(e):
    return render_template("email_not_found.html")

@app.route('/book/<competition>/<club>')
# revoir fonction
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    today = datetime.now()
    compDate = datetime.strptime(competition["date"], '%Y-%m-%d %H:%M:%S')
    placesRequired = int(request.form['places'])
    clubPoints = int(club["points"])
    competitionPlaces = int(competition['numberOfPlaces'])
    if today < compDate:
        if clubPoints >= placesRequired:
            if placesRequired <= 12:
                if int(placesRequired) <= competitionPlaces:            
                    competition['numberOfPlaces'] = competitionPlaces -placesRequired
                    club["points"] = clubPoints - placesRequired
                    flash('Great-booking complete !')
                else:
                    flash("Sorry, you can't take more places that are available.")
            else:
                flash("Sorry, you can't take more than 12 places.")
        else:
            flash("Sorry, you can't take more places than you have points.")
    else: 
        flash(f"The competition has already taken place on this date : {compDate}.")
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display

@app.route('/logout')
def logout():
    return redirect(url_for('index'))