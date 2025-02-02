# engie

## How to run and results format

### Directly on the pycharm terminal

In order to run this code, the following commands must be written in the terminal:
<p>
  
<code> python app.py </code>
  
</p>
<p>
  
<code> curl -X POST "http://localhost:8888/productionplan?filename=payload1.json" </code>
  
</p>
On curl, you must put the name of the json file you want to upload. I have included payload1.json, which was given in the statement. In order to use the file, it must be in the same folder.

The results are displayed on the terminal of the python file, as there is no method GET to retrieve the result and show it on the screen.

### Using the Dockerfile (Windows)

Firstly, make sure you have installed the Docker Desktop application and open it.

Then, open your computer terminal and navigate to the folder where the project is located.

Now, write these two lines: 

<code> docker build -t flask-production-plan . </code>
<code> docker run -p 8888:8888 flask-production-plan . </code>

Now, open another terminal and put the following command: 

<code> curl -X POST "http://localhost:8888/productionplan?filename=payload1.json" </code>

The results will be displayed on the terminal.

NOTE: the json is included in the Dockerfile, change the Dockerfile and make sure to have the json in the folder to avoid problems to use other different payloads.

## Basic ideas

The provided code is a Flask application that sets up a REST API endpoint at /productionplan, designed to calculate a power distribution plan based on input data from a JSON file. When a POST request is made, the app retrieves the filename specified in the request's query parameters and checks for its existence. It then loads the JSON data and validates the presence of required fields such as load, fuels, and powerplants, ensuring that the load is positive and that necessary fuel and power plant details are included and valid. The application calculates the cost per megawatt-hour (MWh) for each power plant based on its type and efficiency, sorts the plants by cost, and allocates energy production starting from the cheapest options. If the total load cannot be fully met, it warns the user while returning the production plan as a JSON response. The app is configured to run in debug mode on all network interfaces at port 8888, making it accessible for testing and development.

## Other possible solutions

If more constraints were given, for example of energy per hour, we could use pyomo, a library specialized in optimization problems. 

## Improvements

To show it in a more user-friendly manner, create a GET method that retrieves the results and show them.
