import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
import functions
import auth
import time
from datetime import datetime
import os
# No need to import io here as it's now in functions.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from functions import generate_pdf_report

# Set page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
auth.init_session_state()

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #25D366;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #128C7E;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #075E54;
    }
    .stat-label {
        color: #128C7E;
        font-weight: bold;
    }
    .sidebar-content {
        padding: 20px 0;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 0.8rem;
        color: #666;
    }
    .user-info {
        padding: 10px;
        background-color: #128C7E; 
        color: white;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
    }
    .btn-custom {
        background-color: #25D366;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .section-divider {
        margin: 40px 0;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar user section
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    # User Authentication Section
    if not st.session_state.logged_in:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/1200px-WhatsApp.svg.png", width=100)
        st.markdown("### WhatsApp Analyzer")
        
        # Create tabs for login and signup
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])        
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login")
                
                if submit_login:
                    if username and password:
                        success, message = auth.authenticate(username, password)
                        if success:
                            auth.login_user(username)
                            st.success(message)
                            st.rerun()  # Fixed: Changed from experimental_rerun to rerun
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter both username and password")
        
        with signup_tab:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_signup = st.form_submit_button("Create Account")
                
                if submit_signup:
                    if new_username and new_email and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            success, message = auth.create_user(new_username, new_password, new_email)
                            if success:
                                st.success(message)
                                st.info("Please login with your new account")
                            else:
                                st.error(message)
                    else:
                        st.warning("Please fill all fields")
        
        
    
    # Logged in user section
    else:
        # User info card
        st.markdown(f"""
        <div class="user-info">
            <h3>👤 {st.session_state.username}</h3>
            <p>Session duration: {auth.get_session_duration()} min</p>
        </div>
        """, unsafe_allow_html=True)
        
        
            # Show user history
        with st.expander("Your Analysis History"):
                history = auth.get_user_history(st.session_state.username)
                if history:
                    for i, entry in enumerate(reversed(history)):
                        if i >= 5:  # Show only last 5 analyses
                            break
                        st.write(f"📊 {entry['file_name']} - {entry['timestamp'].strftime('%d %b, %H:%M')}")
                else:
                    st.write("No analysis history yet")
        
        # Logout button
        if st.button("Logout"):
            auth.logout_user()
            st.rerun()  # Fixed: Changed from experimental_rerun to rerun
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Only show analysis options if logged in
    if st.session_state.logged_in:
        st.markdown("### Analysis Options")
        
        # This will be populated later when a file is uploaded
        if 'users' in st.session_state:
            users = st.session_state.users
            users_s = st.selectbox("Select User to View Analysis", users)
            
            if st.button("Show Analysis"):
                st.session_state.selected_user = users_s
                
                # Record this analysis in user history
                if st.session_state.username != "" and 'file_name' in st.session_state:
                    auth.record_analysis(
                        st.session_state.username, 
                        st.session_state.file_name, 
                        f"Analysis for {users_s}"
                    )

