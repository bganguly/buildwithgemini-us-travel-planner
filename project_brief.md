# My agent: US Travel & Motorcycle Planner (US Voyage Concierge)

One-liner: A conversational travel planner agent that helps travelers design, budget, and visualize multi-day US road trips, scenic motorcycle routes, and local motorcycle/bike rental options complete with rich destination cards and landmark imagery.

Tool coverage:
- Memory: User travel preferences (budget level, riding experience/license level, preferred pace, departure city, dietary restrictions, favorite activity types like scenic highway rides, national parks, hiking)
- Tools: Destination lookup, weather forecast tool, motorcycle/bike rental search (e.g. EagleRider, local shops), scenic riding route finder, and multi-state itinerary generator
- Catalog/UI: Destination & route cards (e.g. Utah's Scenic Byway 12, Route 66, Grand Canyon), rental bike options, and structured daily itinerary tables
- Image gen: AI-generated destination preview photos, motorcycle route postcards, and scenic highlight cards for itinerary stops (e.g. Zion, Bryce, Grand Canyon)
- Sandbox: Trip budget calculator (estimating bike rental costs, gear, fuel, lodging, meals, and park entry fees) and riding distance/time math

Core rails (everyone): memory, tools, eval, deploy, frontend
My stretch menu (pick later): A2UI (rich itinerary cards & tables), Image Generation (destination previews), Sandbox (budget calculator)
First eval question: "Plan a 7-day motorcycle road trip from Salt Lake City or Las Vegas covering Utah's Scenic Byway 12 and the Grand Canyon, including local motorcycle rental options and daily riding distance breakdowns under $2,500."
