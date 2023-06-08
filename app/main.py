import streamlit as st
import pandas as pd, datetime as dt
import random
import time

import uuid
import utils.snowflake as snow

from login import login_page, create_account_page, existing_account_page
from lobby import lobby_page

import utils.snowflake as snow
import utils.wcs as wcs
import gameplay as gameplay

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
        st.session_state.game_id = str(uuid.uuid4())
        table_values = [st.session_state.game_id, st.session_state.game_code, dt.datetime.now(), True]
        snow.push("GAMES", table_columns, table_values)

        st.session_state.current_page = "lobby"
        st.experimental_rerun()

    if join_game_button or entered_game_code:
        query = f"""
        select * from {DB_NAME}.{SCHEMA_NAME}.GAMES
        where IS_ACTIVE = TRUE
        """
        # GAME_CODE,GAME_ID,GAME_TIME_START, IS_ACTIVE all included in df_games
        df_games = snow.pull(query)
        is_active_game = entered_game_code in df_games.GAME_CODE.tolist()

        if is_active_game:
            st.session_state.current_page = "lobby"
            st.session_state.game_code = entered_game_code
            st.experimental_rerun()
            # st.write(df_games)

        else:
            st.error("Not an active game code.")

    wcs.back_widget(to="login")


# this is where game instructions should be included
def game_start_page():
    wcs.header()
    
    # link to a page (function) called play_round_page() that implements the functionality of app.py
    start_game_button = st.button("Start Game")
    st.write("\n")
    # print game docs here:
    gameplay.print_game_rules()

    if start_game_button:
        st.session_state.current_page = "play round"
        st.experimental_rerun()
        
    wcs.back_widget(to="lobby") # goes back to lobby page

def convert_to_number(s):
    return int.from_bytes(s.encode(), 'little')

def same_scenarios(num_of_scenarios=5):
    """
    Problem is scenarios shown in each round are not the same for all players (per game per round)
    Function steps to get deterministic/ same scenarios for all players
    """
    # pull scenarios from snowflake
    query = """
        SELECT SCENARIO_TEXT
        FROM SCENARIO_METADATA
        """
    all_scenarios_list = snow.pull(query=query)['SCENARIO_TEXT'].to_list()

    # unique ID for game ID but same every time
    game_code_seed = convert_to_number(st.session_state.game_code)  
    random.Random(game_code_seed).shuffle(all_scenarios_list)
    
    # return 0-4 scenarios for 1st round, 5-9 second round, etc.
    start_indx = num_of_scenarios * st.session_state["round"] % len(all_scenarios_list) 
    end_indx = start_indx + num_of_scenarios
    if start_indx < len(all_scenarios_list) and end_indx <= len(all_scenarios_list):
         st.session_state["options_to_display"] = all_scenarios_list[start_indx:end_indx]

    else:
        end_indx = num_of_scenarios - (len(all_scenarios_list) - start_indx)
        st.session_state["options_to_display"] = all_scenarios_list[start_indx:] + all_scenarios_list[:end_indx]

    return None
    
