import os
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route('/productionplan', methods=['POST'])
def production_plan():
    # Get the payload filename from the request body
    payload_file = request.args.get('filename')

    # Check if a filename was provided
    if not payload_file:
        return jsonify({"error": "No filename provided"}), 400

    # Check if the file exists
    if not os.path.exists(payload_file):
        return jsonify({"error": "File not found"}), 404

    # Load the payload from the provided file
    with open(payload_file, 'r') as f:
        data = json.load(f)

    # Before extracting the values, we should check that the fields are present
    required_fields = ['load', 'fuels', 'powerplants']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "A field is missing"}), 400

    # Extract values from payload
    load = data['load']
    fuels = data['fuels']
    powerplants = data['powerplants']

    # Now that we have the values, let's take into account other errors

    # First, check that the load is positive
    if load < 0:
        return jsonify({"error": "Invalid 'load'. It must be a positive number."}), 400

    # We also have to check the powerplants and values of the fuel, the necessary ones have
    # to appear and the fuel must be positive
    required_fuels = ["gas(euro/MWh)", "kerosine(euro/MWh)", "co2(euro/ton)", "wind(%)"]
    for fuel in required_fuels:
        if fuel not in fuels:
            return jsonify({"Missing fuel data"}), 400
        if fuels[fuel] < 0:
            return jsonify({"error": "Fuel must be positive"}), 400

    # The necessary fields have to appear in the powerplants, also the pmax cannot be less than the pmin
    for plant in powerplants:
        if 'type' not in plant or 'pmax' not in plant or 'pmin' not in plant or 'efficiency' not in plant or 'name' not in plant:
            return jsonify(
                {"error": "Each powerplant must contain 'type', 'pmax', 'pmin', 'efficiency', and 'name'."}), 400
        if plant["pmax"] < plant["pmin"]:
            return jsonify({"error": "There is a 'pmax' less than 'pmin'."}), 400

    # Calculate power distribution based on the algorithm
    production_plan = calculate_production_plan(load, fuels, powerplants)

    # Return the production plan as a JSON response
    return jsonify(production_plan)




def calculate_production_plan(load, fuels, powerplants):
    """
    Calculates the power distribution

    The idea is to have the cheapest possibility so first we must calculate the costs of each one, then we sort them by
    cost and then we calculate how much energy each plant is going to produce, taking into account CO2 emissions for
    gas-fired powerplants.
    """

    # Step 1: cost of each plant

    for plant in powerplants:
        if plant["type"] == "windturbine":
            # Wind turbines have zero cost, so they will always be the first ones in the list, all the energy they
            # can produce will be produced

            plant["cost_per_mwh"] = 0  # We will keep the costs in cost_per_mwh

            # As the wind percentage is given, we have to calculate the amount of energy the plant
            # will be able to produce based on the amount of wind

            plant["pmax"] = plant["pmax"] * (fuels["wind(%)"] / 100)

        elif plant["type"] == "gasfired":
            # The total cost is the division of the price of the gas and the efficiency of the plant

            base_cost = fuels["gas(euro/MWh)"] / plant["efficiency"]

            # Adding the cost of CO2 emissions, 0.3 tons of CO2 per MWh generated
            co2_cost = 0.3 * fuels["co2(euro/ton)"]

            # The final cost is the sum of both
            plant["cost_per_mwh"] = base_cost + co2_cost

        elif plant["type"] == "turbojet":
            # The total cost is the division of the price of the kerosine and the efficiency of the plant

            plant["cost_per_mwh"] = fuels["kerosine(euro/MWh)"] / plant["efficiency"]

    # Step 2: we will sort the plants by the cost, as we will use the cheapest ones first

    powerplants = sorted(powerplants, key=lambda x: x["cost_per_mwh"])

    # Step 3: calculate the energy based on the remaining one we have to take, based on the prices
    production_plan = []  # Store results
    remaining_load = load

    for plant in powerplants:
        # Calculate the energy depending on the remaining one and the type

        if plant["type"] == "windturbine":
            # We will always use this first as they are cost 0, so use the whole energy they have, or the remaining one
            # in the load

            energy = min(plant["pmax"], remaining_load)

        else:
            # These ones depend on the pmax and pmin, if there is not enough energy because of pmin, we have to go to
            # the next one. If there is, we will calculate the minimum between the remaining load and the amount of
            # energy

            if remaining_load >= plant["pmin"]:
                energy = min(plant["pmax"], remaining_load)
            else:
                energy = 0

        # We subtract the energy from the remaining load
        remaining_load -= energy

        # Append this iteration's result
        production_plan.append({"name": plant["name"], "p": round(energy, 1)})

    # If the load could not be fully met, raise an error
    if remaining_load > 0:
        print("Unable to meet the load")

    return production_plan




if __name__ == '__main__':
    # Set `host='0.0.0.0'` to listen on all available IP addresses
    # Port = 8888 as asked in the problem
    app.run(debug=True, host='0.0.0.0', port=8888)


# TO RUN IT
# python app.py
# curl -X POST "http://localhost:8888/productionplan?filename=payload1.json"