# Main page content
if st.session_state.logged_in:
    # Page Header
    st.markdown('<h1 class="main-header">📱 WhatsApp Chat Analyzer By Bhoomika</h1>', unsafe_allow_html=True)
    
    # Introduction section in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ### 📊 Analyze Your WhatsApp Chats with Ease
    
    This tool helps you analyze your WhatsApp conversations to uncover interesting patterns and statistics. 
    Export your chat (without media) from WhatsApp and upload the text file here to get started.
    
    **Features:**
    - Message frequency analysis
    - Emoji usage statistics
    - Most common words
    - Activity patterns by day and time
    - Monthly and daily timeline visualization
    - Word cloud generation
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown('<h2 class="sub-header">Upload Your Chat File</h2>', unsafe_allow_html=True)
    
    file = st.file_uploader("Choose WhatsApp chat export file (.txt)", type=["txt"])
    
    # Process the uploaded file
    if file:
        st.session_state.file_name = file.name
        
        with st.spinner('Processing your chat file...'):
            try:
                df = functions.generateDataFrame(file)
                
                # Storing users in session state for sidebar
                users = functions.getUsers(df)
                st.session_state.users = users
                
                # Date format selection with improved UI
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Configure Chat Settings")
                dayfirst = st.radio(
                    "Select Date Format in the chat file:",
                    ('dd-mm-yy', 'mm-dd-yy'),
                    horizontal=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                if dayfirst == 'dd-mm-yy':
                    dayfirst = True
                else:
                    dayfirst = False
                
                # Check if user has selected analysis in sidebar
                if 'selected_user' in st.session_state:
                    selected_user = st.session_state.selected_user
                    
                    st.markdown(f'<h2 class="sub-header">Analysis Results for: {selected_user}</h2>', unsafe_allow_html=True)
                    
                    df = functions.PreProcess(df, dayfirst)
                    if selected_user != "Everyone":
                        df = df[df['User'] == selected_user]
                    
                    # Get statistics
                    df, media_cnt, deleted_msgs_cnt, links_cnt, word_count, msg_count = functions.getStats(df)
                    
                    # Display chat statistics in an attractive layout
                    st.markdown('<h2 class="sub-header">Chat Overview</h2>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Total Messages</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{msg_count}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Total Words</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{word_count}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Media Shared</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{media_cnt}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Links Shared</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{links_cnt}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col5:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Deleted Messages</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{deleted_msgs_cnt}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # User Activity Count (only for Everyone)
                    if selected_user == 'Everyone':
                        st.markdown('<h2 class="sub-header">User Activity Analysis</h2>', unsafe_allow_html=True)
                        
                        # User count visualization
                        user_counts = df['User'].value_counts()
                        
                        # Create two columns for the user activity
                        user_col1, user_col2 = st.columns(2)
                        
                        with user_col1:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader("Message Count by User")
                            fig, ax = plt.subplots()
                            bars = ax.bar(user_counts.index, user_counts.values, color=sns.color_palette("viridis", len(user_counts)))
                            plt.xticks(rotation='vertical')
                            plt.ylabel("Number of Messages")
                            st.pyplot(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with user_col2:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader("Message Percentage by User")
                            fig, ax = plt.subplots()
                            plt.pie(user_counts.values, labels=user_counts.index, autopct='%1.1f%%', startangle=90, 
                                   colors=sns.color_palette("viridis", len(user_counts)))
                            plt.axis('equal')
                            st.pyplot(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Add a divider
                        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Emoji Analysis
                    st.markdown('<h2 class="sub-header">Emoji Analysis</h2>', unsafe_allow_html=True)
                    
                    emoji_df = functions.getEmoji(df)
                    
                    if not emoji_df.empty:
                        emoji_df.columns = ['Emoji', 'Count']
                        
                        # Create two columns for emoji analysis
                        emoji_col1, emoji_col2 = st.columns(2)
                        
                        with emoji_col1:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader("Top Emojis Used")
                            
                            fig, ax = plt.subplots()
                            # Show only top 10 emojis
                            top_emojis = emoji_df.head(10)
                            ax.bar(top_emojis['Emoji'], top_emojis['Count'], color=sns.color_palette("YlOrRd", len(top_emojis)))
                            plt.xticks(rotation='vertical')
                            st.pyplot(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with emoji_col2:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader("Emoji Distribution")
                            
                            top_emojis = emoji_df.head(8)  # Limit to top 8 for better visualization
                            fig, ax = plt.subplots()
                            plt.pie(top_emojis['Count'], labels=top_emojis['Emoji'], autopct='%1.1f%%', startangle=90,
                                   colors=sns.color_palette("YlOrRd", len(top_emojis)))
                            plt.axis('equal')
                            st.pyplot(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No emojis found in the selected chat.")
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Most Common Words Analysis
                    st.markdown('<h2 class="sub-header">Most Common Words</h2>', unsafe_allow_html=True)
                    
                    common_words = functions.MostCommonWords(df)
                    if not common_words.empty:
                        common_words.columns = ['Word', 'Count']
                        
                        words_col1, words_col2 = st.columns(2)
                        
                        with words_col1:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader("Top Words")
                            
                            fig, ax = plt.subplots()
                            y_pos = np.arange(len(common_words.head(10)))
                            ax.barh(y_pos, common_words.head(10)['Count'], align='center', color=sns.color_palette("Blues_r", len(common_words.head(10))))
                            ax.set_yticks(y_pos)
                            ax.set_yticklabels(common_words.head(10)['Word'])
                            ax.invert_yaxis()
                            plt.xlabel('Frequency')
                            st.pyplot(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with words_col2:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader("Word Cloud")
                            
                            try:
                                word_cloud = functions.create_wordcloud(df)
                                fig, ax = plt.subplots()
                                plt.imshow(word_cloud, interpolation='bilinear')
                                plt.axis('off')
                                st.pyplot(fig)
                            except Exception as e:
                                st.error(f"Error generating wordcloud: {e}")
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("No common words found after filtering stop words.")
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Activity Patterns
                    st.markdown('<h2 class="sub-header">Activity Patterns</h2>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("Daily Activity")
                        functions.WeekAct(df)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("Monthly Activity")
                        functions.MonthAct(df)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Daily timeline
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    functions.dailytimeline(df)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Activity heatmap
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader("Activity Heatmap")
                    
                    user_heatmap = functions.activity_heatmap(df)
                    fig, ax = plt.subplots(figsize=(12, 8))
                    sns.heatmap(user_heatmap, cmap="YlGnBu", ax=ax)
                    plt.title('Activity Heat Map')
                    plt.xlabel('Hour of Day')
                    plt.ylabel('Day of Week')
                    st.pyplot(fig)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Report download section
                    st.markdown('<h2 class="sub-header">Generate PDF Report</h2>', unsafe_allow_html=True)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    
                    if st.button("Generate PDF Report", key="pdf_report"):
                        with st.spinner("Generating PDF report..."):
                            try:
                                # Generate PDF using the imported function
                                pdf_buffer = functions.generate_pdf_report(
                                    df, media_cnt, deleted_msgs_cnt, links_cnt, 
                                    word_count, msg_count, selected_user,
                                    emoji_df=emoji_df if 'emoji_df' in locals() else None,
                                    common_words=common_words if 'common_words' in locals() else None
                                )
                                
                                # Create download button
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"whatsapp_analysis_{selected_user}_{timestamp}.pdf"
                                
                                st.markdown(
                                    f"""
                                    <div id="pdf_download_success" style="color: #1e8e3e; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #e6f4ea; display: none;">
                                     ✅ PDF report downloaded successfully!
                                    </div>
                                    """, 
                                   unsafe_allow_html=True
                               )
                                
                                st.download_button(
                                    label="Click here if download doesn't start automatically",
                                    data=pdf_buffer,
                                    file_name=filename,
                                    mime="application/pdf",
                                    key="download_pdf"
                                )
                                
                                st.success("PDF report generated successfully!")
                                
                                if st.session_state.username != "":
                                    auth.record_analysis(
                                        st.session_state.username, 
                                        st.session_state.file_name, 
                                        f"Downloaded PDF report for {selected_user}"
                                       )
                                
                                
                            except Exception as e:
                                st.error(f"Error generating PDF report: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error processing file: {e}")
                st.error("Please make sure you've uploaded a valid WhatsApp chat export file.")
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("WhatsApp Chat Analyzer Project by Bhoomika N ")
    st.markdown("Export your WhatsApp chat (without media) and upload the .txt file to analyze.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Display login page for users who aren't logged in
    st.markdown('<h1 class="main-header">📱 WhatsApp Chat Analyzer by Bhoomika</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)


    st.markdown(
    """
    
    ## Follow these steps to analyze your WhatsApp chats:
    1️⃣ **Open WhatsApp** on your phone.  
    2️⃣ **Select the chat** (individual or group) you want to export.  
    3️⃣ **Tap the three-dot menu** (on Android) or **tap the chat name** (on iPhone).  
    4️⃣ **Choose "More"** and select **"Export Chat"**.  
    5️⃣ **Select "Export without media"** to save only text messages.  
    6️⃣ **Choose your export method** (email, Google Drive, or another app).  
    7️⃣ **Send or save the file** to your preferred location.  

    📂 **Your chat will be saved as a `.txt` file. Use this file for analysis!**

    ---

    # 🔐 Please Log In or Create an Account  
    ## Unlock ALL THE FEATURES:
    ✅ **Detailed Chat Analysis** – Get a comprehensive explanation of your chat history.  
    ✅ **Customized Insights** – Filter and analyze messages by individual participants.  
    ✅ **Report Generation** – Summarize your chat analysis into a structured report.  
    ✅ **PDF Export** – Download your generated report in a convenient PDF format.  

    🚀 Start exploring your chats like never before!
    
    """
)
    
    
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
