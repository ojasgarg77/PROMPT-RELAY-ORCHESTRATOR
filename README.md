# Prompt Relay Orchestrator

A command-line AI assistant that improves your prompts before answering them, automatically falls back across multiple models and providers if one fails, can search the web when it needs current information, and keeps its own conversation history manageable through auto-summarization.

## Features

**Two-stage response pipeline**
Every message you send goes through two steps: first, a small/fast "improver" model rewrites your message into a clearer, more focused prompt (using the AI's last question as context, if there was one). Then a second model — chosen based on the priority category you selected — actually answers the improved prompt.

**Provider choice**
Pick between OpenRouter or NVIDIA as your model provider at startup. Each has its own set of free models mapped into the same four priority categories.

**Priority-based model categories**
Choose Speed, Research, Coding, or Business as your priority. Each category maps to a curated list of free models suited to that kind of task, and a model is picked at random from that list for each answer.

**Automatic retry and fallback, at two separate stages**
- *Improver stage:* if the randomly chosen improver model fails or returns garbled output, it's dropped from the list and another is tried. If every model in the primary provider's improver list fails, the tool automatically falls back to a set of free Groq models before giving up and using your raw, unimproved input as a last resort.
- *Answering stage:* if the randomly chosen answering model fails, it's removed from the category's list and another model from the same category is tried instead.

**Garbage-output detection**
The improver step checks for tool-call-style garbage tokens in its output and retries the same model (up to a few times) before giving up on it entirely.

**Agentic web search**
If the answering model determines it needs current information (or you explicitly ask for a search), it responds with a special `SEARCH:<query>` signal instead of a direct answer. The tool detects this, queries the Tavily search API, feeds the results back into the conversation, and asks the model to produce a real answer using those results.

**Conversation memory with auto-summarization**
The tool tracks conversation history across turns. Once the history grows past a threshold, it's automatically summarized (split into "user questions" and "AI responses" sections) and replaced with a condensed summary, keeping later prompts from growing unmanageably long.

**Token and timing tracking**
Every turn reports how many tokens were used (including any extra tokens spent on web search follow-up calls) and how long the response took.

## Requirements

- Python 3.10 or newer
- At least one of: a free OpenRouter account, or a free NVIDIA Build account
- A free Groq account (used as the improver-stage fallback)
- A free Tavily account (used for web search)

You don't need every single provider to try the tool — but the improver fallback and the web search feature won't work without Groq and Tavily keys respectively.

## 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

## 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
If PowerShell blocks the script, run this once first:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Create your `.env` file

Create a file named exactly `.env` in the project root with the following four lines:

```
OPENROUTER_API_KEY=your_openrouter_key_here
NVIDIA_API_KEY=your_nvidia_key_here
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### Getting an OpenRouter API key
1. Sign up at [openrouter.ai](https://openrouter.ai).
2. Go to **Keys** in your account settings.
3. Click **Create Key**, name it, and copy it.
4. Paste it as `OPENROUTER_API_KEY`.

### Getting an NVIDIA API key
1. Sign up at [build.nvidia.com](https://build.nvidia.com).
2. Open any model's page and click **Get API Key**, or find it in account settings.
3. Click **Generate Key** — it starts with `nvapi-`.
4. Paste it as `NVIDIA_API_KEY`.

### Getting a Groq API key
1. Sign up at [console.groq.com](https://console.groq.com) (email verification required).
2. Go to [console.groq.com/keys](https://console.groq.com/keys).
3. Click **Create API Key**, name it, and copy it immediately — it's shown only once.
4. Paste it as `GROQ_API_KEY`.

### Getting a Tavily API key
1. Sign up at [app.tavily.com](https://app.tavily.com) — no credit card required, includes 1,000 free credits/month.
2. Copy an API key from your dashboard (it starts with `tvly-`).
3. Paste it as `TAVILY_API_KEY`.

## 5. Run the program

```bash
python orchestrator.py
```

Choose your provider, choose your priority category, and start chatting. The tool will handle prompt improvement, model selection, retries, and web search automatically as the conversation goes on.

## Project status

This project is under active development. Major fallback issues are left unadressed, I also aim to integrate selenium/playwright in the same.The code is entirely handwritten.

## Notes

- If a model repeatedly fails, check that the corresponding API key is valid and that you haven't exceeded that provider's free-tier rate limits.
- Web search requires a valid `TAVILY_API_KEY` — without one, the `SEARCH:` feature will raise an error if triggered.
