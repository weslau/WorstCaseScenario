import pandas as pd
import random
import streamlit as st
import uuid
import hashlib


def read_rows_from_file(file_path):
    with open(file_path, "r") as f:
        rows = f.readlines()
        # Remove trailing '\n' characters from each row
        rows = [row.strip() for row in rows]

    # Create a DataFrame with the rows and an initial ranking of 0 for each row
    data = pd.DataFrame(
        {"scenarios": rows, "ranking": [0] * len(rows)},
        columns=["scenarios", "ranking"],
    )
    return data


def get_user_rankings(player_id, data_to_display):
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["player_id", "scenarios", "ranking"])

    # Filter the DataFrame to only show the rankings for the current user
    user_rankings = df[df["player_id"] == player_id]

    # Only return the columns that need to be displayed, the rows must correspond to the scenarios that were sampled in data_to_display
    user_rankings = user_rankings.loc[
        user_rankings["scenarios"].isin(data_to_display), ["scenarios", "ranking"]
    ]

    return user_rankings


def save_rankings_to_file(rankings, player_id):
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
                "scenarios": data.iloc[i]["scenarios"],
                "ranking": ranking,
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
data = read_rows_from_file("rows.txt")

# Randomly select 5 options to display
options_to_display = random.sample(data["scenarios"].tolist(), 5)
data_to_display = data[data["scenarios"].isin(options_to_display)]

# Display the options and radio buttons for the current user
st.write(f"{st.session_state['user']}'s rankings:")
col1, col2, col3, col4, col5 = st.columns(5)
rankings = []
cols = [col1, col2, col3, col4, col5]
for i, row in data_to_display.reset_index(drop=True).iterrows():
    radio = cols[i].radio(
        f"{row['scenarios']}", [1, 2, 3, 4, 5], key=f"{st.session_state['user']}-{i}"
    )
    rankings.append(radio)

##find first instance of player_id associated iwth username matching user entered string
if "players" in st.session_state and not st.session_state["players"].empty:
    player_id = (
        st.session_state["players"]
        .loc[
            st.session_state["players"]["username"] == st.session_state["user"],
            "player_id",
        ]
        .iloc[0]
    )
    save_rankings_to_file(rankings, player_id)

    # Show the updated rankings table for the current user
    user_rankings = get_user_rankings(player_id, data_to_display=data_to_display)
    st.write("\n\n\n")
    st.write("Newest rankings:")
    st.write(user_rankings)
