from .agents import incident_analyst, response_planner, safety_review
from .rag import Retriever
from .tools import geocode, nearby_hospitals, weather

def run_rescueai(report, location="", simulate_groq_outage=False, retrieval_mode="auto"):
    timeline = []
    def event(agent,state,message): timeline.append({"agent":agent,"state":state,"message":message})

    event("Incident Analyst","working","Extracting incident facts and missing information.")
    incident = incident_analyst(report, location)
    event("Incident Analyst","completed",f'Detected {incident["type"]} / {incident["severity"]}.')

    event("Location & Context","working","Resolving location and nearby facilities.")
    loc = geocode(location or incident["location_hint"])
    if loc["ok"]:
        event("Location & Context","tool call","Nominatim geocoding completed.")
        loc["hospitals"] = nearby_hospitals(loc["lat"],loc["lon"])
        event("Location & Context","tool call",f'Overpass returned {len(loc["hospitals"])} named facilities.')
    else:
        event("Location & Context","completed",loc["error"])

    event("Environment","working","Fetching current weather when coordinates are available.")
    if loc["ok"]:
        wx = weather(loc["lat"],loc["lon"])
        event("Environment","tool call","Open-Meteo weather lookup completed." if wx["ok"] else wx["error"])
    else:
        wx = {"ok":False,"error":"Skipped because location is unresolved."}
        event("Environment","completed",wx["error"])

    event("Knowledge/RAG","working","Retrieving top knowledge chunks.")
    rag = Retriever(retrieval_mode).retrieve(incident["type"]+" "+" ".join(incident["hazards"])+" "+report,5)
    event("Knowledge/RAG","completed",f"Retrieved {len(rag)} chunks.")

    event("Response Planner","working","Drafting a prioritized evidence-tagged plan.")
    plan = response_planner(incident,loc,wx,rag)
    event("Response Planner","completed","Plan drafted.")

    event("Safety Reviewer","review","Filtering unsupported or unsafe claims.")
    final_plan, flags = safety_review(plan)
    event("Safety Reviewer","completed",f"Review complete; {len(flags)} notices.")

    return {"incident":incident,"loc":loc,"weather":wx,"rag":rag,
            "final_plan":final_plan,"flags":flags,"timeline":timeline}
