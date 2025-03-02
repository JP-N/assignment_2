from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import requests

app = FastAPI(title="US Population")
templates = Jinja2Templates(directory="public")

@app.get("/", response_class=HTMLResponse)
async def get_population_data(request: Request):

    api_url = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        # Get the data, format it, reverse it to be chronological type beat
        data = response.json()
        population_data = data.get("data", [])
        population_data.reverse()

        # Extract years and population values
        years = [entry["Year"] for entry in population_data]
        population_values = [entry["Population"] for entry in population_data]
        growth_data = []

        for i in range(1, len(population_values)):
            previous = population_values[i-1]
            current = population_values[i]
            percentage = ((current - previous) / previous) * 100
            growth_data.append(round(percentage, 2))

        # Felt like adding growth to make it more full
        growth_data.insert(0, 0)
        latest_population = population_values[-1]
        latest_year = years[-1]
        formatted_population = f"{latest_population:,}"
        percent_change = growth_data[-1]

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "years": json.dumps(years),
                "population_values": json.dumps(population_values),
                "growth_data": json.dumps(growth_data),
                "latest_population": formatted_population,
                "latest_year": latest_year,
                "percent_change": percent_change
            }
        )

    except Exception as e:
        print('uh oh', e)