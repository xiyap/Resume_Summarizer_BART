import base64
import streamlit as st

import pymupdf
import re
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
import requests
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def set_background(image_file):
    with open(image_file, 'rb') as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
            background-size: cover;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html = True)

def extract_text_from_pdf(file):
    '''
    Extracts text from pdf and removes whitespace characters.
    
    Args:
        pdf_path (str): Path of pdf file.
        
    Returns:
        str: Text data extracted from pdf file.
    '''
    text = ''
    pdf_file = pymupdf.open(stream = file.read(), filetype = 'pdf')
    for page_num in range(len(pdf_file)):
        text += pdf_file.load_page(page_num).get_text()
        
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_contact_links(text):
    '''
    Extracts phone number, email and links from text data.
    
    Args:
        text (str): Text data.

    Returns:
        dict: Dictionary containing phone number, email and links extracted from input text data.
    '''
    email = []
    http_links = []
    
    phone = re.findall(r'\b\+?\d[\d-]{8,12}\d\b', text)
    links_with_email = re.findall(r'\S+\.(?!\d)\w{2,}?\S+', text)

    for link in links_with_email:
        email_detected = re.search(r'\S+@\S+\.\S{2,}', link)
        if email_detected:
            email.append(email_detected.group())
        else:
            if link.startswith('http'):
                http_links.append(link)
            else:
                http_link = 'https://' + link
                http_links.append(http_link)

    return {'phone': phone, 'email': email, 'links': http_links}

def text_summary(text):
    '''
    Summarizes the text data.
    
    Args:
        text (str): Text data.

    Returns:
        str: Summary of input text data.
    '''
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model_name = 'facebook/bart-large-cnn'
    model = BartForConditionalGeneration.from_pretrained(model_name).to(device)
    tokenizer = BartTokenizer.from_pretrained(model_name)

    tokenized_data = tokenizer.encode('summarize: ' + text, return_tensors = 'pt', max_length = 1024, truncation = True).to(device)
    tokenized_summary = model.generate(tokenized_data, max_length = 150, min_length = 50, length_penalty = 2.0, num_beams = 4, early_stopping = True)

    text_summary = tokenizer.decode(tokenized_summary[0], skip_special_tokens = True)
    
    return text_summary

def text_summary_api(text):
    '''
    Summarizes the text data using Hugging Face's inference API.
    
    Args:
        text (str): Text data.

    Returns:
        str: Summary of input text data.
    '''
    API_URL = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn'
    headers = {'Authorization': f"Bearer {st.secrets['huggingface_api_key']}"}

    payload = {
        'inputs': 'summarize: ' + text,
        'parameters': {'max_length': 150, 'min_length': 50, 'length_penalty': 2.0, 'num_beams': 4, 'early_stopping': True},
        'options': {'wait_for_model': True}
    }

    response = requests.post(API_URL, headers = headers, json = payload)
    text_summary = response.json()[0]['summary_text']
    
    return text_summary

def plot_wordcloud(text):
    '''
    Plots a wordcloud for text data.
    
    Args:
        text (str): Text data.

    Returns:
        Plot: Plots the word cloud of the input text data.
    '''
    wordcloud = WordCloud(width = 800, height = 400, background_color = 'white').generate(text)
    plt.figure(figsize = (12, 8))
    plt.imshow(wordcloud)
    plt.axis('off')
    return plt.gcf()