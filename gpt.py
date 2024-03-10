import requests
import logging as log
from config import max_sentences, max_tokens, temperature
from transformers import AutoTokenizer

levels = {'новичок': 'beginner', 'продвинутый': 'advanced'}

# log конфиг
log.basicConfig(
    level=log.INFO,
    filemode="w",
    filename="logbook.txt",
    format='%(asctime)s - %(levelname)s - %(message)s')


def get_resp(promt, prev_answer, subj, level):
    resp = requests.post(  # POST запрос
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": f"You are a {subj} teacher who talks to {level}."
                                              f"Answer in a maximum of {max_sentences} sentences. "},
                {"role": "user", "content": promt},
                {"role": "assistant", "content": f"Continue answer: {prev_answer}"}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    )
    if resp.status_code == 200 and 'choices' in resp.json():
        gpt_resp = resp.json()['choices'][0]['message']['content']
        log.info(f"Ответ gpt: {gpt_resp}")
        return gpt_resp.replace('"', "'")
    else:
        log.error(f"Ошибка: {resp.json()}")
        return "ERROR"
