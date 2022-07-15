from genericpath import exists
from flask import Flask
import server
from server import app
from flask import template_rendered
from contextlib import contextmanager
# from tests.conftest import client

# refacto mocker clubs, competitions pour tout le fichier

clubs = [
    {
        "name":"Huge shirts",
        "email":"huge@shirts.com",
        "points":"20"
    },
    {
        "name":"Hungry Birds",
        "email": "admin@hungrybirds.com",
        "points":"4"
    },
    {   
        "name":"Cool buddies",
        "email":"cool@buddies.uk",
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
            "numberOfPlaces": "10"
        },
        {
            "name": "Super competition",
            "date": "2022-10-22 13:30:00",
            "numberOfPlaces": "20"
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
    '''test booking if club is found and competition is found
        should status code OK,
        should redirect to booking.html'''
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

def test_booking_competition_not_found(mocker):
    '''test booking if club is found and competition is not found, 
        should status code OK,
        should redirect to welcome.html'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)
   
        club = clubs[0]
        club_name = club['name']
        competition =         {
            "name": "Badass Tournament",
            "date": "2022-10-22 13:30:00",
            "numberOfPlaces": "1"
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
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)
   
        club = {   "name":"Invisible Club",
        "email": "ghost@club.com",
        "points":"12"
        } # club doesn't exists
        club_name = club['name']
        competition = competitions[0]
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
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)  
        
        competition = competitions[1]
        comp_name = competition['name']
        comp_places = competition['numberOfPlaces']
        club = clubs[0]
        club_name = club['name']
        club_points = club['points']
        placesRequired = 1
        
        response = app.test_client().post('/purchasePlaces', data={"competition":comp_name, "club":club_name, "places": placesRequired}) 
        assert response.status_code  == 200       
        
        template, context = templates[0] 

        assert context['competitions'] == competitions
        assert context['clubs'] == clubs
        assert context['club'] == club
        
        assert club['points'] == int(club_points) - placesRequired
        assert competition['numberOfPlaces'] == int(comp_places) - placesRequired
        
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
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)  
        
        competition = competitions[1]
        comp_name = competition['name']
        comp_places = competition['numberOfPlaces']
        club = clubs[0]
        club_name = club['name']
        club_points = club['points']
        placesRequired = 11
        
        response = app.test_client().post('/purchasePlaces', data={"competition":comp_name, "club":club_name, "places": placesRequired}) 
        assert response.status_code  == 200
        
        assert club['points'] == club_points
        assert competition['numberOfPlaces'] == comp_places
        
        assert b"Sorry, you can&#39;t take more places that are available." in response.data     
        template, context = templates[0] 

        assert context['competitions'] == competitions
        assert context['clubs'] == clubs
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
    
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)  
        
        competition = competitions[2]
        comp_name = competition['name']
        comp_places = competition['numberOfPlaces']
        club = clubs[0]
        club_name = club['name']
        club_points = club['points']
        placesRequired = 13
        
        response = app.test_client().post('/purchasePlaces', data={"competition":comp_name, "club":club_name, "places": placesRequired}) 
        assert response.status_code  == 200
        
        assert club['points'] == club_points
        assert competition['numberOfPlaces'] == comp_places

        assert b"Sorry, you can&#39;t take more than 12 places." in response.data     
        template, context = templates[0] 

        assert context['competitions'] == competitions
        assert context['clubs'] == clubs
        assert context['club'] == club
        
        assert template.name == 'welcome.html'

def test_not_enough_points_to_buy_required_places(mocker):
    ''' test purchase places 
        when placesRequired > club points, 
        should unallowed transaction,
        should flash correct message,
        should not change club points and competition places, 
        should status code OK 
        should redirect to welcome.html'''
    with captured_templates(app) as templates:
        
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)  
        
        competition = competitions[1]
        comp_name = competition['name']
        comp_places = competition['numberOfPlaces']
        club = clubs[1]
        club_name = club['name']
        club_points = club['points']
        placesRequired = 6
        
        response = app.test_client().post('/purchasePlaces', data={"competition":comp_name, "club":club_name, "places": placesRequired}) 
        assert response.status_code  == 200 
        
        assert club['points'] == club_points
        assert competition['numberOfPlaces'] == comp_places
        
        assert b"Sorry, you can&#39;t take more places than you have points." in response.data     
        template, context = templates[0] 

        assert context['competitions'] == competitions
        assert context['clubs'] == clubs
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
        mocker.patch.object(server, 'clubs', clubs)
        mocker.patch.object(server, 'competitions', competitions)  
        
        competition = competitions[0]
        comp_name = competition['name']
        comp_places = competition['numberOfPlaces']
        club = clubs[1]
        club_name = club['name']
        club_points = club['points']
        placesRequired = 1
        
        response = app.test_client().post('/purchasePlaces', data={"competition":comp_name, "club":club_name, "places": placesRequired}) 
        assert response.status_code  == 200 
        
        assert club['points'] == club_points
        assert competition['numberOfPlaces'] == comp_places
        assert b"The competition has already taken place on this date" in response.data     
        template, context = templates[0] 

        assert context['competitions'] == competitions
        assert context['clubs'] == clubs
        assert context['club'] == club
        
        assert template.name == 'welcome.html'
    

# questions
'''
pourquoi plusieurs templates ?
[(<Template 'welcome.html'>, 
{'clubs': [{'name': 'Huge shirts', 'email': 'huge@shirts.com', 'points': 10}, {'name': 'Hungry Birds', 'email': 'admin@hungrybirds.com', 'points': '4'}, {'name': 'Cool buddies', 'email': 'cool@buddies.uk', 'points': '12'}], 'club': {'name': 'Huge shirts', 'email': 'huge@shirts.com', 'points': 10}, 'competitions': [{'name': 'Magic festival', 'date': '2020-03-27 10:00:00', 'numberOfPlaces': '25'}, {'name': 'Crazy Tournament', 'date': '2022-10-22 13:30:00', 'numberOfPlaces': 10}], 'g': <flask.ctx._AppCtxGlobals object at 0x1021d3d60>, 
'request': <Request 'http://localhost/purchasePlaces' [POST]>, 'session': <SecureCookieSession {}>})] (<Template 'welcome.html'>, {'clubs': [{'name': 'Huge shirts', 'email': 'huge@shirts.com', 'points': 10}, {'name': 'Hungry Birds', 'email': 'admin@hungrybirds.com', 'points': '4'}, {'name': 'Cool buddies', 'email': 'cool@buddies.uk', 'points': '12'}], 'club': {'name': 'Huge shirts', 'email': 'huge@shirts.com', 'points': 10}, 'competitions': [{'name': 'Magic festival', 'date': '2020-03-27 10:00:00', 'numberOfPlaces': '25'}, {'name': 'Crazy Tournament', 'date': '2022-10-22 13:30:00', 'numberOfPlaces': 10}], 'g': <flask.ctx._AppCtxGlobals object at 0x1021d3d60>, 'request': <Request 'http://localhost/purchasePlaces' [POST]>, 'session': <SecureCookieSession {}>})
'''