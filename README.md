
# Prompt Challenge Game

A Streamlit app where players write prompts to match target outputs using GPT-3.5.

## How to Run

```bash
streamlit run app.py
````

## Requirements

* Python 3.8+
* OpenAI API key (`OPENAI_API_KEY` as environment variable)
* Dependencies in `requirements.txt`

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...  # or set it directly in the script for testing
```

## Description

* Enter a prompt to solve a challenge.
* GPT generates output.
* You’re scored on similarity to the target and token efficiency.
* Results and leaderboard appear after all rounds.


