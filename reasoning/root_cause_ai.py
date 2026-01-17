import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
def determine_root_cause(metrics_analysis: dict, log_analysis: dict) -> str:
    prompt = f"""
You are a Site Reliability Engineer.

Based ONLY on the facts below, determine the most likely root cause.
Return ONE concise sentence.
Do NOT suggest actions.
Do NOT speculate beyond the facts.

Metrics analysis:
{metrics_analysis}

Log analysis:
{log_analysis}
"""

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100,
            timeout=10
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        return "Root cause analysis unavailable due to AI service error"
