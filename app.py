import pandas as pd
import random
import streamlit as st


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


def get_user_rankings(user):
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["user", "scenarios", "ranking"])

    # Filter the DataFrame to only show the rankings for the current user
    user_rankings = df[df["user"] == user].reset_index(drop=True)

    # Only return the columns that need to be displayed
    user_rankings = user_rankings[["scenarios", "ranking"]]

    return user_rankings.tail(len(data_to_display))


def save_rankings_to_file(rankings, user):
    # Load the current rankings from the CSV file
    try:
        df = pd.read_csv("rankings.csv")
    except:
        df = pd.DataFrame(columns=["user", "scenarios", "ranking"])

    # Add the new rankings to the DataFrame
    for i, ranking in enumerate(rankings):
        df = df.append(
            {"user": user, "scenarios": data.iloc[i]["scenarios"], "ranking": ranking},
            ignore_index=True,
        )

    # Save the updated DataFrame to the CSV file
    df.to_csv("rankings.csv", index=False)


# Set the user name as a session state variable
if "user" not in st.session_state:
    st.session_state["user"] = ""

# If the user name is not set, display the text input to get the user name
if st.session_state["user"] == "":
    st.session_state["user"] = st.text_input("Enter your name:")

# Read rows from a text file and store them in a Pandas DataFrame
data = read_rows_from_file("rows.txt")

# Randomly select 5 options to display
options_to_display = random.sample(data["scenarios"].tolist(), 5)
data_to_display = data[data["scenarios"].isin(options_to_display)]

# Display the options and radio buttons for the current user
st.write(f"{st.session_state['user']}'s rankings:")
rankings = []
for i, row in data_to_display.iterrows():
    st.write(row["scenarios"])
    ranking = st.radio(
        f"Rank {i+1}", [1, 2, 3, 4, 5], key=f"{st.session_state['user']}-{i}"
    )
    rankings.append(ranking)
save_rankings_to_file(rankings, st.session_state["user"])

# Display the newest rankings from the user before submission
user_rankings = get_user_rankings(st.session_state["user"])
st.write("\n\n\n")
st.write("Newest rankings:")
st.write(user_rankings)
