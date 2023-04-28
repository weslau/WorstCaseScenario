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

    # Only return the columns that need to be displayed, and the latest rows
    user_rankings = (
        user_rankings[["scenarios", "ranking"]]
        .tail(len(data_to_display))
        .reset_index(drop=True)
    )

    return user_rankings


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
col1, col2, col3, col4, col5 = st.columns(5)
rankings = []
for i, row in data_to_display.iterrows():
    if i == 0:
        radio = col1.radio(
            f"{row['scenarios']}",
            [1, 2, 3, 4, 5],
            key=f"{st.session_state['user']}-{i}",
        )
    elif i == 1:
        radio = col2.radio(
            f"{row['scenarios']}",
            [1, 2, 3, 4, 5],
            key=f"{st.session_state['user']}-{i}",
        )
    elif i == 2:
        radio = col3.radio(
            f"{row['scenarios']}",
            [1, 2, 3, 4, 5],
            key=f"{st.session_state['user']}-{i}",
        )
    elif i == 3:
        radio = col4.radio(
            f"{row['scenarios']}",
            [1, 2, 3, 4, 5],
            key=f"{st.session_state['user']}-{i}",
        )
    elif i == 4:
        radio = col5.radio(
            f"{row['scenarios']}",
            [1, 2, 3, 4, 5],
            key=f"{st.session_state['user']}-{i}",
        )
    rankings.append(radio)
save_rankings_to_file(rankings, st.session_state["user"])

# Show the updated rankings table for the current user
user_rankings = get_user_rankings(st.session_state["user"])
st.write("\n\n\n")
st.write("Newest rankings:")
st.write(user_rankings)
