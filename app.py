import streamlit as st
import json
import os
from datetime import date

DATA_PATH = "state.json"

DEFAULT_STATE = {
    "date": str(date.today()),
    "streak": 0,
    "stats": {
        "strength": 50,
        "energy": 50,
        "mood": 50,
        "recovery": 50
    },
    "actions_today": []
}

ACTION_EFFECTS = {
    "stretch_5":     {"strength": 1, "energy": 2, "mood": 2, "recovery": 3},
    "strength_20":   {"strength": 4, "energy": -2, "mood": 1, "recovery": -1},
    "cardio_15":     {"strength": 2, "energy": -3, "mood": 2, "recovery": -1},
    "protein_meal":  {"strength": 1, "energy": 3, "mood": 1, "recovery": 1},
    "early_sleep":   {"strength": 1, "energy": 4, "mood": 2, "recovery": 4},
}

def load_state():
    if not os.path.exists(DATA_PATH):
        return DEFAULT_STATE.copy()
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_state(state):
    with open(DATA_PATH, "w") as f:
        json.dump(state, f, indent=2)

state = load_state()

today = str(date.today())
if state["date"] != today:
    state["date"] = today
    state["actions_today"] = []
    state["streak"] += 1

st.title("💪 Body Mood RPG")
st.caption(f"Today: {today} ｜ 🔥 Streak: {state['streak']} days")

st.subheader("Your body status")
for k, v in state["stats"].items():
    st.progress(v / 100)
    st.write(f"{k.capitalize()}: {v}")

st.subheader("Actions")

for action in ACTION_EFFECTS:
    if st.button(action):
        if action not in state["actions_today"]:
            state["actions_today"].append(action)
            for stat, delta in ACTION_EFFECTS[action].items():
                state["stats"][stat] = max(
                    0, min(100, state["stats"][stat] + delta)
                )
            save_state(state)
            st.experimental_rerun()

st.subheader("Today's actions")
st.write(state["actions_today"])
