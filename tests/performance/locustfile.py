import locust
from locust import HttpUser, task

class ProjectPerfTest(HttpUser):
    
    email = "kate@shelifts.co.uk"
    comp_name = "Fall Classic"
    club_name = "She Lifts"
    
    def on_start(self):
        self.client.post("/show-summary", {
            "email": self.email
        })
        
    @task
    def home(self):
        response = self.client.get("/")
          
    @task
    def login(self):
        response = self.client.post("/show-summary", {"email": self.email})
        
    @task 
    def book(self):
        response = self.client.get(f'/book/{self.comp_name}/{self.club_name}')
    
    @task()
    def purchase_places(self):
        response = self.client.post('/purchase-places', {"club":self.club_name, "competition":self.comp_name, "places": 1})
        
    def on_stop(self):
        self.client.get("/logout")
