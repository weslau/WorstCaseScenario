import random, string
import streamlit as st

DB_NAME = "DEV_WORSTCASESCENARIO_DB" 
SCHEMA_NAME = "WCS_DB_SCHEMA1"

PSEUDONYM_ADJECTIVES = [
    "anachronistic", "boisterous", "cadaverous", "capricious", "convivial",
    "ebullient", "enigmatic", "moody", "esoteric",
    "euphoric", "fastidious", "gregarious", "ineffable",
    "mellifluous", "mercurial", "nefarious", "inconceivable",
    "serendipitous", "surreptitious", "taciturn"
]

PSEUDONYM_NOUNS = [
    "antenna", "azimuth", "bayesian", "convolution",
    "downlink", "eigenvector", "entropy", "payload",
    "classifier", "radiation", "kurtosis", "cluster",
    "manifold", "orthogonality", "diplexer", "quadrature",
    "polarization", "tensor", "waveguide", "orbit", "GPT"
]

def header():
    st.write("### Worst Case Scenario")
    st.write("\n\n\n")

def back_widget(to:str="welcome"):
    for _ in range(5):
        st.write("\n")
    back_button = st.button("back")
    if back_button:
        st.session_state.current_page = to
        st.experimental_rerun()

def assign_blame():
    whos_at_fault = random.choice(["Mike", "Wesley", "Matthew", "Mark D"])
    st.error(f"Something went wrong. Blame {whos_at_fault}.")

def generate_game_code():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(6))

def generate_pseudonym():
    adj = str.capitalize(random.choice(PSEUDONYM_ADJECTIVES))
    noun = str.capitalize(random.choice(PSEUDONYM_NOUNS))
    return f"{adj} {noun}"