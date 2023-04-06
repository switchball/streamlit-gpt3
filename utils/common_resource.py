import streamlit as st
from transformers import GPT2Tokenizer


@st.cache_resource(ttl=86400)
def get_tokenizer():
    """Loads the GPT-2 tokenizer from the model's tokenizer file."""
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    return tokenizer
