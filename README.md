# Diamond in the Rough

**Play the game live:** [Diamond in the Rough](https://sippyr.github.io/Diamond_In_The_Rough/?utm_source=gemini)

## Project Overview

**Diamond in the Rough** is a daily baseball trivia game inspired by Wordle and the Immaculate Grid. Players are presented with a baseball field where they must identify a player and a specific season that fits a given statistical or team-based category for each of the 9 positions.

The ultimate goal is to identify the player/season combinations that yield the highest **Wins Above Replacement (WAR)** for each square.

### Key Features

* **Daily Categories:** Just like Wordle, the categories change every day for all players using a daily seeded random generator.

* **WAR Optimization:** Guessing a correct player grants you their WAR for that season. Finding the absolute best possible answer (Max WAR) for a square highlights it in blue.

* **Hard Mode:** A toggleable challenge that restricts players to only one guess per position. Miss it, and the square is locked!

* **Social Sharing:** Share your daily results and total WAR score with friends using a generated emoji grid.

## Tech Stack

This project was built with a full-stack approach across multiple cloud hosting platforms:

* **Frontend:** HTML, CSS, and Vanilla JavaScript. Hosted on **GitHub Pages**. Handles state management, daily seed generation, and UI/UX interactions.

* **Backend:** Python **Flask** API. Hosted on **Render**. Processes guesses, calculates WAR percentages, queries for the optimal daily lineup, and serves autocomplete suggestions.

* **Database:** **PostgreSQL** hosted on **neon.tech**.

## Data Integration & Pipeline

A significant challenge in this project was acquiring, cleaning, and merging baseball data from three distinct sources to create a seamless experience:

1. **The Baseball Scholar:** Base historical player statistics.

2. **Lahman Baseball Database:** Merged to acquire specific team data for each player/season, including complex logic for traded players.

3. **MLB Advanced Media (MLBAM):** Integrated via Chadwick Register lookup tables. By mapping Baseball-Reference IDs to MLBAM IDs, the frontend dynamically fetches and displays official player headshots upon a successful guess.

*(See `dataCleanup.py` for the normalization and merging logic).*

## Future Work

* **Mobile Optimization:** Improve UI/UX responsiveness for mobile devices.

* **Expanded Categories:** Add new trivia requirements such as "Won a World Series", "MVP", or specific playoff stats.

* **Endless Mode:** Allow users to shuffle the board and play continuous, randomized games without waiting for the next day.

* **Leaderboards:** Implement a way to see how your score ranks against all other daily players.