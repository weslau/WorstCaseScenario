import streamlit as st
import pandas as pd, datetime as dt

import random, string, uuid

import snowflake_utils as snow

DB_NAME = "DEV_WORSTCASESCENARIO_DB" 
SCHEMA_NAME = "WCS_DB_SCHEMA1"

def generate_game_code():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(6))

def generate_uuid():
    pass

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

    st.session_state.current_page = "welcome"

    create_game_button = st.button("Create Game")
    st.write("\n")
    join_game_button = st.button("Join Game")

    if create_game_button:

        new_game_code = generate_game_code()
        st.session_state.game_code = new_game_code
        table_columns = ["GAME_ID", "GAME_CODE", "GAME_TIME_START", "IS_ACTIVE"]
        table_values = [str(uuid.uuid4()), st.session_state.game_code, dt.datetime.now(), True]
        snow.push("GAMES", table_columns, table_values)

        st.session_state.current_page = "lobby"
        st.experimental_rerun()

    if join_game_button:
        entered_game_code = st.text_input("Enter 6-digit game code")

        if entered_game_code:
            query = f"""
            select * from {DB_NAME}.{SCHEMA_NAME}.GAMES
            where IS_ACTIVE = TRUE
            """

            result = snow.pull(query)
            print(result)


def lobby_page():
    header()

    st.write(f"### code: {st.session_state.game_code}")
    
        
    ## show lobby page; how many players have joined and whom
    back_widget()


if __name__ == "__main__":

    page_dict = {
        "welcome": welcome_page,
        "lobby": lobby_page
    }

    if "current_page" not in st.session_state:
        welcome_page()
    
    else:
        page_dict[st.session_state.current_page]()

    # if "current_page" not in st.session_state or st.session_state.current_page == "welcome":
    #     welcome_page()
    # elif st.session_state.current_page == "lobby":
    #     lobby_page()