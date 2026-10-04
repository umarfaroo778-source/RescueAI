import re

def incident_analyst(report, location=""):
    text = report.lower()
    if any(x in text for x in ["fire", "smoke", "burning"]): kind = "fire"
    elif any(x in text for x in ["flood", "flooding", "water rising"]): kind = "flood"
    elif any(x in text for x in ["rain", "storm", "lightning", "wind"]): kind = "severe weather"
    elif any(x in text for x in ["crash", "collision", "accident", "bus", "car"]): kind = "road traffic accident"
    else: kind = "unknown"

    severity = "high" if any(x in text for x in ["trapped", "multiple injured", "collapsed", "heavy smoke"]) else "moderate"
    m = re.search(r"(\d+)\s+(?:people|persons|casualties|injured|victims)", text)
    casualties = int(m.group(1)) if m else None

    hazards = []
    for key, label in [("smoke","smoke"),("fire","fire"),("gas","possible gas"),
                       ("water","flood water"),("electric","electrical hazard"),
                       ("traffic","traffic"),("unstable","unstable structure")]:
        if key in text and label not in hazards: hazards.append(label)

    missing = []
    if casualties is None: missing.append("casualty count")
    if not location.strip(): missing.append("location")
    if not hazards: missing.append("scene hazards")

    return {"type":kind, "severity":severity, "casualties":casualties,
            "hazards":hazards, "missing_info":missing, "location_hint":location.strip()}

def response_planner(incident, loc, weather, rag):
    plan = [
        "1. **Contact local emergency services first.** [AI]",
        "2. Keep a safe distance from the scene and do not enter an unstable, flooded, smoky, or otherwise hazardous area. [KB:scene-safety-01]"
    ]
    if incident["type"] == "road traffic accident":
        plan.append("3. Warn approaching traffic only if this can be done without entering danger. [KB:traffic-01]")
    elif incident["type"] == "fire":
        plan.append("3. Move away from smoke/fire and avoid entering the structure. [KB:fire-01]")
    elif incident["type"] == "flood":
        plan.append("3. Avoid moving through floodwater and seek safer elevated ground where appropriate. [KB:flood-01]")
    elif incident["type"] == "severe weather":
        plan.append("3. Move to a safer sheltered location away from exposed areas. [KB:weather-01]")
    else:
        plan.append("3. Do not take actions that expose you to an unknown hazard. [AI]")
    plan.append("4. Provide responders with the known location, hazards, casualty information, and changes you observe. [AI]")
    if incident["missing_info"]:
        plan.append("5. **Unknowns:** " + ", ".join(incident["missing_info"]) + ". [AI]")
    return plan

def safety_review(plan):
    forbidden = re.compile(r"\b(diagnos|dose|dosage|dispatch|eta|arrive in|road closure)\b", re.I)
    cleaned, flags = [], []
    for line in plan:
        if forbidden.search(line):
            flags.append("Removed unsupported/unsafe claim: " + line)
        else:
            cleaned.append(line)
    flags.append("No rescue-time or safety guarantee is provided.")
    return cleaned, flags
