import streamlit as st
import pandas as pd, datetime as dt

import uuid

from login import login_page, create_account_page, existing_account_page
from lobby import lobby_page

import utils.snowflake as snow
import utils.wcs as wcs

DB_NAME = wcs.DB_NAME
SCHEMA_NAME = wcs.SCHEMA_NAME


def logged_in_as():
    st.write(f"Logged in as: {st.session_state.player_name}")


def welcome_page():
    wcs.header()
    logged_in_as()

    st.session_state.current_page = "welcome"

    create_game_button = st.button("Create Game")
    st.write("\n")
    entered_game_code = str.upper(st.text_input("Enter 6-digit game code"))
    join_game_button = st.button("Join Game")

    if create_game_button:
        new_game_code = wcs.generate_game_code()
        st.session_state.game_code = new_game_code
        table_columns = ["GAME_ID", "GAME_CODE", "GAME_TIME_START", "IS_ACTIVE"]
        table_values = [str(uuid.uuid4()), st.session_state.game_code, dt.datetime.now(), True]
        snow.push("GAMES", table_columns, table_values)

        st.session_state.current_page = "lobby"
        st.experimental_rerun()

    if join_game_button or entered_game_code:
        query = f"""
        select * from {DB_NAME}.{SCHEMA_NAME}.GAMES
        where IS_ACTIVE = TRUE
        """

        df_games = snow.pull(query)
        is_active_game = entered_game_code in df_games.GAME_CODE.tolist()

        if is_active_game:
            st.session_state.current_page = "lobby"
            st.session_state.game_code = entered_game_code
            st.experimental_rerun()

        else:
            st.error("Not an active game code.")

    wcs.back_widget(to="login")


# this is where game instructions should be included
def game_start_page():
    wcs.header()
    # link to a page (function) called play_round_page() that implements the functionality of app.py

    wcs.back_widget(to="lobby")
    
def play_round_page():
    # TEMPORARY BEFORE DB SETUP:Read rows from a text file and store them in a Pandas DataFrame
    data_scenarios = gameplay.read_rows_from_file("rows.txt")
    



if __name__ == "__main__":

    page_dict = {
        "login": login_page,
        "create account": create_account_page,
        "login existing account": existing_account_page,
        "welcome": welcome_page,
        "lobby": lobby_page,
        "game start": game_start_page,
        "play round": play_round_page,
    }

    st.session_state.in_lobby = False

    if "current_page" not in st.session_state:
        login_page()
    
    else:
        page_dict[st.session_state.current_page]()
