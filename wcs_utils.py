import random, string
import streamlit as st

def assign_blame():
    whos_at_fault = random.choice(["Mike", "Wesley", "Mark D"])
    st.error(f"Something went wrong. Blame {whos_at_fault}.")

def generate_game_code():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(6))

def generate_pseudonym():

    ADJECTIVES = [
        "anachronistic", "boisterous", "cadaverous", "capricious", "convivial",
        "ebullient", "enigmatic", "ephemeral", "esoteric",
        "euphoric", "fastidious", "gregarious", "ineffable",
        "mellifluous", "mercurial", "nefarious", "obsequious",
        "serendipitous", "surreptitious", "taciturn"
    ]

    NOUNS = [
        "antenna", "azimuth", "bayesian", "convolution",
        "downlink", "eigenvector", "entropy", "geostationary",
        "classifier", "radiation", "kurtosis", "cluster",
        "manifold", "orthogonality", "diplexer", "quadrature",
        "spectrogram", "tensor", "waveguide", "orbit", "GPT"
    ]

    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"