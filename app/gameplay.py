import numpy as np
import pandas as pd
import random
import streamlit as st
import uuid
import hashlib
import utils.snowflake as snow
import utils.wcs as wcs


DB_NAME = wcs.DB_NAME
SCHEMA_NAME = wcs.SCHEMA_NAME

# @st.cache_data
def display_user_rankings(player_id):
    user_rankings = get_user_rankings(player_id)
    return user_rankings

def push_rows_to_db(file_path):
    """upload scenarios from rows.txt to snowflake's SCENARIO_METADATA table
    also should annotate each scenario_text in file with a scenario_id

    Args:
        file_path (file-like object or str): file object representing a .txt where scenario_text's are stored one per row
    """
    with open(file_path, "r") as f:
        rows = f.readlines()
        # Remove trailing '\n' characters from each row
        rows = [row.strip() for row in rows]

    # Create a DataFrame with the rows and convert 'scenarios' to string type (in case it's not already)
    data_scenarios = pd.DataFrame({"scenarios": rows})
    data_scenarios['scenarios'] = data_scenarios['scenarios'].astype(str)

    # Generate a scenario ID from hash of each row in 'scenarios'
    # And create a new column for these as well
    data_scenarios["scenario_ID"] = data_scenarios["scenarios"].apply(lambda x: hash(x))

    # Group by the 'scenario_ID' to remove duplicate scenarios. for duplicate IDs, keep the first instance of scenario text with that ID
    data_scenarios = data_scenarios.groupby("scenario_ID")["scenarios"].first().reset_index()
    # Rename cols as reminder this is how df is ordered now
    data_scenarios.columns = ["scenario_id", "scenario_text"]
    
    # Push this dataframe to DB table called SCENARIO_METADATA via API calls
    for index, row in data_scenarios.iterrows():
        # scenario_id = row['scenario_id']
        # scenario_text = row['scenario_text']
        table_columns = ["SCENARIO_CATEGORY", "SCENARIO_ID", "SCENARIO_TEXT"]
        table_values = [None, row['scenario_id'], row['scenario_text']]
        snow.push("SCENARIO_METADATA", table_columns, table_values)
    
def get_user_rankings(player_id):
    # Load the current rankings from the CSV file (TODO: transition to DB table "RANKINGS")
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking", "game_id", "round"])

    # Filter the DataFrame to only show the rankings for the current user
    user_rankings = df[df["player_id"] == player_id]
    ##instead, get user rankings from RANKINGS table and  show the ones from current player
    # get player_ID from player_INFO table from DB
    DB_NAME = wcs.DB_NAME
    SCHEMA_NAME = wcs.SCHEMA_NAME
    query = f"""
    select PLAYER_ID, RANK, SCENARIO_ID from {DB_NAME}.{SCHEMA_NAME}.RANKINGS
    """
    df = snow.pull(query)
    user_rankings = df[df["PLAYER_ID"] == player_id]
    return user_rankings

def save_rankings_to_file(rankings, player_id, data_to_display, round_id, game_id):
    """saves the player ranking data and associated metadata into snowflake database RANKINGS table

    Args:
        rankings (_type_): _description_
        player_id (_type_): _description_
        data_to_display (_type_): _description_
        round_id (_type_): _description_
        game_id (_type_): _description_
    """
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking", "round", "game_id", "scenario_id"])

    # # # Add the new rankings to the DataFrame
    # # rankings and data_to_display are both dataframes with the same index, so rankings[i] will be ranking for scenario in data_to_display[i]
    # new_rows = []
    # for i, (ranking, row) in enumerate(zip(rankings, data_to_display.iterrows())):
    #     new_rows.append({
    #         "player_id": player_id,
    #         "scenarios": row['scenarios'],
    #         "ranking": ranking,
    #         "round": round_id,
    #         "game_id": game_id,
    #         "scenario_id": row['scenario_id']
    #     })

    # # Concatenate the new rows with the existing DataFrame along the zeroth axis
    # df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    # # Convert the list of dictionaries to a pandas DataFrame
    # new_rankings_df = pd.DataFrame(new_rows, index=data_to_display.index)

    # # st.write(new_rankings_df)
    
    # push the new_rows data into snowflake database RANKINGS table
    for (index, row), ranking in zip(data_to_display.iterrows(), rankings):
        table_columns = ["GAME_ID", "PLAYER_ID", "RANK", "ROUND_NO", "SCENARIO_ID"]
        table_values = [game_id, player_id, ranking, round_id, row.loc["scenario_id"]]
        # st.write(table_columns, table_values)
        snow.push("RANKINGS", table_columns, table_values)
    
    # Save the updated DataFrame to the CSV file
    df.to_csv("rankings.csv", index=False)

