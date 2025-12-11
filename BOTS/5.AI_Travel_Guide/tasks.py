from crewai import Task
from datetime import datetime, date
from typing import Union, Iterable

DateLike = Union[date, datetime, str]


def _to_date(d: DateLike) -> date:
    """Normalize input to a date object. Accepts date, datetime, or ISO-like string."""
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        # try parsing ISO-ish strings
        try:
            return datetime.fromisoformat(d).date()
        except Exception:
            raise ValueError(f"Unrecognized date string: {d!r}. Use YYYY-MM-DD or ISO datetime.")
    raise TypeError(f"Unsupported date type: {type(d)}")


def _validate_dates(date_from: DateLike, date_to: DateLike) -> tuple[date, date]:
    d_from = _to_date(date_from)
    d_to = _to_date(date_to)
    if d_to < d_from:
        raise ValueError("date_to must be the same or later than date_from")
    return d_from, d_to


def _join_list(items: Iterable[str]) -> str:
    return ", ".join(str(x) for x in items)


def location_task(agent, from_city: str, destination_city: str, date_from: DateLike, date_to: DateLike) -> Task:
    """
    Task for Location Expert to research destination information.
    """
    d_from, d_to = _validate_dates(date_from, date_to)

    description=f"""
    Gather up-to-date travel details for a trip from {from_city} to {destination_city} between {date_from} and {date_to}.

    Use web_search_tool for each part of this job. Don't rely on assumptions or cached knowledge.

    Focus on:
    1. Visa rules for travelers coming from {from_city} to {destination_city}
    2. Flight options, typical prices, and travel times
    3. Local transport in {destination_city} — metro, buses, taxis, ride-share
    4. Expected weather during the travel window
    5. Current safety advisories
    6. Currency, exchange rates, and approximate daily costs
    """
    
    expected_output="""
    A clear travel brief that includes:
    - Visa requirements and any steps needed to apply
    - Flight choices with estimated pricing
    - A practical guide to getting around the city, with sample fares
    - Weather expectations and what to pack
    - Safety notes and key emergency contacts
    - Budget ranges for lodging, food, and activities
    - Currency details and sensible exchange advice
    """
    
    return Task(description=description, expected_output=expected_output, agent=agent)


def guide_task(agent, destination_city: str, interests: Iterable[str], date_from: DateLike, date_to: DateLike) -> Task:
    """
    Task for Local Guide Expert to provide recommendations.
    """
    d_from, d_to = _validate_dates(date_from, date_to)
    interests_str = _join_list(interests)

    description = f"""
    Act as a well-informed local guide for {destination_city} and build personalized recommendations
    for a traveler interested in: {interests}.

    Trip dates: {d_from} → {d_to}

    Use web_search_tool for all current data — reviews, hours, closures, prices, and date-specific events.

    Provide:

    1. Top Attractions
    • 10–15 must-see spots that genuinely match the traveler’s interests  
    • A short explanation of why each place fits

    2. Local Restaurants
    • 8–10 well-reviewed, authentic places favored by locals  
    • Signature dishes and expected price ranges

    3. Cultural Experiences
    • Museums, theaters, festivals, and any events occurring during the travel dates

    4. Hidden Gems
    • 5–7 lesser-known places locals enjoy

    5. Food Recommendations
    • Specific dishes worth trying and where to find them

    6. Nightlife and Entertainment
    • Bars, clubs, or live-music venues with notes on vibe and typical crowd

    7. Shopping Areas
    • Markets, boutiques, and neighborhoods known for interesting local goods

    Make sure the information reflects current conditions. Note any holiday schedules, temporary closures, or special happenings.
    """

    expected_output = """
    A complete travel guide that includes:
    - 10–15 top attractions with explanations
    - 8–10 restaurant picks with standout dishes
    - Cultural events or festivals during the trip dates
    - 5–7 hidden gems
    - A neighborhood guide with character notes
    - Practical advice on timing, crowd avoidance, and navigation
    - Local customs and etiquette tips
    """

    return Task(description=description, expected_output=expected_output, agent=agent)


def planner_task(context_tasks: Iterable[Task], agent, destination_city: str, interests: Iterable[str],
                 date_from: DateLike, date_to: DateLike) -> Task:
    """
    Task for Travel Planner Expert to create the final itinerary.
    `context_tasks` should contain the results from Location Expert and Local Guide Expert.
    """
    d_from, d_to = _validate_dates(date_from, date_to)
    trip_duration = (d_to - d_from).days + 1
    interests_str = _join_list(interests)

    description=f"""
    Build a complete, day-by-day itinerary for {destination_city} from {date_from} to {date_to}
    ({trip_duration} days).

    Traveler interests: {interests}

    Use insights from the Location Expert and Local Guide Expert already in context.
    IMPORTANT: Use relevant emojis for each section header and activity (e.g., 🏨 for hotel, 🍛 for food, 🚗 for transport) to make the itinerary visually appealing.
    
    Use web_search_tool to confirm all current details — prices, hours, closures, transit info,
    and booking requirements.

    Research and deliver:

    1. Accommodation
    • 3–4 hotel or lodging options with current prices

    2. Daily Itinerary
    • An hour-by-hour plan for every day of the trip

    3. Activity Booking
    • Call out anything that requires advance reservations

    4. Meal Planning
    • Specific places for breakfast, lunch, and dinner

    5. Transportation
    • How to get between activities and realistic travel times

    6. Budget Breakdown
    • Daily and total estimates

    7. Practical Tips
    • Booking links, contacts, and reservation suggestions

    The itinerary should balance activity and downtime, group nearby attractions to reduce travel,
    include weather-friendly backups, consider opening hours and peak times, and stay within a
    reasonable budget.

    Make sure all prices, hours, and booking details reflect current conditions.
    """
    
    expected_output=f"""
    A full travel plan that includes:

    EXECUTIVE SUMMARY
    - Overview of the trip and key highlights
    - Total estimated budget
    - Top booking priorities

    ACCOMMODATION OPTIONS
    - 3–4 recommended hotels or stays with prices, location notes, and pros/cons

    DAY-BY-DAY ITINERARY (all {trip_duration} days)
    For each day:
    - Morning plans with times and locations
    - Lunch recommendation
    - Afternoon plans with times and locations
    - Dinner recommendation
    - Optional evening activities
    - Daily budget estimate
    - Transportation notes

    BOOKING CHECKLIST
    - Experiences that need advance reservations with links or contacts
    - Restaurants that require booking
    - Transportation passes or tickets to secure

    PACKING LIST
    - Based on expected weather and activities

    EMERGENCY INFORMATION
    - Key phone numbers
    - Nearby hospitals or clinics
    - Embassy or consulate contacts

    The final plan should feel polished, practical, and ready to use.
    """
    return Task(description=description, expected_output=expected_output, agent=agent, context=context_tasks)