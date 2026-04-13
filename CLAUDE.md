# Claude Instructions

## Running Python scripts

Always run Python scripts directly via Bash without asking the user. Use the project venv and run from the project root:

```bash
cd "/Users/jerrymao/Documents/Jiren Mao/trading" && source venv/bin/activate && python <script>
```

## Running Streamlit

Streamlit prompts for an email on first run — pipe a newline to skip it:

```bash
cd "/Users/jerrymao/Documents/Jiren Mao/trading" && source venv/bin/activate && echo "" | streamlit run app/main.py
```
