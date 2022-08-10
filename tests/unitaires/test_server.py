from genericpath import exists
from flask import Flask
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
        
def test_index_should_status_code_ok():
    with captured_templates(app) as templates:
        response = app.test_client().get('/')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'
        
def test_email_not_found_should_status_code_ok(mocker):
    '''test if user redirected if email not found'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
        
        response = app.test_client().post('/show-summary', data = {'email':'igfhuefn'})
        assert response.status_code == 200       
        assert templates[0][0].name == 'email_not_found.html'
        
def test_email_empty_should_status_code_ok(mocker):
    '''test if user redirected if email is empty'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
        
        response = app.test_client().post('/show-summary', data = {'email':''})
        assert response.status_code == 200       
        assert templates[0][0].name == 'email_not_found.html'
        
       
def test_logging_should_status_code_ok(mocker):
    '''test if mail adress is recognized to log the user'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)    
        data = {'email':'huge@shirts.com'}
        
        response = app.test_client().post('/show-summary', data = data)
        assert response.status_code == 200
        template, context = templates[0]
        assert context['clubs'] == CLUBS
        assert context['competitions'] == COMPETITIONS
        assert context['club']['email'] == data['email']
        
        assert template.name == 'welcome.html'

def test_booking_should_status_code_ok(mocker):
    '''test booking if club is found and competition is found
        should status code OK,
        should redirect to booking.html'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS) # utile ?
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
   
        club = CLUBS[0]
        club_name = club['name']
        competition = COMPETITIONS[0]
        comp_name = competition['name']
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        
        template, context = templates[0]
        assert context['club'] == club
        assert context['competition'] == competition
        
        assert template.name == 'booking.html'

def test_booking_competition_not_found(mocker):
    '''test booking if club is found and competition is not found, 
        should status code OK,
        should redirect to welcome.html'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
   
        club = CLUBS[0]
        club_name = club['name']
        competition =         {
            "name": "Badass Tournament",
            "date": "2022-10-22 13:30:00",
            "number_of_places": "1"
        } # competition doesn't exists
        comp_name = competition["name"]
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        
        template, context = templates[0]     
        assert context['club'] == club
        
        assert template.name == 'welcome.html'
        
def test_booking_failed_club_not_found(mocker):
    '''test booking if club is not found and competition is found
        should status code OK
        should redirect to index.html'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)
   
        club = {   "name":"Invisible Club",
        "email": "ghost@club.com",
        "points":"12"
        } # club doesn't exists
        club_name = club['name']
        competition = COMPETITIONS[0]
        comp_name = competition["name"]
        
        response = app.test_client().get(f'/book/{comp_name}/{club_name}')
        assert response.status_code == 200
        
        template, context = templates[0]      
        
        assert template.name == 'index.html'
        
def test_purchase_places_ok(mocker):
    ''' test purchase places 
        when all conditions are reunited to purchase places
        should change club points and competition places 
        should redirect to booking.html
        should status code OK
        should redirect to welcome.html '''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)  
        
        competition = COMPETITIONS[1]
        comp_name = competition['name']
        comp_places = competition['number_of_places']
        club = CLUBS[0]
        club_name = club['name']
        club_points = club['points']
        places_required = 1
        
        response = app.test_client().post('/purchase-places', data={"competition":comp_name, "club":club_name, "places": places_required}) 
        assert response.status_code  == 200       
        
        template, context = templates[0] 

        assert context['competitions'] == COMPETITIONS
        assert context['clubs'] == CLUBS
        assert context['club'] == club
        
        assert club['points'] == int(club_points) - places_required
        assert competition['number_of_places'] == int(comp_places) - places_required
        
        assert template.name == 'welcome.html'
        
