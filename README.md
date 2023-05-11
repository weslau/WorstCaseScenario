# WorstCaseScenario

## Flow diagram the different pages of webapp

```mermaid
flowchart TD;

A[login] -->|clicks new account button| B[create account page]
A -->|clicks existing account button| C[existing account page]
A --> D(welcome)
B -->|creates account| D
B -->|clicks back button| A
C -->|logs in with existing account| D
C -->|clicks back button| A
F -->|Start Game| G(play_round_page)
F -->|goes back to game start| E
E -->|goes back to welcome| D
A -->|Continue as Guest| D(welcome)
D -->|Join Game| E(lobby)
D -->|Create Game| E(lobby)
E -->|Ready to Play| F(game_start_page)
G -->|Next Round| G
G -->|Submit| G
%% eventually we will want a way to finish the game
%% G -->|Finish game| F
```

tasks:
- getting a snowflake version of database to connect

- horizontal placement of buttons

-the database should have a column for round unique to game, should have a UUID column for game

- create logins where you can save users UUID so can calculate stats across rounds/games

- finding a "source" for scenarios that we can import to the rows.txt or whatever format

- come up with a set of examples, and then ask chatGPT to come up with many more examples
-> we can combine our results somehow at the end

- optional, the user can set a "theme" for the scenario's and then LLM/GPT can pick scenarios related to that theme

- in the scoring function, showing the results of your own ranking compared to the spymaster ranking - differences table

- we should have UUIDS associated with each scenario so we can do statistics at the end

- implement how users can vote on questions if they like or dislike them