def play_round_page():
    st.set_page_config(page_title="Worst Case Scenario", layout="wide", initial_sidebar_state="expanded")
    # TEMPORARY BEFORE DB SETUP:Read rows from a text file and store them in a Pandas DataFrame
    # the full file path is actually scenarios_file_path = "/app/worstcasescenario/app/rows.txt"
    # NOTE: this is how snowflake data is inserted into SCENARIO_METADATA TABLE
    # gameplay.push_rows_to_db(file_path="app/rows.txt")
    if "round" not in st.session_state:
        st.session_state["round"] = 0
    # TODO: simplify this logic, does new_round need to be a variable?
    if "options_to_display" not in st.session_state or (
        st.session_state["new_round"] and st.button("Next Round")
    ):
        # select 5 options to display
        same_scenarios()
        st.session_state["new_round"] = False

    if st.button("Next Round"):
        # TODO: Implement error checking logic. If not all users in this round of this game have submitted rankings, don't advance round if pressed
        st.session_state["round"] += 1
        same_scenarios()
    options_to_display = st.session_state["options_to_display"]
    # data_to_display is a dataframe, subset of matching rows from data. data is 2 col dataframe with scenarios and rankings (is rankings needed?)
    # Create a DataFrame with the rows and an initial ranking of 0 for each row
    data_to_display = pd.DataFrame(
        {"scenarios": options_to_display, "ranking": [0] * len(options_to_display)},
        columns=["scenarios", "ranking"],
    )

    # Display the options and radio buttons for the current user
    st.write(
        f"{st.session_state.player_name}'s rankings for round {st.session_state['round']}:"
    )
    col1, col2, col3, col4, col5 = st.columns(5)
    rankings = []
    cols = [col1, col2, col3, col4, col5]
    current_rankings = pd.DataFrame(columns=["scenarios", "ranking"])
    for i, row in data_to_display.reset_index(drop=True).iterrows():
        radio = cols[i].radio(
            f"{row['scenarios']}",
            [1, 2, 3, 4, 5],
            ## create a unique key to keep radio ranking button save state consistent
            # currently on a per user, per column (1-5), and per round basis. perhaps change it to include the GAME index later?
            key=f"{st.session_state.player_name}-{i}-{st.session_state['round']}",
        )

        # Update the current_rankings DataFrame
        data_to_display.loc[
            data_to_display["scenarios"] == row["scenarios"], "ranking"
        ] = radio
        rankings.append(radio)
        
    # Generate "Submit" button to send user rankings to DB
    submit_rankings_button = st.button("Submit")
    if submit_rankings_button:
        # TODO: query game_id from db for current game (how?) and pass it into save_rankings_to_file
        
        # get player_ID from player_INFO table from DB
        query = f"""
        select PLAYER_ID, PLAYER_NAME from {DB_NAME}.{SCHEMA_NAME}.PLAYER_INFO
        """
        df_players = snow.pull(query)
        # get the dataframe of row with correct player name (from .loc), then get the player_id column as a pd series, then take the first index value
        curr_player_id = df_players.loc[df_players.PLAYER_NAME == st.session_state.player_name]['PLAYER_ID'].values[0]
        
        query = f"""
        select * from {DB_NAME}.{SCHEMA_NAME}.GAMES
        where IS_ACTIVE = TRUE
        """
        # GAME_CODE,GAME_ID,GAME_TIME_START, IS_ACTIVE all included in df_games
        df_games = snow.pull(query)
        game_id = df_games[df_games['GAME_CODE']== st.session_state.game_code]["GAME_ID"].iloc[0]
        
        # write another function that generates scenario_ID's from data_to_display scenario_strings
        data_to_display['scenario_id'] = data_to_display.apply(lambda row: str(uuid.uuid4()), axis=1)
        # TODO: push that scenario & scenario ID table to SCENARIO_METADATA
        
        # then make save_rankings_to_db function take in scenario ID's and push the ranking data into snowflake when submitted
        gameplay.save_rankings_to_file(rankings, curr_player_id, data_to_display,round_id=st.session_state["round"],game_id=game_id)
        st.write(f"{st.session_state.game_code} {game_id} was submitted to db")
    
        # Show the rankings table for the current user, current round
        user_rankings = gameplay.get_user_rankings(curr_player_id).tail(5)
        st.write(user_rankings)

        st.write("\n\n\n")
        st.write("Newest rankings:")
        # st.write(user_rankings.drop(["player_id","round","game_id"], axis=1))
        wcs.back_widget(to="lobby")


        current_game, current_round = game_id, st.session_state.round
        # Check if all players have submitted
        ranking_query = f"""
            SELECT t1.SCENARIO_ID, t1.PLAYER_ID, t2.PLAYER_NAME, t1.RANK from {DB_NAME}.{SCHEMA_NAME}.RANKINGS t1
            JOIN {DB_NAME}.{SCHEMA_NAME}.PLAYER_INFO t2 ON t1.PLAYER_ID = t2.PLAYER_ID
            WHERE GAME_ID LIKE '{current_game}' AND ROUND_NO = {current_round}
            """
        rankings = snow.pull(ranking_query)
        lobby_query = f"""
            SELECT GAME_CODE, PLAYER_NAME from {DB_NAME}.{SCHEMA_NAME}.LOBBY_INFO
            WHERE GAME_CODE LIKE '{st.session_state.game_code}'
            """
        lobby = snow.pull(lobby_query)
        st.write("Waiting for other players...")
        while rankings["PLAYER_ID"].nunique() < lobby["PLAYER_NAME"].nunique():
            time.sleep(1)

        # Wait for everyone to submit scores
        victim="weslau"
        all_rankings = gameplay.get_all_rankings(current_game, current_round)
        st.write(all_rankings)
        distance_df = gameplay.get_player_distances(all_rankings, victim=victim)
        st.write(distance_df)
        gameplay.save_distances_to_db(current_game, current_round, distance_df) 


if __name__ == "__main__":

    page_dict = {
        "login": login_page,
        "create account": create_account_page,
        "login existing account": existing_account_page,
        "welcome": welcome_page,
        "lobby": lobby_page, ## page lists players in game and explains rules. combined game_start_page into lobby page
        "game start": game_start_page, ##unused
        "play round": play_round_page, ##this is the UI showing scenarios and UI for rankings
    }

    st.session_state.in_lobby = False

    if "current_page" not in st.session_state:
        login_page()

        current_game, current_round = "1234", 0
        all_rankings = gameplay.get_all_rankings(current_game, current_round)
        distance_df = gameplay.get_player_distances(all_rankings, victim="weslau")
        gameplay.save_distances_to_db(current_game, current_round, distance_df)
    
    else:
        page_dict[st.session_state.current_page]()
