import pandas as pd
import random
import streamlit as st
import uuid
import hashlib


# @st.cache_data
def display_user_rankings(player_id):
    user_rankings = get_user_rankings(player_id)
    return user_rankings


def read_rows_from_file(file_path):
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
    data_scenarios.columns = ["scenario_ID", "scenarios"]
    
    # #Push this dataframe to DB via API calls
    
    
    return data_scenarios


def get_user_rankings(player_id):
    # Load the current rankings from the CSV file (TODO: transition to DB table "RANKINGS")
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking", "game_id", "round"])

    # Filter the DataFrame to only show the rankings for the current user
    user_rankings = df[df["player_id"] == player_id]
    print(user_rankings)

    return user_rankings


def save_rankings_to_file(rankings, player_id, data_to_display, round_id, game_id):
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking", "game_id", "round"])

    # # Add the new rankings to the DataFrame
    # rankings and data_to_display are both dataframes with the same index, so rankings[i] will be ranking for scenario in data_to_display[i]
    new_rows = []
    for ranking, scenario in zip(rankings, data_to_display):
        new_rows.append({
            "player_id": player_id,
            "scenarios": scenario,
            "ranking": ranking,
            "round": round_id,
            "game_id": game_id,
        })

    # Concatenate the new rows with the existing DataFrame along the zeroth axis
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    st.write(df)
    # Save the updated DataFrame to the CSV file
    df.to_csv("rankings.csv", index=False)




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