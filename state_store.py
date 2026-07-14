# -*- coding: utf-8 -*-
"""Server-side storage for the student profile + chat history.

Single-user app (no login), so this is one JSON file shared across
browsers/devices instead of per-browser localStorage.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATE_PATH = os.path.join(DATA_DIR, 'state.json')

DEFAULT_STATE = {'profile': None, 'history': []}


def load_state():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STATE_PATH):
        return dict(DEFAULT_STATE)
    with open(STATE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {'profile': data.get('profile'), 'history': data.get('history', [])}


def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def save_profile(profile):
    state = load_state()
    state['profile'] = profile
    save_state(state)
    return state


def save_history(history):
    state = load_state()
    state['history'] = history
    save_state(state)
    return state


def clear_history():
    state = load_state()
    state['history'] = []
    save_state(state)
    return state
