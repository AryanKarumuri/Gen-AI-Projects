import streamlit as st
from datetime import date, timedelta
from tasks import location_task, guide_task, planner_task
from crewai import Crew
from agents import build_agents

st.set_page_config(page_title="Your Travel Planner", layout="centered")

st.sidebar.title("⚙️ Settings")

if "mistral_api_key" not in st.session_state:
    st.session_state.mistral_api_key = ""

st.session_state.mistral_api_key = st.sidebar.text_input(
    "🔑 Mistral API key",
    type="password",
    value=st.session_state.mistral_api_key,
    help="Paste your Mistral API key here. Sidebar can be collapsed.",
)

st.sidebar.caption("You can collapse this panel from the top-left arrow.")


st.title("🧭 AI Trip planner")

today = date.today()
default_start = today
default_end = today + timedelta(days=1)

with st.form("trip_form"):
    c1, c2 = st.columns(2)
    with c1:
        from_city = st.text_input("🚐 From city", value="palakollu")
    with c2:
        destination = st.text_input("📍 Destination city", value="bhimavaram")

    d1, d2 = st.columns(2)
    with d1:
        date_from = st.date_input(
            "📅 Start date",
            value=default_start,
            min_value=today,
            help="Select today or a future date",
        )
    with d2:
        date_to = st.date_input(
            "🗓️ End date",
            value=max(default_end, date_from),
            min_value=date_from,
            help="End date must be same as or after start date",
        )

    interests_raw = st.text_area(
        "🎯 Interests (one per line or comma separated)",
        value="food\nculture\nnature",
        height=140,
    )

    verbose = st.checkbox("🔍 Verbose output", value=True)

    submit = st.form_submit_button("✨ Run trip planner")


if submit:
    if not st.session_state.mistral_api_key:
        st.error("Please provide a Mistral API key before running the workflow.")
    elif date_to < date_from:
        st.error("⚠️ End date cannot be before start date. Fix the dates and try again.")        
    else:
        # Normalize interests
        raw = interests_raw.replace(",", "\n")
        interests = [s.strip() for s in raw.splitlines() if s.strip()]

        st.info("This takes 3-4 mins for completing your itinerary. Your patience is appreciated! 🤖✈️")

        with st.spinner("🧩 Agents planning your trip..."):
            try:
                planner_agent, location_agent, guide_agent = build_agents(
                    st.session_state.mistral_api_key
                )
            except Exception as e:
                st.error(f"Failed to build agents: {e}")
                st.exception(e)
                st.stop()

        with st.spinner("🚀 Preparing your itinerary.."):
            try:
                loc_task = location_task(
                    agent=location_agent,
                    from_city=from_city,
                    destination_city=destination,
                    date_from=date_from,
                    date_to=date_to,
                )

                guide_task_obj = guide_task(
                    agent=guide_agent,
                    destination_city=destination,
                    interests=interests,
                    date_from=date_from,
                    date_to=date_to,
                )

                plan_task = planner_task(
                    context_tasks=[loc_task, guide_task_obj],
                    agent=planner_agent,
                    destination_city=destination,
                    interests=interests,
                    date_from=date_from,
                    date_to=date_to,
                )

                crew = Crew(
                    agents=[location_agent, guide_agent, planner_agent],
                    tasks=[loc_task, guide_task_obj, plan_task],
                    verbose=verbose,
                )

                result = crew.kickoff()

                st.success("🎉 Workflow finished")
                
                st.subheader("🗺️ Final itinerary / result")
                final_markdown = result.raw if hasattr(result, "raw") else str(result)
                st.markdown(final_markdown)

                # Add this snippet to allow downloading the plan
                st.download_button(
                    label="📥 Download Itinerary",
                    data=final_markdown,
                    file_name="trip_plan.md",
                    mime="text/markdown"
                )

                # Extract individual task outputs
                if hasattr(result, "tasks_output") and result.tasks_output:
                    st.write("✅ All agents completed successfully!")
                    
                    # Get individual task results
                    if len(result.tasks_output) >= 3:
                        st.session_state.location_response = str(
                            result.tasks_output[0].raw
                            if hasattr(result.tasks_output[0], "raw")
                            else result.tasks_output[0]
                        )
                        st.session_state.guide_response = str(
                            result.tasks_output[1].raw
                            if hasattr(result.tasks_output[1], "raw")
                            else result.tasks_output[1]
                        )
                        st.session_state.planner_response = str(
                            result.tasks_output[2].raw
                            if hasattr(result.tasks_output[2], "raw")
                            else result.tasks_output[2]
                        )
                    else:
                        # Fallback: use final result for all
                        final_output = result.raw if hasattr(result, "raw") else str(result)
                        st.session_state.location_response = final_output
                        st.session_state.guide_response = final_output
                        st.session_state.planner_response = final_output
                else:
                    # Fallback for older CrewAI versions
                    final_output = result.raw if hasattr(result, "raw") else str(result)
                    st.session_state.planner_response = final_output
                    st.session_state.location_response = "Included in final plan"
                    st.session_state.guide_response = "Included in final plan"
                
                st.write("🎉 Travel plan generation complete!")

            except Exception as e:
                st.error(f"Workflow failed: {e}")
                st.exception(e)

st.caption(
    "Note: The API key you enter is used only for this session to construct the LLM and agents. "
    "It is not written to disk by this app."
)
