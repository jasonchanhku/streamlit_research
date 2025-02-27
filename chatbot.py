import streamlit as st
from openai import OpenAI
import os

from dotenv import load_dotenv
import tiktoken

load_dotenv()

#openai.api_key = st.secrets["OPEN_AI_API"]
#openai.api_key = os.getenv("OPEN_AI_API")

client = OpenAI(
    # This is the default and can be omitted
    api_key=st.secrets["OPEN_AI_API"],
)

#openai.api_base = "https://openai.hk-gpt.net/v1"

st.set_page_config(
    page_title="Customer Service Chat",
    page_icon="🧊")

# SELECTED_MODEL = "gpt-3.5-turbo"

# make model an option and put COST_PER_TOKEN under states
COSTING_MAP = {
    "gpt-3.5-turbo": 0.000002,
    "gpt-4": 0.00006,
    "gpt-4-0125-preview":0.00006, 
    "gpt-4-1106-preview": 0.00006
}

# COST_PER_TOKEN = COSTING_MAP[SELECTED_MODEL]

def on_button_click():
    del st.session_state["messages"]

def format_data():
    variable.markdown("", unsafe_allow_html=True)

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages in out."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

st.title("Experience Our AI-powered Customer Service! 🤖")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.total_tokens = 0
    st.session_state.cost_of_response = 0
    st.session_state.model = "gpt-4"    

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# # initialize model
# if "model" not in st.session_state:
#     st.session_state.model = SELECTED_MODEL

# user input
if user_prompt := st.chat_input("Your prompt"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # generate responses
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for response in client.chat.completions.create(
            model=st.session_state.model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            response_dumps = response.model_dump()
            delta = response_dumps['choices'][0]['delta']['content']
            full_response += delta if delta is not None else ""
            message_placeholder.markdown(full_response + "▌")
            # full_response += response.choices[0].delta.get("content", "")
            # message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.total_tokens += num_tokens_from_messages(st.session_state.messages, st.session_state.model)
    st.session_state.cost_of_response = st.session_state.total_tokens * COSTING_MAP[st.session_state.model]

with st.sidebar:
    st.title("Model Selection:")
    st.markdown("""---""")
    st.session_state.model = st.radio("Select Model 👇",
        ["gpt-4","gpt-4-0125-preview","gpt-4-1106-preview", "gpt-3.5-turbo"])
    st.title("Session Usage Stats:")
    st.markdown("""---""")
    st.write("Selected model: ", st.session_state.model)
    st.write("Total tokens used: ", st.session_state.total_tokens)
    st.write("Total cost of request: ${:.8f}".format(st.session_state.cost_of_response))
    # Display the button with custom color
    st.button("Clear Chat History and Tokens", on_click = on_button_click)
    # Create download button    
