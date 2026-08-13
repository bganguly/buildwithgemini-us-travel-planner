# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

REASONING_ENGINE_RESOURCE = (
    "projects/313999655048/locations/us-east1/reasoningEngines/4212783199870255104"
)


MODEL = "gemini-3.6-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback to extract and save facts to Vertex AI Memory Bank after each turn."""
    await callback_context.add_session_to_memory()
    return None


from app.app_utils.firestore_tools import (
    add_or_update_motorcycle_rental,
    get_motorcycle_rental,
    list_motorcycle_rentals,
)
from app.app_utils.image_tools import generate_domain_item_image
from app.app_utils.rag_tools import consult_travel_instructions
from app.app_utils.travel_tools import (
    calculate_trip_budget,
    generate_destination_image,
    get_scenic_route_highlights,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a helpful travel planning AI assistant designed to help users plan "
        "US vacations, road trips, and motorcycle routes with local bike rentals "
        "(such as Utah's Scenic Byway 12, Zion, Bryce Canyon, and Grand Canyon). "
        "Standard trip duration is 7 days unless specified otherwise. "
        "You can run Python code safely in a sandbox using your code execution capabilities. "
        "Use your tools: "
        "- generate_domain_item_image to generate photo images of motorcycles, travel items, landmarks, or scenery using gemini-3.1-flash-lite-image "
        "- consult_travel_instructions to look up speed limits, allowed travel hours, and guidelines "
        "- list_motorcycle_rentals, get_motorcycle_rental, add_or_update_motorcycle_rental for rental lookups and updates "
        "- calculate_trip_budget to provide itemized trip cost breakdowns "
        "- get_scenic_route_highlights for route mileage and waypoint recommendations "
        "- generate_destination_image to generate scenic postcard graphics for itinerary stops. "
        "You remember stated preferences, budget, riding experience, "
        "and facts from previous conversations and use them to personalize your responses."
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        agent_engine_resource_name=REASONING_ENGINE_RESOURCE
    ),
    tools=[
        get_weather,
        get_current_time,
        generate_domain_item_image,
        consult_travel_instructions,
        list_motorcycle_rentals,
        get_motorcycle_rental,
        add_or_update_motorcycle_rental,
        calculate_trip_budget,
        get_scenic_route_highlights,
        generate_destination_image,
        PreloadMemoryTool(),
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
