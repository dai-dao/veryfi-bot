import sys
import os
if not os.environ.get("OPENAI_API_KEY"):
    print("Please set OpenAI API key environment variable and then run the app")
    sys.exit()
import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")
import jsonlines
from typing import Tuple, List, Optional
from indexing import ingest_doc_page, build_index_db, get_index_db
from langchain.schema import Document
from langchain.vectorstores import Chroma


INDEX_NAME = "veryfi_python_client"
DOC_PAGE_URL = "https://raw.githubusercontent.com/veryfi/veryfi-python/master/veryfi/client.py"


"""
Ingest code file directly from github, extract function signatures and docstrings, generate embeddings for each function
and build vector database for the embeddings to use for retrieval

Ideally this part should be in its own microservice and expose a REST API endpoint
"""
def update_index():
    global vectordb
    documents : List[Document] = ingest_doc_page(DOC_PAGE_URL, INDEX_NAME)
    build_index_db(documents, INDEX_NAME)
    vectordb = get_index_db(INDEX_NAME)


# Load pre-built index if exists, else create new index
if os.path.isdir(INDEX_NAME):
    vectordb : Chroma = get_index_db(INDEX_NAME)
else:
    update_index()


def call_gpt_turbo(messages, token_len=300) -> Optional[str]:
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.,
    max_tokens=token_len,
  )
  if "choices" in response:
    if len(response["choices"]) > 0:
      out = response["choices"][0]["message"]["content"]
      return out.strip()
  return None


"""
Workaround to fix chatbot code formatting problem

https://github.com/gradio-app/gradio/issues/3531
"""
def parse_codeblock(text : str) -> str:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "```" in line:
            if line != "```":
                lines[i] = f'<pre><code class="{lines[i][3:]}">'
            else:
                lines[i] = '</code></pre>'
        else:
            if i > 0:
                lines[i] = "<br/>" + line.replace("<", "&lt;").replace(">", "&gt;")
    return "".join(lines)


"""
Call chatgpt to generate sample code for how to use the veryfi-python package, given a question in natural language

To give chatgpt some context, include 3 examples taken from the veryfi-python README page. The example is given in this format

input: {most_relevant_doc}\n{question}
output: {code}

{most_relevant_doc} is retrieved using embedding search over a pre-built index of all function signatures and docstrings
"""
def generate_code_suggestion(question : str) -> Optional[str]:
    def build_prompt_with_samples_for_code_suggestion() -> List[dict]:
        setup_code = \
        """
    from veryfi import Client

    client_id = 'your_client_id'
    client_secret = 'your_client_secret'
    username = 'your_username'
    api_key = 'your_password'
        """
        
        sample_question1 = "Use veryfi to OCR and extract data from a document"
        sample_code1 = \
        f"""
    {setup_code}

    categories = ['Grocery', 'Utilities', 'Travel']
    file_path = '/tmp/invoice.jpg'

    # This submits document for processing (takes 3-5 seconds to get response)
    veryfi_client = Client(client_id, client_secret, username, api_key)
    response = veryfi_client.process_document(file_path, categories=categories)
        """

        sample_question2 = "Use veryfi to OCR and extract data from a document with URL"
        sample_code2 = \
        f"""
    {setup_code}

    # This submits document for processing (takes 3-5 seconds to get response)
    veryfi_client = Client(client_id, client_secret, username, api_key)
    response = veryfi_client.process_document_url(url, external_id=some_id)
        """

        sample_question3 = "Use veryfi to update a document"
        sample_code3 = \
        f"""
    {setup_code}

    new_vendor = {{"name": "Starbucks", "address": "123 Easy Str, San Francisco, CA 94158"}}
    category = "Meals & Entertainment"
    new_total = 11.23
    veryfi_client.update_document(id=12345, vendor=new_vendor, category=new_category, total=new_total)
        """

        questions = [sample_question1, sample_question2, sample_question3]
        codes = [sample_code1, sample_code2, sample_code3]
        out = [{"role" : "system", "content" : """You are a helpful Python developer. I give you a few python code examples with documentation."""}]
        for q, c in zip(questions, codes):
            retrieved_docs : Tuple[Document, int] = vectordb.similarity_search_with_score(q)
            most_relevant_doc : str = retrieved_docs[0][0].page_content
            out.append({"role" : "user", "content" : f"{most_relevant_doc}\n{q.strip()}"})
            out.append({"role" : "assistant", "content" : c.strip()})
        
        return out

    #
    retrieved_docs : Tuple[Document, int] = vectordb.similarity_search_with_score(question)
    most_relevant_doc = retrieved_docs[0][0].page_content
    instruction = \
    """Using the provided function signature and documentation from veryfi OCR package. 
        Please give me Python code for this prompt.
    """.strip()
    messages = build_prompt_with_samples_for_code_suggestion()
    messages.append({"role" : "user", "content" : f"{instruction}\n{most_relevant_doc}\n{question.strip()}"})
    out = call_gpt_turbo(messages)
    if out:
        return parse_codeblock(out)
    return out


"""
Using chatgpt, provide a list of example prompts asking for help on using the veryfi-python package
Take the first sentence of all the docstrings in the code to use as prompts. This represents what user might ask

Prompt format: 
    input: {first_sentence_docstring}
    output: yes

This provides chatgpt with some context to which questions might be relevant to the 
veryfi-python package and which questions are not relevant

Currently this will use the first sentence of all docstrings as input to chatgpt, 
which will become a bottleneck if the package has hundreds of methods.
To scale this approach, the best solution is to fine-tune a custom model, and at inference time only need to 
input the question without the need to provide any examples.

"""
def is_veryfi_python_help_intent(question : str) -> bool:
    def build_prompt_with_samples_for_intent_detection() -> List[dict]:
        out = [{"role" : "system", "content" : """You are a helpful Python developer. 
                                                Please check if the following prompt is asking for help with the veryfi-python package.
                                                I give you a few examples.
                                                """}]
        # Take only the first sentence of the docstring as sample
        with jsonlines.open(f"data/{INDEX_NAME}_doc.jsonl", "r") as reader:
            for sample in reader:
                docstring = sample["docstring"]
                if docstring:
                    first_sentence = docstring.split("\n")[0].strip()
                    out.append({"role" : "user", "content" : first_sentence})
                    out.append({"role" : "assistant", "content" : "yes"})
        return out    

    instruction = \
    """
    Is this question asking for help on using the veryfi-python package?
    """
    messages = build_prompt_with_samples_for_intent_detection()
    messages.append({"role" : "user", "content" : f"{instruction}\n{question.strip()}"})
    out = call_gpt_turbo(messages, token_len=10)
    if out and "yes" in out.lower():
        return True
    return False