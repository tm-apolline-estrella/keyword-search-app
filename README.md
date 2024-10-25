# Traditional Keyword Search vs. CoachAI
Run all commands from the root directory of this repo, unless specified otherwise.

## System requirements
You need to have Python 3.10 and Poetry already installed.

## Environment variables
For local development, get the env values from Bitwarden > [tm LLM8s] > CoachAI Local Env (Latest, w/ APIM) under the ### api ### section.

## Local setup
1. Make a virtual environment: `python3.10 -m venv .venv`
2. Activate `.venv`: `source .venv/bin/activate`
3. Install traditional keyword search dependencies: `pip3.10 install -r requirements.txt`
4. Under `src/components/coach_ai`, create a `.env` file from the `.env.sample`: `cp .env.sample .env`
5. Under `src/components/coach_ai`, run `direnv allow`. If that doesn't work, run `source .env`
6. Going back to the root directory, install CoachAI search dependencies: `make dev`
7. Run the streamlit app: `streamlit run app.py`
