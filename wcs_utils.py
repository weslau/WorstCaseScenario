import random, string
import streamlit as st

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

def assign_blame():
    whos_at_fault = random.choice(["Mike", "Wesley", "Matthew", "Mark D"])
    st.error(f"Something went wrong. Blame {whos_at_fault}.")

def generate_game_code():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(6))

def generate_pseudonym():
    adj = str.capitalize(random.choice(PSEUDONYM_ADJECTIVES))
    noun = str.capitalize(random.choice(PSEUDONYM_NOUNS))
    return f"{adj} {noun}"