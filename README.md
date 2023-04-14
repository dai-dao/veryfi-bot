---
title: Veryfi Bot
emoji: 💻
colorFrom: yellow
colorTo: yellow
sdk: gradio
sdk_version: 3.24.1
app_file: app.py
pinned: false
---

## Also hosted on Huggingface for free
- https://huggingface.co/spaces/daidao-ai-100/veryfi-bot


## To install requirements
- make install

## OpenAI API Key
- In .env file:
```
export OPENAI_API_KEY= 
```

## To run the app
- make run

## To run algorithm test
- make test


## Chatbot application to answer questions about how to use the veryfi-python package


## Improvements
- improve the bot to not only suggest code, but also answer questions about what veryfi can do and what services are available

- Break into microservice architecture
    - the gradio app
    - ingesting and indexing documents
    - openai LLM service
    - grouping anagram algo service

- stream response to chatbot, instead of having user wait and print everything out at once
