import dotenv
dotenv.load_dotenv()
from predict import generate_code_suggestion, is_veryfi_python_help_intent, update_index
import gradio as gr
import random
from typing import Optional, List, Tuple


greeting = \
"""
I was trained to answer questions about how to use the veryfi-python package.
Feel free to try me out. Cheers 🤖
"""



with gr.Blocks() as demo:
    chatbot = gr.Chatbot([(None, greeting)])
    user_input = gr.Textbox(label="Input")
    examples = gr.Examples(["Update index db (will pull in the latest code and re-build the search index)", 
                            "use veryfi-python package to delete document", 
                            "process document with url and extract fields",
                            "process w9 document"], inputs=user_input)
    clear = gr.Button("Clear")


    def user(user_message, history) -> Tuple[Optional[str], List[Tuple[Optional[str], Optional[str]]]]:
        return "", history + [[user_message, None]]


    def bot(history) -> Optional[List[str]]:
        user_question = history[-1][0]
        if "update index db" in user_question.lower():
            update_index()
            bot_message = "Index updated with the latest code changes 😎"
        elif is_veryfi_python_help_intent(user_question):
            bot_message : str = generate_code_suggestion(user_question.strip())
            if not bot_message:
                bot_message = "Sorry there was an error in my system. Diagnosing 🩺 ..."
        else:
            bot_message = "Sorry I wasn't trained to answer this question 😔"
        history[-1][1] = bot_message
        return history


    user_input.submit(fn=user, inputs=[user_input, chatbot], 
                                outputs=[user_input, chatbot])\
              .then(bot, inputs=[chatbot], outputs=[chatbot])
    clear.click(fn = lambda: None, inputs=None, outputs=[chatbot])


# Only run with share on an EC2 instance for testing
# demo.launch(share=True)
demo.launch()
