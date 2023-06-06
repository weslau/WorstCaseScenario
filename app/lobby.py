import streamlit as st, datetime as dt
import time

import utils.snowflake as snow
from utils.wcs import DB_NAME, SCHEMA_NAME, header, back_widget
import gameplay as gameplay

def join_lobby(df_lobby):
    game_code, player_name = st.session_state.game_code, st.session_state.player_name

    if [game_code, player_name] in df_lobby[["GAME_CODE", "PLAYER_NAME"]].values.tolist():
        pass

    else:
        colnames = ["game_code", "player_name", "joined_at"]
        values = [game_code, player_name, dt.datetime.now()]
        snow.push("lobby_info", colnames, values)
        st.experimental_rerun()

    st.session_state.in_lobby = True

def leave_lobby(df_lobby):
    game_code, player_name = st.session_state.game_code, st.session_state.player_name

    if [game_code, player_name] in df_lobby[["GAME_CODE", "PLAYER_NAME"]].values.tolist():
        conditional = (df_lobby['GAME_CODE']==game_code) & (df_lobby['PLAYER_NAME']==player_name)
        df_lobby = df_lobby.drop(df_lobby[conditional].index)

    # Remove from Snowflake too,
    query = f"""
    DELETE from {DB_NAME}.{SCHEMA_NAME}.lobby_info
    where
        game_code = '{st.session_state.game_code}'
        AND PLAYER_NAME = '{player_name}'
    """
    df_lobby = snow.pull(query)

    st.session_state.in_lobby = False
    st.session_state.current_page = "welcome"
    st.experimental_rerun()


def lobby_page():
    header()

    query = f"""
    select * from {DB_NAME}.{SCHEMA_NAME}.lobby_info
    where game_code = '{st.session_state.game_code}'
    order by joined_at
    """
    df_lobby = snow.pull(query)

    n_players = df_lobby.shape[0]

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"### code: {st.session_state.game_code}")
    with c2:
        st.write(f"### {n_players} / 10")

    join_lobby(df_lobby)
    
    for name in df_lobby.PLAYER_NAME:
        # st.write(f"{name} \u2713")
        st.write(name)

    ## start game widget
    start_game_button = st.button("Ready to Play")

    if start_game_button:
        if n_players < 3:
            st.error("Not enough players")
            
            ### HACK
            if st.session_state.player_name == "dev":
                st.session_state.current_page = "game start"
                st.experimental_rerun()
            ###
        
        else:
            st.session_state.current_page = "play round"
            st.experimental_rerun()
    
    # Leave lobby.
    leave_lobby_button = st.button("Leave lobby")
    if leave_lobby_button:
        leave_lobby(df_lobby)

    gameplay.print_game_rules()

    back_widget()
    time.sleep(2)
    st.experimental_rerun()