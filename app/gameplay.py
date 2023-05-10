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

    # Create a DataFrame with the rows and an initial ranking of 0 for each row
    data_scenarios = pd.DataFrame(
        {"scenarios": rows, "ranking": [0] * len(rows)},
        columns=["scenarios", "ranking"],
    )
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

    # # Only return the columns that need to be displayed, the rows must correspond to the scenarios that were sampled in data_to_display
    # user_rankings = user_rankings.loc[
    #     user_rankings["scenarios"].isin(data_to_display["scenarios"]),
    #     ["scenarios", "ranking"],
    # ]
    # user_rankings["scenarios"] = user_rankings["scenarios"].astype(str)
    # data_to_display["scenarios"] = data_to_display["scenarios"].astype(str)

    # # Merge user_rankings with data_to_display based on the scenarios column to ensure correct order and only display relevant columns
    # user_rankings = data_to_display[["scenarios"]].merge(
    #     user_rankings, on="scenarios", how="left"
    # )

    return user_rankings


def save_rankings_to_file(rankings, player_id, data_to_display):
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking"])

    # Add the new rankings to the DataFrame
    for i, ranking in enumerate(rankings):
        df = df.append(
            {
                "player_id": player_id,
                "scenarios": data_to_display[i],
                "ranking": ranking,
                "round": st.session_state["round"],
                "game_id": None,
            },
            ignore_index=True,
        )

    # Save the updated DataFrame to the CSV file
    df.to_csv("rankings.csv", index=False)


# Use SessionState to create an empty dataframe to store the player_id and associated username
if "players" not in st.session_state:
    st.session_state["players"] = pd.DataFrame(columns=["player_id", "username"])
# If the user has not yet logged in, display the login form
if "user" not in st.session_state or st.session_state["user"] == "":
    st.session_state["user"] = st.text_input("Enter your name:")
    if st.session_state["user"] != "":
        # Generate a player ID from hash of the user's username
        hash_object = hashlib.sha256(st.session_state["user"].encode())
        player_id = hash_object.hexdigest()
        # add player ID and input username string into st.session_state, used to save variables across streamlit app runs
        # session_state["players"] was created as a df, so you append a new row onto it using df.append
        st.session_state["players"] = st.session_state["players"].append(
            {"player_id": player_id, "username": st.session_state["user"]},
            ignore_index=True,
        )
        st.write(f"Welcome, {st.session_state['user']}! Your player ID is {player_id}.")


# Read rows from a text file and store them in a Pandas DataFrame
data_scenarios = read_rows_from_file("rows.txt")


def get_random_options():
    st.session_state["options_to_display"] = random.sample(
        data_scenarios["scenarios"].tolist(), 5
    )


if "round" not in st.session_state:
    st.session_state["round"] = 0

if "options_to_display" not in st.session_state or (
    st.session_state["new_round"] and st.button("Next Round")
):
    # Randomly select 5 options to display
    get_random_options()
    st.session_state["new_round"] = False

if st.button("Next Round"):
    # TODO: Implement error checking logic. If not all users in this round of this game have submitted rankings, don't advance round if pressed
    st.session_state["round"] += 1
    get_random_options()

options_to_display = st.session_state["options_to_display"]
##data_to_display is a dataframe, subset of matching rows from data. data is 2 col dataframe with scenarios and rankings (is rankings needed?)
# Create a DataFrame with the rows and an initial ranking of 0 for each row
data_to_display = pd.DataFrame(
    {"scenarios": options_to_display, "ranking": [0] * len(options_to_display)},
    columns=["scenarios", "ranking"],
)
# data_to_display = data_scenarios[data_scenarios["scenarios"].isin(options_to_display)]

# Display the options and radio buttons for the current user
st.write(
    f"{st.session_state['user']}'s rankings for round {st.session_state['round']}:"
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
        key=f"{st.session_state['user']}-{i}-{st.session_state['round']}",
    )

    # Update the current_rankings DataFrame
    data_to_display.loc[
        data_to_display["scenarios"] == row["scenarios"], "ranking"
    ] = radio
    rankings.append(radio)

##find first instance of player_id associated with username matching user entered string
if "players" in st.session_state and not st.session_state["players"].empty:
    player_id = (
        st.session_state["players"]
        .loc[
            st.session_state["players"]["username"] == st.session_state["user"],
            "player_id",
        ]
        .iloc[0]
    )
    save_rankings_to_file(rankings, player_id, st.session_state["options_to_display"])

    # Show the rankings table for the current user, current round
    user_rankings = get_user_rankings(player_id, data_to_display=data_to_display).tail(
        5
    )

    st.write("\n\n\n")
    st.write("Newest rankings:")
    st.write(user_rankings.drop("player_id", axis=1))

# Generate "Submit" button to send user rankings to Snowflake DB
if st.button("Submit"):
    # TODO: Implement sending user rankings to Snowflake DB
    st.write("User rankings submitted to Snowflake DB.")
