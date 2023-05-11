import pandas as pd
import random
import streamlit as st
import uuid
import hashlib


# @st.cache_data
def display_user_rankings(player_id):
    user_rankings = get_user_rankings(player_id, data_to_display=data_to_display)
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


def get_user_rankings(player_id, data_to_display):
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking"])

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
    # for i, ranking in enumerate(rankings):
    #     new_row = {
    #         "player_id": player_id,
    #         "scenarios": data_to_display[i],
    #         "ranking": ranking,
    #         "round": st.session_state["round"],
    #         "game_id": None,
    #     }
    #     df = df.append(new_row, ignore_index=True)
    # Create a list of dictionaries representing new rows to be added to the DataFrame
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


def get_random_options():
    st.session_state["options_to_display"] = random.sample(
        data_scenarios["scenarios"].tolist(), 5
    )


def print_game_rules():
    st.markdown('''
    ## HOW TO PLAY

    1. SPIN AWAY! Player One, “The Victim,” starts the game by spinning The Victim Wheel and reading aloud the space they land on.

    2. FLIP ‘EM OVER! The Victim then turns over and reads aloud, one by one, the next five worst-case scenario cards...to create a row of five cards in the middle of the play area.

    3. RANK ‘EM! What scenario is bad, very bad, awful, horrible, or the worst...according to The Victim? Every player, including The Victim, decides how The Victim will rank the five cards from 1-5, by secretly placing their chips facedown next to each card (as shown below).

    - When there are 5-6 players, chips can be placed on either end of the card, so long as players remember their chip color.
    - Table talk is encouraged, but players should be discreet when placing their chips facedown, so nobody knows how other players rank the five cards.

    4. REVEAL ‘EM! After all players have made their selections, The Victim reads aloud the first card on their left and turns over the other players’ corresponding chips. The Victim then reveals the numbered chip they assigned to that card. Players who match The Victim’s number should rejoice. Turn non-matching chips over to the “X” side. Players repeat this step for the remaining four cards/chips until selections are revealed for all five cards.)

    5. SCORING TIME! Unless The Victim lands on SCORE YOUR CHIPS! (see The Victim Wheel page), players get one point for every chip that matched one of The Victim’s chips PLUS any bonus points awarded on The Victim Wheel. The Victim gets the same number of points as the player(s) with the most points (including any bonus). Remember, we said the scorekeeper needs to be responsible!

    6. READY FOR THE NEXT ROUND! After the scorekeeper tallies everyone’s scores, chips are returned to each player and used cards are removed from the play area. The Victim Wheel is passed to the player to the left, who starts a new round as The Victim, by spinning The Victim Wheel and turning over five new cards. Play moves clockwise.

    ## HOW TO WIN

    In a 3, 4, or 6-player game, the player with the most points after 12 rounds wins the game. In a 5-player game, the player with the most points after 10 rounds wins the game. If there is a tie at the end, continue play until the tie is broken and a winner is declared. For a quicker game, all players can simply have one less round playing The Victim.

    ## NOTES ON PLAY

    - The Victim changes every round, and every player has an equal number of rounds playing The Victim.
    - Always rank the cards secretly based on how you think The Victim will rank the cards.
    ''')