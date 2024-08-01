"""
Author: Sothyra Chan
Last Modified by: Sothyra Chan
Date Last Modified: 2024-08-01
Program Description: This module handles user input and interaction with the ChatGPT API.
Revision History:
  - 2024-07-31: Initial creation
  - 2024-08-01: Added error handling for API responses
"""

# Import necessary libraries
import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI

# Inital session state
if "generated" not in st.session_state:
    st.session_state["generated"] = [] #output from the model
if "past_conversation" not in st.session_state:
    st.session_state["past_conversation"] = [] #input of conversation history
if "input" not in st.session_state:
    st.session_state["input"] = "" #save input of past conversation history
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = [] #conversation session

# Create a function to retrieve and store user input
def get_text():
    """
    Get user input text.
    Returns:
        str: User input text
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                               placeholder="AI assistant here! Type and ask me anything...",
                               label_visibility='hidden')
    return input_text

# Define a function to start a new chat session
def new_chat():
    """
    Clears session state and commences a new chat session.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1,-1,-1):
        save.append("User:" + st.session_state["past_conversation"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past_conversation"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()

# Set the title of the app
st.title("MemoryBot AI Assistant")

# Get API key from user input
api_key = st.sidebar.text_input("Please Enter Your API-Key here: ", type="password")
MODEL = st.sidebar.selectbox(label='Model', options=["gpt-3.5-turbo", "gpt-2", "gpt-neo", "gpt-j", "gpt-3.5", "gpt-4"])

if api_key:
    try:
        # Create OpenAI instance
        llm = OpenAI(
            temperature=0,
            openai_api_key=api_key,
            model_name=MODEL,
        )

        # Create a conversation memory
        if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=10)

        # Create a conversation chain
        Conversation = ConversationChain(
            llm=llm,
            prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory,
        )

    except Exception as e:
        st.error(f"Failed to initialize OpenAI: {e}")  # Added error handling for initialization
else:
    st.error("No API found! Please enter your OpenAI API-Key to continue.")

# Create a button to start a new chat session
st.sidebar.button("New Chat", on_click=new_chat, type='primary')

# Get user input
user_input = get_text()

# Generate output using ConversationChain instance and the user input, and add the input to the conversation history
if user_input:
    output = Conversation.run(input=user_input)

    st.session_state.past_conversation.append(user_input)
    st.session_state.generated.append(output)

with st.expander("Conversation"):
    for i in range(len(st.session_state['generated'])-1,-1,-1):
        st.info(st.session_state["past_conversation"][i])
        st.success(st.session_state["generated"][i],icon=":robot_face:")