def test_not_enough_available_places(mocker):
    ''' test purchase places 
        when there is less available places than required, 
        should unallowed transaction,
        should not change club points and competition places,
        should flash correct message, 
        should status code OK 
        should redirect to welcome.html '''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)  
        
        competition = COMPETITIONS[1]
        comp_name = competition['name']
        comp_places = competition['number_of_places']
        club = CLUBS[0]
        club_name = club['name']
        club_points = club['points']
        places_required = 11
        
        response = app.test_client().post('/purchase-places', data={"competition":comp_name, "club":club_name, "places": places_required}) 
        assert response.status_code  == 200
        
        assert club['points'] == club_points
        assert competition['number_of_places'] == comp_places
        
        assert b"Sorry, you can&#39;t take more places that are available." in response.data     
        template, context = templates[0] 

        assert context['competitions'] == COMPETITIONS
        assert context['clubs'] == CLUBS
        assert context['club'] == club
        
        assert template.name == 'welcome.html'
        
def test_more_than_max_places_required(mocker):
    ''' test purchase places 
        when places required exceeds maximum allowed, 
        should unallowed transaction,
        should not change club points and competition places,
        should flash correct message 
        should status code OK 
        should redirect to welcome.html'''
    
    with captured_templates(app) as templates:
    
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)  
        
        competition = COMPETITIONS[2]
        comp_name = competition['name']
        comp_places = competition['number_of_places']
        club = CLUBS[0]
        club_name = club['name']
        club_points = club['points']
        places_required = 13
        
        response = app.test_client().post('/purchase-places', data={"competition":comp_name, "club":club_name, "places": places_required}) 
        assert response.status_code  == 200
        
        assert club['points'] == club_points
        assert competition['number_of_places'] == comp_places

        assert b"Sorry, you can&#39;t take more than 12 places." in response.data     
        template, context = templates[0] 

        assert context['competitions'] == COMPETITIONS
        assert context['clubs'] == CLUBS
        assert context['club'] == club
        
        assert template.name == 'welcome.html'

def test_not_enough_points_to_buy_required_places(mocker):
    ''' test purchase places 
        when places_required > club points, 
        should unallowed transaction,
        should flash correct message,
        should not change club points and competition places, 
        should status code OK 
        should redirect to welcome.html'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)  
        
        competition = COMPETITIONS[1]
        comp_name = competition['name']
        comp_places = competition['number_of_places']
        club = CLUBS[1]
        club_name = club['name']
        club_points = club['points']
        places_required = 6
        
        response = app.test_client().post('/purchase-places', data={"competition":comp_name, "club":club_name, "places": places_required}) 
        assert response.status_code  == 200 
        
        assert club['points'] == club_points
        assert competition['number_of_places'] == comp_places
        
        assert b"Sorry, you can&#39;t take more places than you have points." in response.data     
        template, context = templates[0] 

        assert context['competitions'] == COMPETITIONS
        assert context['clubs'] == CLUBS
        assert context['club'] == club
        
        assert template.name == 'welcome.html'
        

def test_competition_is_over(mocker):
    """ test purchase places
        when competition already happened
        should unallowed transaction,
        should flash correct message,
        should not change club points and competition places, 
        should status code OK 
        should redirect to welcome html"""
    with captured_templates(app) as templates:
        mocker.patch.object(server, 'CLUBS', CLUBS)
        mocker.patch.object(server, 'COMPETITIONS', COMPETITIONS)  
        
        competition = COMPETITIONS[0]
        comp_name = competition['name']
        comp_places = competition['number_of_places']
        club = CLUBS[1]
        club_name = club['name']
        club_points = club['points']
        places_required = 1
        
        response = app.test_client().post('/purchase-places', data={"competition":comp_name, "club":club_name, "places": places_required}) 
        assert response.status_code  == 200 
        
        assert club['points'] == club_points
        assert competition['number_of_places'] == comp_places
        assert b"The competition has already taken place on this date" in response.data     
        template, context = templates[0] 

        assert context['competitions'] == COMPETITIONS
        assert context['clubs'] == CLUBS
        assert context['club'] == club
        
        assert template.name == 'welcome.html'
    