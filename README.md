# Diamond in the Rough

A daily baseball trivia game where users try to build the optimal team by guessing players who fit specific statistical and franchise categories. It is a full-stack web application featuring player autocomplete and live WAR (Wins Above Replacement) scoring, with a PostgreSQL database hosted on Neon, a Python Flask API hosted on Render, and a vanilla HTML/CSS/JS frontend hosted on GitHub Pages.

## Features

*   **Daily Seeded Puzzles:** Uses a Mulberry32 seeded randomizer tied to the calendar date so all players globally face the exact same grid on any given day.
*   **Live Player Autocomplete:** Queries the backend database in real-time as the user types to prevent spelling errors and streamline the guessing process.
*   **Dynamic WAR Scoring & Badges:** Calculates the submitted player's WAR against the highest possible WAR for that specific category, awarding a percentage-based badge (and a gold badge for a 100% optimal guess).
*   **Hard Mode:** A toggleable switch that restricts players to a single guess per square. Incorrect guesses lock the square with a red "MISSED" penalty.
*   **Optimal Lineup Reveal:** At the end of the game (or if the user clicks "Give Up"), players can fetch the mathematically best possible lineup from the database.
*   **Shareable Emoji Grid:** Generates an Immaculate Grid-style emoji layout formatted for the clipboard to easily share daily results.

## Architecture & Tech Stack

*   **Frontend (Static Web Hosting):** Vanilla HTML5, CSS3, and JavaScript deployed on **GitHub Pages**. Handles state management, daily seed generation, UI state transitions, and API interactions.
*   **Backend (REST API):** Python **Flask** application deployed on **Render** (via Gunicorn). Handles data validation, database connection pooling, and CORS management.
*   **Database (Cloud Relational):** **PostgreSQL** hosted on **Neon.tech**. Stores historical baseball statistics, franchise histories, and MLBAM IDs for rendering live player headshots directly from MLB.com.
