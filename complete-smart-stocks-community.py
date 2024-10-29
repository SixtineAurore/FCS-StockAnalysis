import streamlit as st
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import sqlite3
import hashlib

#titel
st.set_page_config(
    page_title="Smart Stocks",   
)

#styling mit CSS (Armin)
st.write(''' <style> /* eingebettetes CSS, daher <> und </> zum öffnen und schliessen von commands wie in html/css */
         /* company logo color ist 43,103,176 in RGB und #2b67b0 in hex */
         
    
        input[type="password"], input[type="text"] {
        background-color: #b3d8ff;
        padding: 0px;
        font-size: 2em;
        border: 4px solid #2b67b0;
        border-radius: 8px;
        margin-bottom: 0px;
        width: 100%;
        box-sizing: border-box;
    }

        body, h1, h2, h3, h4, h5, h6, p, div, label, span {
        font-family: 'Verdana', sans-serif;
        color: #2b67b0;
        
    }

    /* Hintergrundfarbe */
    [data-testid="stAppViewContainer"] {
        background-color: #89CFF0; 
        
    }
    
         </style>''', unsafe_allow_html=True)  #muss man machen um automatisches "Übergehen" von html bzw css code zu umgehen

# Database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    risk_preference TEXT,
    favorite_industries TEXT,
    reasons_membership TEXT,
    favorite_stock TEXT
)
''')

# Create messages table for chat functionality
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender) REFERENCES users (username),
    FOREIGN KEY (receiver) REFERENCES users (username)
)
''')

conn.commit()

# Password hashing function for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registration function
def register():
    username = st.text_input("Please enter a username*:")
    if username:
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            st.write("Username already exists. Please choose another.")
            return
        
        password = st.text_input("Please enter a password*:", type="password")
        risk_types = ["Low", "Medium", "High"]
        risk_preference = st.selectbox("Risk appetite:", risk_types)
        
        industries = ["Technology", "Healthcare", "Financials", "Energy", "Consumer Goods", "Utilities"]
        favorite_industries = st.selectbox("Favorite industry:", industries)
        
        favorite_stock = st.text_input("Favorite stock symbol:")
        reasons = ["Access to stock analysis", "Network with investors", "Curiosity"]
        reasons_membership = st.selectbox("Reason for joining:", reasons)

        if st.button("Register"):
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, risk_preference, favorite_industries, reasons_membership, favorite_stock) VALUES (?, ?, ?, ?, ?, ?)",
                (username, hashed_password, risk_preference, favorite_industries, reasons_membership, favorite_stock)
            )
            conn.commit()
            st.write("Registration successful!")

