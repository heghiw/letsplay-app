import streamlit as st
import pandas as pd
import json
from fuzzywuzzy import fuzz
from openai import OpenAI
import tiktoken


# --- OpenAI setup ---
client = OpenAI(api_key="")
ENCODING = tiktoken.encoding_for_model(MODEL_NAME)

def get_token_count(text):
    return len(ENCODING.encode(text)) if text.strip() else 0

def query_openai(prompt, max_tokens=50):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=1.0,
            top_p=0.95
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API Error: {e}")
        return ""

# --- Language selection ---
language = st.sidebar.selectbox("Choose Language", ["Czech", "English","Russian"])

# --- Load challenges ---
@st.cache_data
def load_challenges(lang):
    filename = (
    "challenge.json" if lang == "Czech"
    else "challenges_ru.json" if lang == "Russian"
    else "challenge_eng.json"
)
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

challenges = load_challenges(language)

# --- Session state ---
if "round" not in st.session_state:
    st.session_state.round = 1
if "prompt_submitted" not in st.session_state:
    st.session_state.prompt_submitted = False
if "scores" not in st.session_state:
    st.session_state.scores = []

# --- Welcome screen ---
if st.session_state.round == 1 and not st.session_state.prompt_submitted:
    st.title("🎮 Prompt Challenge Game")
    st.markdown("""
    #### Rules:
    1. Solve each task using a natural language prompt.
    2. The AI generates an output.
    3. You're scored by how close the output matches the target.
    4. Short prompts with good output earn more points!
    5. !!!MODEL OUTPUT SHOULD NOT BE PART OF THE MPROMPT!!!
    """)
    st.text_input("Your Name (optional)", key="player_name")
    st.markdown(f"**Language:** {language}")

# --- Game logic ---
current_round = st.session_state.round
max_rounds = len(challenges)

if current_round <= max_rounds:
    challenge = challenges[current_round - 1]
    challenge_text = challenge["task"]
    target_output = challenge["target"]

    st.markdown(f"### Round {current_round} of {max_rounds}")
    st.info(challenge_text)

    if not st.session_state.prompt_submitted:
        user_prompt = st.text_area("Your Prompt:", height=150, key="prompt_input")
        live_token_count = get_token_count(user_prompt)
        st.markdown(f"**Token count:** {live_token_count}")

        if st.button("Submit Prompt"):
            with st.spinner("Generating..."):
                model_output = query_openai(user_prompt.strip(), max_tokens=50)

                match_score = fuzz.ratio(model_output.lower(), target_output.lower())
                allowed_tokens = get_token_count(target_output)
                used_tokens = get_token_count(model_output)
                token_penalty = -(used_tokens - allowed_tokens) if used_tokens > allowed_tokens else 0
                final_score = max(0, match_score + token_penalty)

                score_data = {
                    "round": current_round,
                    "prompt": user_prompt,
                    "output": model_output,
                    "target": target_output,
                    "match_score": match_score,
                    "token_penalty": token_penalty,
                    "final_score": final_score
                }

                st.session_state.current_score = score_data
                st.session_state.prompt_submitted = True
                st.session_state.scores.append(score_data)

    if st.session_state.prompt_submitted:
        score = st.session_state.get("current_score", {})
        if score:
            st.subheader("Model Output")
            st.code(score["output"])
            st.subheader("Target Output")
            st.code(score["target"])
            st.subheader("Scoring Breakdown")
            col1, col2, col3 = st.columns(3)
            col1.metric("Fuzzy Match", f"{score['match_score']}%")
            col2.metric("Token Penalty", f"{score['token_penalty']}")
            col3.metric("Final Score", f"{score['final_score']}")

            if score["final_score"] >= 90:
                st.success("🔥 Excellent match!")
            elif score["final_score"] >= 60:
                st.warning("Not bad! Try to reduce tokens.")
            else:
                st.error("Needs improvement.")

        if st.button("Next Round"):
            st.session_state.round += 1
            st.session_state.prompt_submitted = False

else:
    st.balloons()
    st.title("Game Over 🎉")
    st.header("Final Scoreboard")

    df = pd.DataFrame(st.session_state.scores)
    if not df.empty:
        df["player"] = st.session_state.get("player_name", "You")
        leaderboard = df.pivot_table(index="player", values="final_score", aggfunc="sum")
        st.dataframe(leaderboard)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results as CSV", csv, "results.csv", "text/csv")

# --- Progress Bar ---
if st.session_state.round <= max_rounds:
    st.progress((st.session_state.round - 1) / max_rounds)

# --- Custom Style ---
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    textarea {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)