def get_all_rankings(current_game, current_round):
    query = f"""
        SELECT t3.SCENARIO_TEXT, t1.PLAYER_ID, t2.PLAYER_NAME, t1.RANK from {DB_NAME}.{SCHEMA_NAME}.RANKINGS t1
        JOIN {DB_NAME}.{SCHEMA_NAME}.PLAYER_INFO t2 ON t1.PLAYER_ID = t2.PLAYER_ID
        JOIN {DB_NAME}.{SCHEMA_NAME}.SCENARIO_METADATA t3 on t1.SCENARIO_ID = t3.SCENARIO_ID
        WHERE GAME_ID LIKE '{current_game}' AND ROUND_NO = {current_round}
        """
    rankings = snow.pull(query)
    all_rankings = pd.pivot_table(rankings, values='RANK', index='SCENARIO_TEXT', columns='PLAYER_NAME', aggfunc='sum')
    return all_rankings


def get_player_distances(all_rankings, victim):
    victim_choice = all_rankings[victim].values
    distances = {}
    for player in all_rankings.columns:
        # if player == victim:
        #     continue
        player_guess = all_rankings[player].values
        distance = np.linalg.norm(victim_choice - player_guess)
        # distances[player] = distance
        distances[player] = [player, distance]
    distance_df = pd.DataFrame.from_dict(distances, orient='index', columns=['Player', 'Distance']).reset_index(drop=True)
    return distance_df

def save_distances_to_db(current_game, current_round, distance_df):
    columns = ["GAME_ID", "ROUND_NO", "PLAYER_ID", "PLAYER_SCORE"]

    for index, row in distance_df.iterrows():
        values = [current_game, current_round, row["Player"], row["Distance"]]
        snow.push(table_name="PLAYER_SCORES", columns=columns, values=values)

def print_game_rules():
    st.markdown('''
    ## HOW TO PLAY

    1. Player One starts the game as "The Victim", and each player takes turns to go first in subsequent rounds of the game.

    2. READ THE SCENARIOS! The Victim then reads aloud, one by one, the five worst-case scenario presented after pressing the "Start Game" button

    3. RANK ‘EM! What scenario is bad, very bad, awful, horrible, or the worst...according to The Victim? Every player, including The Victim, decides how The Victim will rank the five cards from 1-5, selecting a ranking option under each scenario in the webapp (see below notes).

    - Table talk is encouraged, but players should be discreet about their selection, so nobody knows how other players rank the five cards.

    4. REVEAL ‘EM! After all players have made their selections, The Victim reads aloud their ranking and reveals the other players' rankings of the scenarios. Players who match The Victim's number should rejoice.

    5. SCORING TIME! Players get one point for every chip that matched one of The Victim's chips. The Victim gets the same number of points as the player(s) with the most points (including any bonus). Remember, we said the scorekeeper needs to be responsible!

    6. READY FOR THE NEXT ROUND! After the scorekeeper tallies everyone’s scores, the scenarios are reset. The player to the left starts a new round as The Victim, and a new set of scenarios are displayed. Play moves clockwise.

    ## HOW TO WIN

    In a 3, 4, or 6-player game, the player with the most points after 12 rounds wins the game. In a 5-player game, the player with the most points after 10 rounds wins the game. If there is a tie at the end, continue play until the tie is broken and a winner is declared. For a quicker game, all players can simply have one less round playing The Victim.

    ## NOTES ON PLAY

    - The Victim changes every round, and every player has an equal number of rounds playing The Victim.
    - Always rank the cards secretly based on how you think The Victim will rank the cards.
    ''')
    
def compare_ranking(victim_playerid, second_playerid, df_gameplay):
    return 0