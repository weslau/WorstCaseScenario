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

def logged_in_as():
    st.write(f"Logged in as: {st.session_state.player_name}")

def back_widget(to:str="welcome"):
    back_button = st.button("Back")
    if back_button:
        st.session_state.current_page = to
        st.experimental_rerun()

def create_account_page():
    header()

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
                split = new_username.split(" ")
                if len(new_username) < 3:
                    st.error("Username must be at least 3 characters.")
                elif len(set(string.punctuation) - set(new_username)) != len(string.punctuation):
                    st.error("No punctuation in usernames, por favor.")
                elif len(split) > 1:
                    if (split[0] in wcs.PSEUDONYM_ADJECTIVES) & (split[1] in wcs.PSEUDONYM_NOUNS):
                        st.error("Name reserved for guests.")

                else:

                    try:
                        columns = ["PLAYER_ID", "PLAYER_NAME", "PLAYER_NGAMES"]
                        values = [str(uuid.uuid4()), new_username, 0]
                        snow.push("PLAYER_INFO", columns, values)

                        st.success("Success!")
                        st.session_state.player_name = new_username
                        st.session_state.current_page = "welcome"
                    
                    except:
                        wcs.assign_blame()

    back_widget(to="login")


def existing_account_page():

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
                    df_players[df_players.PLAYER_NAME == existing_username]
                    .values.tolist()[0]
                )
                st.success("Success! Sick!")
                st.session_state.current_page = "welcome"
                st.experimental_rerun()
            
            else:
                st.error("Username not found. How embarrassing for you.")

    back_widget(to="login")


def login_page():
    header()

    st.session_state.current_page = "login"
    existing_account_button = st.button("Existing account")
    
    if existing_account_button:
        st.session_state.current_page = "login existing account"
        st.experimental_rerun()
    
    new_account_button = st.button("New account")
    st.write("\n")

    if new_account_button:
        st.session_state.current_page = "create account"
        st.experimental_rerun()

    st.write("\n")
    guest_login_button = st.button("Continue as guest")

    if guest_login_button:
        pseudonym = wcs.generate_pseudonym()
        st.success(f"Logging in as `{pseudonym}`!")

        st.session_state.player_name = pseudonym
        st.session_state.current_page = "welcome"
        st.experimental_rerun()


def welcome_page():
    header()
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

    if join_game_button:
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

    back_widget(to="login")


def join_lobby(df_lobby):
    game_code, player_name = st.session_state.game_code, st.session_state.player_name

    if (game_code, player_name) in df_lobby[["GAME_CODE", "PLAYER_NAME"]].values:
        pass

    else:
        colnames = ["game_code", "player_name", "joined_at"]
        values = [game_code, player_name, dt.datetime.now()]
        snow.push("lobby_info", colnames, values)

def lobby_page():
    header()

    st.write(f"### code: {st.session_state.game_code}")
    
    query = f"""
    select * from {DB_NAME}.{SCHEMA_NAME}.lobby_info
    where game_code = '{st.session_state.game_code}'
    order by joined_at
    """
    df_lobby = snow.pull(query)

    join_lobby(df_lobby)
    
    for name in df_lobby.PLAYER_NAME:
        st.write(name)

    back_widget()


if __name__ == "__main__":

    page_dict = {
        "login": login_page,
        "create account": create_account_page,
        "login existing account": existing_account_page,
        "welcome": welcome_page,
        "lobby": lobby_page
    }

    if "current_page" not in st.session_state:
        login_page()
    
    else:
        page_dict[st.session_state.current_page]()