# Login function
def login():
    username = st.text_input("Username:")
    if username:
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        if not user:
            st.write("Username not found.")
            return None
        
        password = st.text_input("Password:", type="password")
        if password:
            hashed_password = hash_password(password)
            if user[1] == hashed_password:
                st.write("Login successful!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                return username
            else:
                st.write("Incorrect password")
                return None

# Profile display function
def view_profile(username):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        st.write(f"**Profile for {username}:**")
        st.write(f"- Favorite Industry: {user[3]}")
        st.write(f"- Risk Preference: {user[2]}")
        st.write(f"- Membership Reason: {user[4]}")
        st.write(f"- Favorite Stock: {user[5]}")

# Introduction function placeholder
def intro():
    st.write("Welcome to Smart Stocks!")

# Stock analysis function with DCF calculation and plotting
def stock_analysis():
    st.write("Stock Analysis Tool")

    stock_symbol = st.text_input("Enter stock symbol:")
    if stock_symbol:
        yahoo_stock = yf.Ticker(stock_symbol)
        stock_data = yahoo_stock.history(period="1y")

        current_price_yahoo = stock_data['Close'].iloc[-1] #retrieves the most recent stock price; more in INFO doc
        eps_yahoo = yahoo_stock.info.get('trailingEps') #retrieves the latest EPS data

        st.write(f"Current stock price of {stock_symbol}: ${current_price_yahoo:.2f}")
        st.write(f"Earnings per share (EPS) of {stock_symbol}: {eps_yahoo}")

        if eps_yahoo:
            pe_ratio = current_price_yahoo / eps_yahoo
            st.write(f"The P/E ratio of {stock_symbol}: {pe_ratio:.2f}")
        else:
            st.write("P/E ratio is not available.")

        st.line_chart(stock_data['Close'])

    # Retrieve cashflow data from Yahoo Finance
    cashflow_data = yahoo_stock.cashflow
    st.write(cashflow_data)
    
    # Check if the 'Total Cash From Operating Activities' column exists
    if cashflow_data is not None and 'Total Cash From Operating Activities' in cashflow_data.columns:
        free_cash_flow_yahoo = cashflow_data.loc[:, 'Total Cash From Operating Activities'].iloc[0] #iloc indicates the exact location of the data we're looking for; more in INFO doc
        st.write(f"Free Cash Flow (Yahoo Finance): {free_cash_flow_yahoo}")

        if free_cash_flow_yahoo:  # Ensure free cash flow is available for DCF calculation
            discount_rate = 0.10
            growth_rate = 0.03 #IMPORTANT let's see if we want to change this or let people input it themselves
            years = 5
    
            # Calculate discounted cash flows over the given years
            for year in range(1, years +1):
                cash_flows = [free_cash_flow_yahoo * (1 + growth_rate) ** year / (1 + discount_rate) ** year]
            
            # Calculate terminal value using the last cash flow
            terminal_value = cash_flows[-1] * (1 + growth_rate) / (discount_rate - growth_rate)
            
            # Calculate total DCF value
            total_dcf_value = sum(cash_flows) + terminal_value
    
            st.write(f"The estimated DCF value of {stock_symbol}: ${total_dcf_value:.2f}")

            # Plot discounted cash flows
            plt.figure(figsize=(10, 5))
            plt.plot(range(1, years + 1), cash_flows, label='Discounted Cash Flows', marker='o')
            plt.title(f'Discounted Cash Flows for {stock_symbol}')
            plt.xlabel('Year')
            plt.ylabel('DCF (in $)')
            plt.grid(True)
            plt.legend()
    
            # Display the chart in Streamlit
            st.pyplot(plt.gcf()) 

        else:
            st.write("Free cash flow data is not available for DCF calculation.")
    else:
        st.write("Could not find 'Total Cash From Operating Activities' in the cashflow data.")

# New Community Functions
def find_similar_users(username):
    """Find users with similar interests and risk preferences"""
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    current_user = cursor.fetchone()
    
    if current_user:
        cursor.execute("""
            SELECT username, risk_preference, favorite_industries, favorite_stock 
            FROM users 
            WHERE username != ? 
            AND (risk_preference = ? OR favorite_industries = ? OR favorite_stock = ?)
        """, (username, current_user[2], current_user[3], current_user[5]))
        
        similar_users = cursor.fetchall()
        return similar_users
    return []

def save_message(sender, receiver, message):
    """Save a chat message to the database"""
    cursor.execute("""
        INSERT INTO messages (sender, receiver, message, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    """, (sender, receiver, message))
    conn.commit()

def get_chat_history(user1, user2):
    """Retrieve chat history between two users"""
    cursor.execute("""
        SELECT sender, message, timestamp 
        FROM messages 
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp ASC
    """, (user1, user2, user2, user1))
    return cursor.fetchall()

def community_page(username):
    st.header("Community")
    
    # Display similar users
    st.subheader("Users with Similar Interests")
    similar_users = find_similar_users(username)
    
    if similar_users:
        for user in similar_users:
            with st.expander(f"📊 {user[0]}'s Profile"):
                st.write(f"Risk Preference: {user[1]}")
                st.write(f"Favorite Industry: {user[2]}")
                st.write(f"Favorite Stock: {user[3]}")
                
                # Chat interface
                if st.button(f"Chat with {user[0]}", key=f"chat_{user[0]}"):
                    st.session_state.chat_with = user[0]
    else:
        st.write("No similar users found yet.")

    # Chat interface
    if "chat_with" in st.session_state:
        st.subheader(f"Chat with {st.session_state.chat_with}")
        
        # Display chat history
        chat_history = get_chat_history(username, st.session_state.chat_with)
        for msg in chat_history:
            sender, message, timestamp = msg
            if sender == username:
                st.write(f"You ({timestamp}): {message}")
            else:
                st.write(f"{sender} ({timestamp}): {message}")
        
        # Message input
        new_message = st.text_input("Type your message:", key="message_input")
        if st.button("Send"):
            if new_message.strip():
                save_message(username, st.session_state.chat_with, new_message)
                st.experimental_rerun()

# Main function for logged-in user
def main_after_login(username):
    st.title("Smart Stocks - User Portal")
    menu2 = ["Home", "Profile", "Stock Analysis", "Community"]
    choice = st.sidebar.selectbox("Menu", menu2)

    if choice == "Home":
        st.write("Welcome to the Home Page!")
    elif choice == "Profile":
        view_profile(username)
    elif choice == "Stock Analysis":
        stock_analysis()
    elif choice == "Community":
        community_page(username)

# Main function for initial app navigation (pre-login)
def main_initial():
    st.title("User Registration and Login System")
    menu = ["Who we are", "Register", "Login", "Exit"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        register()
    elif choice == "Login":
        username = login()
        if username:
            main_after_login(username)
    elif choice == "Who we are":
        intro()
    else:
        st.write("Goodbye!")

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        main_after_login(st.session_state["username"])
    else:
        main_initial()
