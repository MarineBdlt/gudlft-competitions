from genericpath import exists
import json, sys
from flask import Flask
import server
from server import app
from flask import template_rendered
from contextlib import contextmanager
# from tests.conftest import client

clubs = [
    {
        "name":"Huge shirts",
        "email":"huge@shirts.com",
        "points":"13"
    },
    {
        "name":"Hungry Birds",
        "email": "admin@hungrybirds.com",
        "points":"4"
    },
    {   "name":"Cool buddies",
        "email": "cool@buddies.uk",
        "points":"12"
    }
]

competitions = [
        {
            "name": "Magic festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Crazy Tournament",
            "date": "2022-10-22 13:30:00",
            "numberOfPlaces": "13"
        }
    ]


@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)    
        
def test_index_should_status_code_ok():
    with captured_templates(app) as templates:
        response = app.test_client().get('/')
        print("templates", templates)
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'
        
def test_email_not_found_should_status_code_ok(mocker):
    '''test if user redirected if email not found'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)
        
        response = app.test_client().post('/showSummary', data = {'email':'igfhuefn'})
        assert response.status_code == 200       
        assert templates[0][0].name == 'email_not_found.html'
        
        response = app.test_client().post('/showSummary', data = {'email': ''})
        assert response.status_code == 200
        assert templates[0][0].name == 'email_not_found.html'
       
def test_logging_should_status_code_ok(mocker):
    '''test if mail adress is recognized to log the user'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)    
        data = {'email':'huge@shirts.com'}
        
        response = app.test_client().post('/showSummary', data = data)
        assert response.status_code == 200
        template, context = templates[0]
        assert context['clubs'] == clubs
        assert context['competitions'] == competitions
        assert context['club']['email'] == data['email']
        
        assert template.name == 'welcome.html'

def test_booking_should_status_code_ok(mocker):
    '''test if club is found and competition is found'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'clubs', clubs) # utile ?
        mocker.patch.object(server, 'competitions', competitions)
   
        club = clubs[0]
        club_name = club['name']
        competition = competitions[0]
        comp_name = competition['name']
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        
        template, context = templates[0]
        assert context['club'] == club
        assert context['competition'] == competition
        
        assert template.name == 'booking.html'

def test_booking_failed_competition_not_found(mocker):
    '''test if club is found and competition is found'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)
   
        club = clubs[0]
        club_name = club['name']
        competition =         {
            "name": "Badass Tournament",
            "date": "2022-10-22 13:30:00",
            "numberOfPlaces": "1"
        }
        comp_name = competition["name"]
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        
        template, context = templates[0]
        print("CONTEXT", context)       
        assert context['club'] == club
        assert context['competitions'] == competitions 
        
        assert template.name == 'welcome.html'