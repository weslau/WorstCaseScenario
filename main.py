import streamlit as st
import pandas as pd

import random, string

import snowflake_utils as snow

def generate_game_code():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(6))

def header():
    st.write("### Worst Case Scenario")
    st.write("\n\n\n")

def back_widget(to:str="welcome"):
    back_button = st.button("Back")
    if back_button:
        st.session_state.current_page = to
        st.experimental_rerun()

def welcome_page():
    header()

    # if "current_page" not in st.session_state:
    st.session_state.current_page = "welcome"

    create_game_button = st.button("Create Game")
    st.write("\n")
    join_game_button = st.button("Join Game")

    if create_game_button:

        new_game_code = generate_game_code()
        st.session_state.game_code = new_game_code

        st.session_state.current_page = "lobby"
        st.experimental_rerun()

    if join_game_button:
        st.text_input("Enter 6-digit game code")


def lobby_page():
    header()

    st.write(f"### code: {st.session_state.game_code}")
        
    ## show lobby page; how many players have joined and whom
    back_widget()


if __name__ == "__main__":

    if "current_page" not in st.session_state or st.session_state.current_page == "welcome":
        welcome_page()
    elif st.session_state.current_page == "lobby":
        lobby_page()