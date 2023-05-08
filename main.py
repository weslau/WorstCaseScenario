import streamlit as st
import pandas as pd, datetime as dt

import uuid, string

import snowflake_utils as snow
import wcs_utils as wcs

DB_NAME = "DEV_WORSTCASESCENARIO_DB" 
SCHEMA_NAME = "WCS_DB_SCHEMA1"


def header():
    st.write("### Worst Case Scenario")
    st.write("\n\n\n")

def back_widget(to:str="welcome"):
    back_button = st.button("Back")
    if back_button:
        st.session_state.current_page = to
        st.experimental_rerun()

def login_page():
    header()

    st.session_state.current_page = "login"
    with st.form("username_login"):
        existing_username = st.text_input("Username:")

        existing_login_button = st.form_submit_button("Login")

        if existing_login_button:
            query = f"""
            select PLAYER_ID, PLAYER_NAME from {DB_NAME}.{SCHEMA_NAME}.PLAYER_INFO
            """

            df_players = snow.pull(query)
            is_user = existing_username in df_players.PLAYER_NAME.tolist()

            if is_user:
                st.session_state.player_id, st.session_state.player_name = (
                    df_players[df_players.player_name == existing_username]
                    .values.tolist()
                )
                st.success("Success! Sick!")
                st.session_state.current_page = "welcome"
            
            else:
                st.error("Username not found. How embarrassing for you.")

    new_account_button = st.button("Create new account")
    st.write("\n")

    if new_account_button:
        with st.form("New Account"):
            new_username = st.text_input("New username:")

            new_username_button = st.form_submit_button("Submit and login")

            if new_username_button:
                query = f"""
                select PLAYER_ID, PLAYER_NAME from {DB_NAME}.{SCHEMA_NAME}.PLAYER_INFO
                """

                df_players = snow.pull(query)
                is_user_already = new_username in df_players.PLAYER_NAME.tolist()

                if is_user_already:
                    st.error(f"`{new_username}` is already an existing username, doofus.")
                else:
                    if len(new_username) < 3:
                        st.error("Username must be at least 3 characters.")
                    if len(set(string.punctuation) - set(new_username)) != len(string.punctuation):
                        st.error("No punctuation in usernames, por favor.")

                    try:
                        columns = ["PLAYER_ID", "PLAYER_NAME", "PLAYER_NGAMES"]
                        values = [str(uuid.uuid4()), new_username, 0]
                        snow.push("PLAYER_INFO", columns, values)

                        st.success("Success!")
                        st.session_state.current_page = "welcome"
                    
                    except:
                        wcs.assign_blame()
                    


    st.write("\n")
    guest_login_button = st.button("Continue as guest")

def welcome_page():
    header()

    st.session_state.current_page = "welcome"

    create_game_button = st.button("Create Game")
    st.write("\n")
    entered_game_code = st.text_input("Enter 6-digit game code")
    join_game_button = st.button("Join Game")

    if create_game_button:

        new_game_code = wcs.generate_game_code()
        st.session_state.game_code = new_game_code
        table_columns = ["GAME_ID", "GAME_CODE", "GAME_TIME_START", "IS_ACTIVE"]
        table_values = [str(uuid.uuid4()), st.session_state.game_code, dt.datetime.now(), True]
        snow.push("GAMES", table_columns, table_values)

        st.session_state.current_page = "lobby"
        st.experimental_rerun()

    if join_game_button:
        query = f"""
        select * from {DB_NAME}.{SCHEMA_NAME}.GAMES
        where IS_ACTIVE = TRUE
        """

        result = snow.pull(query)
        print(entered_game_code)
        print(type(entered_game_code))
        print(entered_game_code in result.GAME_CODE.tolist())




def lobby_page():
    header()

    st.write(f"### code: {st.session_state.game_code}")
    
        
    ## show lobby page; how many players have joined and whom
    back_widget()


if __name__ == "__main__":

    page_dict = {
        "login": login_page,
        "welcome": welcome_page,
        "lobby": lobby_page
    }

    if "current_page" not in st.session_state:
        login_page()
    
    else:
        page_dict[st.session_state.current_page]()

    # if "current_page" not in st.session_state or st.session_state.current_page == "welcome":
    #     welcome_page()
    # elif st.session_state.current_page == "lobby":
    #     lobby_page()