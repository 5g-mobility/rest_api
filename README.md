
# 5G Mobility REST API

  

Django application with the REST API for the 5G Mobility project, built with DRF, Celery, Djongo...

In addition to the Django application, the next services are being used:

- MongoDB
- Mongo Express (To easily check the db)
- RabbitMQ (Broker used by Celery)
- Redis (Backend used by Celery)
- Celery Workers (To run the tasks)
- Flower (To monitor the Celery tasks development)

  
  

## **Running**

  

A **Makefile** was created with all the commands needed to run the application. The following will demonstrate the most important.

  

### **Docker Compose**

  

To facilitate, it is being used Docker Compose to run the multiple services.

  

**Run the development environment** 

In the development environment all the services needed for the Django application are started in Docker containers, letting the user run Django on his personal computer. The following command will start the services containers with one Celery worker:

``make dev``

**Run the production environment** 

In the production environment all the services are started on Docker containers. The following command will start the services containers with one Celery worker:

``make prod``

**Run the above with more than one Celery worker**

To customize the number of Celery workers initiated with Docker containers just pass it using the Makefile. The following example will enable 5 Celery workers on the development environment.

``make dev workers=5``
  

**Other useful Make commands**

To make a new Python virtual environment:

``make venv``
  
To make a new Python virtual environment (if needed) and install all the requirements:

``make install``

To make and apply Django migrations:

``make migrate``

To load initial data (fixtures) into the db :

``make fixtures``

To run tests on local computer :

``make test``

To run Django server on local computer :

``make run``
  
