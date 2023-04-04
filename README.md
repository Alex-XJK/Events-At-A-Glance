# COMS 4111 Web Front-End Project

## Events At A Glance

Python Flask and PostgreSQL based one-stop campus event managing and searching platform.

> Author: Xuande Feng (xf2219); Jiakai Xu (ax2155)  
> Date: April 1, 2023

## PostgreSQL account

ax2155

## Website URL

http://ap.cs.columbia.edu/~ax2155/database  
Click on this link will redirect you to our project page.

## Environment requirements

- Development environment: Python 3.10.4
- Production environment: Python 3.8.10

## Proposal description  
In the webpage front end implementation, we covered most of the functionalities that were described in the initial plan that are directly related to the database management system. For instance, we designed a query page that allows users to check the events based on their given restrictions, while we also guaranteed the robustness by returning all events when the users do not specify any restrictions. In addition, we also implemented a create page to create new events and insert them into the database. The robustness is guaranteed through redirections: if a specific time slot of a specific room has been assigned to an existing event, then it will automatically redirect the user to an reminding page and then help the user to get back to the homepage. We also implemented the trigger-style functionality to automatically insert an event_occupancy and an location_occupancy so that the upcoming events will not be able to select this occupied time slot. We did not accomplish some of the functionalities that are not directly related to the database management system including user authentications and calender file downloading. The main reason is that both of us do not have much prior experience in doing these, and they may require too much efforts for us to improve the overall quality of our web front end project.  

## Interesting page examples

We have two webpages that contains interaction between users and our backend, and we first introduct the interesting part of the query page: its robustness. We implement different types of querying: exact select or fuzzy select. Exact select requires the database to search with exactly the provided event title whereas the fuzzy select encourage the database to search event with title that contains the keyword. In addition, when a specific search attribute is missing from the user, our backend will automatically omit it and give a ‘broader’ search. Briefly speaking, the users can accomplish any applausible querying through our query page.  
  
The second page is our create page, and the interesting part is that we give the users full control over attributes except for several mandatory fields(correponding to the not-null attributes in our events table). In addition, when a valid new event is created, the corresponding event_occupancy and location_occupancy will be created simultaneously in our backend, accomplishing the functionality of ‘Trigger’ in database management system.  

---
