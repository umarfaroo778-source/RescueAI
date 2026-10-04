import streamlit as st
from rescueai.coordinator import run_rescueai
from rescueai.scenarios import load_scenarios

st.set_page_config(page_title="RescueAI Mission Control", page_icon="🚨", layout="wide")
st.error("🚨 RescueAI is decision support only — not an emergency service, dispatcher, medical system, or replacement for local emergency authorities. Contact local emergency services first.")

scenarios = load_scenarios()
with st.sidebar:
    st.title("RescueAI")
    selected = st.selectbox("Prepared scenario", list(scenarios))
    simulate = st.checkbox("Simulate Groq outage")
    retrieval_mode = st.selectbox("Retrieval mode", ["auto", "keyword", "semantic"])

scenario = scenarios[selected]
st.subheader("Emergency Intake")
report = st.text_area("Incident report", scenario["report"], height=150)
location = st.text_input("Location (optional)", scenario.get("location", ""))

if st.button("🚨 Run RescueAI", type="primary", use_container_width=True):
    result = run_rescueai(report, location, simulate, retrieval_mode)

    a, b = st.columns(2)
    with a:
        inc = result["incident"]
        st.metric("Incident type", inc["type"])
        st.metric("Severity", inc["severity"])
        st.metric("Casualties", inc["casualties"] if inc["casualties"] is not None else "Unknown")
        st.write("**Hazards:**", ", ".join(inc["hazards"]) or "Unknown")
    with b:
        loc = result["loc"]
        st.write("### Location Evidence")
        if loc["ok"]:
            st.success(f'{loc["name"]} ({loc["lat"]:.4f}, {loc["lon"]:.4f})')
            st.caption(f'Source: {loc["source"]} · {loc["fetched_at"]}')
            for h in loc["hospitals"]:
                st.write("• " + h)
        else:
            st.warning(loc["error"])

        wx = result["weather"]
        st.write("### Weather Evidence")
        if wx["ok"]:
            st.write(f'{wx["temperature_c"]} °C · rain {wx["rain_mm"]} mm · wind {wx["wind_kmh"]} km/h')
            st.caption(f'Observed: {wx["observed_at"]} · fetched: {wx["fetched_at"]}')
        else:
            st.warning(wx["error"])

    st.write("### Agent Timeline")
    for e in result["timeline"]:
        st.write(f'**{e["state"].upper()}** — {e["agent"]} · {e["message"]}')

    st.write("### Retrieved Knowledge")
    for item in result["rag"]:
        with st.expander(f'{item["id"]} · score {item["score"]:.3f}'):
            st.caption(item["source"])
            st.write(item["text"])

    st.write("### Prioritized Action Plan")
    for action in result["final_plan"]:
        st.markdown(action)

    st.write("### Safety / Uncertainty Notices")
    for flag in result["flags"]:
        st.warning(flag)
