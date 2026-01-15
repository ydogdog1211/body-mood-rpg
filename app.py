import json
import os
from datetime import date, timedelta

import streamlit as st

DATA_DIR = "data"
DATA_PATH = os.path.join(DATA_DIR, "state.json")

DEFAULT_STATS = {
    "strength": 50,
    "energy": 50,
    "mood": 50,
    "recovery": 50,
}

ACTION_EFFECTS = {
    "stretch_5": {"strength": 1, "energy": 2, "mood": 2, "recovery": 3},
    "strength_20": {"strength": 4, "energy": -2, "mood": 1, "recovery": -1},
    "cardio_15": {"strength": 2, "energy": -3, "mood": 2, "recovery": -1},
    "protein_meal": {"strength": 1, "energy": 3, "mood": 1, "recovery": 1},
    "early_sleep": {"strength": 1, "energy": 4, "mood": 2, "recovery": 4},
}


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def load_state():
    if not os.path.exists(DATA_PATH):
        return {
            "date": str(date.today()),
            "actions": [],
            "stats": DEFAULT_STATS.copy(),
            "streak": 0,
            "last_action_date": None,
        }
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)


def roll_to_today(state):
    today = date.today()
    stored_date = date.fromisoformat(state["date"])
    if stored_date == today:
        return state

    yesterday = today - timedelta(days=1)
    last_action_date = state.get("last_action_date")
    if last_action_date:
        last_action_date = date.fromisoformat(last_action_date)

    if last_action_date == yesterday:
        state["streak"] = state.get("streak", 0)
    else:
        state["streak"] = 0

    state["date"] = str(today)
    state["actions"] = []
    save_state(state)
    return state


def apply_action(state, action_key):
    if action_key in state["actions"]:
        return state

    is_first_action = len(state["actions"]) == 0
    state["actions"].append(action_key)
    for stat, delta in ACTION_EFFECTS[action_key].items():
        state["stats"][stat] = clamp(state["stats"][stat] + delta)

    if is_first_action:
        today_str = str(date.today())
        yesterday_str = str(date.today() - timedelta(days=1))
        last_action_date = state.get("last_action_date")

        if last_action_date == yesterday_str:
            state["streak"] = state.get("streak", 0) + 1
        else:
            state["streak"] = 1

        state["last_action_date"] = today_str

    save_state(state)
    return state


state = load_state()
state = roll_to_today(state)

today_str = str(date.today())

st.title("Body Mood RPG")
st.caption(f"Today: {today_str} ｜ 🔥 Streak: {state['streak']} days")

st.subheader("Your body status")
for key, value in state["stats"].items():
    st.progress(value / 100)
    st.write(f"{key.capitalize()}: {value}")

st.subheader("Actions")
for action_key in ACTION_EFFECTS:
    if st.button(action_key):
        state = apply_action(state, action_key)
        st.rerun()

st.subheader("Today's actions")
st.write(state["actions"])
