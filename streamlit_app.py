import streamlit as st
from utils import set_background, extract_text_from_pdf, extract_contact_links, text_summary, plot_wordcloud

st.set_page_config(page_title = "Ian's Resume Summarizer")
# set_background('./streamlit_data/background.jpg')

session_state = st.session_state

if 'extracted_data' not in session_state:
    session_state.extracted_data = {}

# Sidebar
with st.sidebar:
    '# Control Panel'
    st.divider()
    
    '## 1. Upload your resume 📝'
    file = st.file_uploader('', type = ['pdf'])
    st.divider()
    
    '## 2. Select features to extract ✅'
    show_summary = st.checkbox('Summary')
    show_contact = st.checkbox('Contact')
    show_email = st.checkbox('Email')
    show_links = st.checkbox('Links')
    show_wordcloud = st.checkbox('Word Cloud')

    st.divider()
    '## 3. Confirm selection and run 👍'
    if st.button('Screen Resume'):
        if file:
            progress_message = st.empty()
            progress_message.success('Screening in progress...')
            
            session_state.extracted_data = {}

            text = extract_text_from_pdf(file)
            contact_info = extract_contact_links(text)
            
            if show_summary:
                session_state.extracted_data['summary'] = text_summary(text)
            if show_contact:
                session_state.extracted_data['phone_numbers'] = '\n'.join(contact_info['phone'])
            if show_email:
                session_state.extracted_data['emails'] = '\n'.join(contact_info['email'])
            if show_links:
                session_state.extracted_data['links'] = '\n'.join(contact_info['links'])
            if show_wordcloud:
                session_state.extracted_data['wordcloud'] = plot_wordcloud(text)

            progress_message.success('Screening complete!')
        
        else:
            st.warning('Please upload a PDF file.')

# Main section
'''
# Ian's Resume Summarizer 🔍
### 👈 Follow the steps at the control panel to get started.
'''
st.divider()

if show_summary and 'summary' in session_state.extracted_data:
    st.subheader('Summary:')
    st.info(session_state.extracted_data['summary'])

left_column, right_column = st.columns(2)

if show_contact and 'phone_numbers' in session_state.extracted_data:
    left_column.subheader('Contact:')
    left_column.info(session_state.extracted_data['phone_numbers'])

if show_email and 'emails' in session_state.extracted_data:
    if show_contact and 'phone_numbers' in session_state.extracted_data:
        right_column.subheader('Email:')
        right_column.info(session_state.extracted_data['emails'])
    else:
        left_column.subheader('Email:')
        left_column.info(session_state.extracted_data['emails'])

if show_links and 'links' in session_state.extracted_data:
    st.subheader('Links:')
    st.markdown('<br>'.join(session_state.extracted_data['links'].split('\n')), unsafe_allow_html = True)

if show_wordcloud and 'wordcloud' in session_state.extracted_data:
    st.subheader('Word Cloud:')
    st.pyplot(session_state.extracted_data['wordcloud'])
       
# Footer
st.divider()
st.markdown('<style>footer {position: fixed;bottom: 0;width: 100%;}</style>', unsafe_allow_html = True)
st.markdown('''
#### Disclaimer
*This application is in its preliminary version and may contain inaccuracies. We do not guarantee the accuracy of the information extracted and are not liable for any harm caused by its use. Please verify all information independently.*
''')