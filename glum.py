import openai
import logging
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_response(messages):
    try:
        # Volání OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=128
        )
        message = response['choices'][0]['message']['content'].strip()
        return message
    except Exception as e:
        logging.error(f'Error: {e}')
        return str(e)
