from ... import server
from ...server import app
from flask import template_rendered
from contextlib import contextmanager
from ..mock import CLUBS, COMPETITIONS


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

def test_login_and_logout(mocker):
    '''test that connexion work and doesn't change points'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
        credentials = {'email':'huge@shirts.com'}
        
        club = CLUBS[0]
        
        response = app.test_client().post('/show-summary', data = credentials) 
        assert response.status_code == 200  
        assert templates[0][0].name == 'welcome.html'
        
        club_points = club['points']
        
        response = app.test_client().get('/logout')       
        assert response.status_code == 302
        
        response = app.test_client().post('/show-summary', data = credentials) 
        assert response.status_code == 200  
        assert templates[1][0].name == 'welcome.html' 
        
        assert club['points'] == club_points
        
        
def test_login_and_booking(mocker):
    '''test login and booking'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
        credentials = {'email':'huge@shirts.com'}
        
        response = app.test_client().post('/show-summary', data = credentials) 
        assert response.status_code == 200  
        assert templates[0][0].name == 'welcome.html' 
        
        club = CLUBS[0]
        club_name = club['name']
        competition = COMPETITIONS[0]
        comp_name = competition['name']
        
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        assert templates[1][0].name == 'booking.html' 
            
def test_booking_and_purchase_places(mocker):
    '''test booking and purchase places'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS) 
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
   
        club = CLUBS[0]
        club_name = club['name']
        club_points = club['points']
        competition = COMPETITIONS[1]
        comp_name = competition['name']
        comp_places = competition['number_of_places']
        places_required = 2
        
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        assert templates[0][0].name == 'booking.html' 
        
        response = app.test_client().post('/purchase-places', data={"competition":comp_name, "club":club_name, "places": places_required})
        assert response.status_code  == 200
        assert club['points'] == int(club_points) - places_required
        assert competition['number_of_places'] == int(comp_places) - places_required
        
        assert templates[1][0].name == 'welcome.html'
        

