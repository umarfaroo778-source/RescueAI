from rescueai.agents import incident_analyst, safety_review
from rescueai.rag import Retriever

def test_incident_extraction():
    x = incident_analyst("Bus crash with 3 injured people and smoke", "Karachi")
    assert x["type"] == "road traffic accident"
    assert x["casualties"] == 3
    assert "smoke" in x["hazards"]

def test_missing_location():
    x = incident_analyst("A fire with smoke", "")
    assert "location" in x["missing_info"]

def test_retrieval():
    assert len(Retriever("keyword").retrieve("fire smoke building", 5)) > 0

def test_safety_filter():
    plan, flags = safety_review(["Contact emergency services. [AI]", "ETA is 5 minutes. [AI]"])
    assert len(plan) == 1
    assert flags
