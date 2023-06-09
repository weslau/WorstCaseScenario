import datetime as dt
import streamlit as st
import uuid, string

import utils.snowflake as snow
import utils.wcs as wcs

from utils.wcs import DB_NAME, SCHEMA_NAME, header, back_widget

def create_account(new_username):
    try:
        columns = ["PLAYER_ID", "PLAYER_NAME", "PLAYER_NGAMES"]
        values = [str(uuid.uuid4()), new_username, 0]
        snow.push("PLAYER_INFO", columns, values)

        st.success("Success!")
        st.session_state.player_name = new_username
        st.session_state.current_page = "welcome"
        st.experimental_rerun()
    
    except Exception as e:
    # If you just "Except:" it catches a BaseException: RerunData(page_script_hash='195f142363f570330eea1b6ff39c752d')
    # Don't know what this is though so ignoring it
        st.write(e)
        wcs.assign_blame()

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
                    if (split[0] in wcs.PSEUDONYM_ADJECTIVES) and (split[1] in wcs.PSEUDONYM_NOUNS):
                        st.error("Name reserved for guests.")
                    else:
                        create_account(new_username)

                else:
                    create_account(new_username)

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
    # guest_login_button = st.button("Continue as guest")

    # if guest_login_button:
    #     pseudonym = wcs.generate_pseudonym()
    #     st.success(f"Logging in as `{pseudonym}`!")

    #     st.session_state.player_name = pseudonym
    #     st.session_state.current_page = "welcome"
    #     st.experimental_rerun()

    # Delete old games.
    delete_old_games()


def delete_old_games():
    hours_to_delete = 24

    query = f"""
    DELETE from {DB_NAME}.{SCHEMA_NAME}.lobby_info
        WHERE TIMEDIFF(hours, JOINED_AT, '{dt.datetime.now()}') > {hours_to_delete}
    """
    snow.pull(query)