'''Instructions for how to understand and read the following code:
The following code is divided into five parts: 
1. Set up 
2. Welcome Page, Registration, and Log In
3. Logged-In User Interface
3.1 Profile Page
3.2 Data Analysis Page
3.3 Community Page
4. Menu and Page Navigations
(5. Bibliography)

For this code to run correctly, the following needs to be installed: streamlit, numpy, pandas, yfinance, matplotlib, scikit-learn'''

######################################## Set Up #########################################

##### Imports #####

import streamlit as st                            # Open Source Python library to work on the code all together 
import numpy as np                                # Open Source Python library to integrate mathematical functions 
import pandas as pd                               # Open Source Python library to integrate data analysis 
import yfinance as yf                             # API 
import matplotlib.pyplot as plt                   # Open Source Python library to integrate statics and animation 
import sqlite3                                    # Open Source Data Base management to store and manage data 
import hashlib                                    # Open Source Python library to integrate hashes 
from sklearn.linear_model import LinearRegression # Module to integrate linear regression model 

##### CSS Styling #####
st.write(''' <style> /* embedded CSS, therefore <> and </> in order to open and close commands according to html/css */
         /* company logo color is 43,103,176 in RGB and #2b67b0 in hex */
         
    
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

    /* Chart styling */


    
         </style>''', unsafe_allow_html=True)  #in order to avoid automatic "escaping" or sanitization of html or css code#


######################################## Welcome Page, Registration, and Log In#########################################

##### Homepage #####

def intro():
    st.write("Invest effortlessly using our data analysis tool.")
    st.image("LogoCS.png", width=700)


def Home():
    return None

##### Password Hashing #####

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


##### User Database Setup #####

# Users database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Creation of the table in the database if it doesn't exist yet
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    risk_preference TEXT,
    favorite_industries TEXT,
    reasons_membership TEXT,
    favorite_stock TEXT,
    linkedin_profile TEXT
)
''')

##### Registration #####

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
        
        favorite_stock = st.text_input("Favorite stock symbol (optional):")
        reasons = ["Access to stock analysis", "Network with investors", "Curiosity"]
        reasons_membership = st.selectbox("Reason for joining:", reasons)
        linkedin_profile =st.text_input("Linkedin Profile Link (optional):") 
        
        if st.button("Register"):
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, risk_preference, favorite_industries, reasons_membership, favorite_stock, linkedin_profile) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, hashed_password, risk_preference, favorite_industries, reasons_membership, favorite_stock, linkedin_profile)
            )
            conn.commit()
            st.write("You've successfully registered. To access your profile, the stock analysis tool, and the community, please go to the Log In page.")

##### Log In #####

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
                st.write("You've successfully logged in! You can now access the profile, stock analysis and community through the new menu on the left of your screen. We wish you a pleasant time investing and getting to know other investors.")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["current_page"] = Home
                return username
            else:
                st.write("Incorrect password.")
                return None


######################################## Logged In User Interface #########################################

############### Profile Page ###############

##### User Industry Preferences Overview Pie Chart #####

def pie_chart():
    st.subheader("Industry Interest Distribution")
    cursor.execute("SELECT favorite_industries FROM users")
    industries_data = cursor.fetchall()
    industries_list = [item[0] for item in industries_data] # Retrieve the industries from the database created before

    if industries_list:
        # Convert data to DataFrame
        df = pd.DataFrame(industries_list, columns=['Industry'])
        
        # Calculate the distribution of industries
        industry_counts = df['Industry'].value_counts()
    
        # Plot the pie chart
        fig, ax = plt.subplots(facecolor='none')
        ax.pie(industry_counts, labels=industry_counts.index, autopct='%1.1f%%', startangle=90)
        ax.set_facecolor('none')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
 
        st.pyplot(fig)
    else:
        st.write("Unfortunately, there isn't enough data available to display the chart for now. Once more users sign up to Smart Stocks, we will be able to create the chart.")


##### User's Profile Information View #####

def view_profile(username):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user:
        st.subheader(f"{username}'s Profile:")
        st.write(f"- Favorite Industry: {user[3]}")
        st.write(f"- Risk Preference: {user[2]}")
        st.write(f"- Membership Reason: {user[4]}")
        st.write(f"- Favorite Stock: {user[5]}")
        if user [6]: #If Linkedin link exists, display it
            st.write(f"- LinkedIn: [Link]({user[6]})")
    pie_chart()



############### Stock Analysis ###############


##### Yahoo Finance Data Retrieval and Analysis #####

def yahoof(stock_symbol):
    try: 
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
    except:
        st.write("Unfortunately, we could not find the information you're requesting on Yahoo Finance. Please enter another valid stock symbol.")


##### Stock price prediction model using a linear regression model (Machine Learning) #####

def predictions(stock_symbol):
    yahoo_stock = yf.Ticker(stock_symbol)
    period_options = ["1mo", "3mo", "6mo", "1y"]
    selected_period = st.selectbox("Select period for analysis:", period_options)
    data = yahoo_stock.history(period=selected_period)
    if data.empty:
        st.write("There is no data available for the selected period.")
        return
    data['DateOrdinal'] = data.index.map(pd.Timestamp.toordinal)
    X = data['DateOrdinal'].values.reshape(-1, 1)
    Y = data['Close'].values.reshape(-1, 1)
    linear_regressor = LinearRegression()
    linear_regressor.fit(X, Y)
    Y_pred = linear_regressor.predict(X)
    future_days = 30
    future_dates = pd.date_range(data.index[-1], periods=future_days + 1, freq='B')[1:]
    future_ordinals = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    future_pred = linear_regressor.predict(future_ordinals)

    plt.figure(figsize=(12, 6))
    plt.plot(data.index, Y, label="Actual Close Price", color="blue")
    plt.plot(data.index, Y_pred, label="Fitted Trend", linestyle="--", color="green")
    plt.plot(future_dates, future_pred, label="Future Predictions", linestyle="--", color="red")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.title(f"Stock Price Prediction for {stock_symbol} - {selected_period}")
    st.pyplot(plt)


##### Error handling for stocks unavailable in the database #####

def check(stock_symbol):
    if yf.Ticker(stock_symbol):
        yahoof(stock_symbol)
        predictions(stock_symbol)
    else:
        st.write("Unfortunately, we could not find the information you're requesting on Yahoo Finance. Please enter another valid stock symbol.")


##### Stock Analysis Page #####

def stock_analysis():
    st.subheader("Stock Analysis Tool")
    stock_symbol = st.text_input("Enter a valid stock symbol:")
    if stock_symbol:
        check(stock_symbol)

############### Community ###############

##### Set up for the chat interface #####

# Creation of a separate database for messages from chats between users
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

# Function that saves messages exchanged between users in the database
def save_message(sender, receiver, message):
    cursor.execute("""
        INSERT INTO messages (sender, receiver, message, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    """, (sender, receiver, message))
    conn.commit() #saves changes to database permanently

# Function that retrieves the chat history between two users
def get_chat_history(user1, user2):
    cursor.execute("""
        SELECT sender, message, timestamp 
        FROM messages 
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp ASC
    """, (user1, user2, user2, user1))
    return cursor.fetchall()


##### Finding similar users to display and chat with #####

def find_similar_users(username):
    """Find users with similar interests and risk preferences"""
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    current_user = cursor.fetchone()
    
    if current_user:
        cursor.execute("""
            SELECT username, risk_preference, favorite_industries, favorite_stock, linkedin_profile 
            FROM users 
            WHERE username != ? 
            AND (risk_preference = ? OR favorite_industries = ? OR favorite_stock = ?)
        """, (username, current_user[2], current_user[3], current_user[5]))
        
        similar_users = cursor.fetchall()
        return similar_users
    return []

##### Community Page (including chat interface) #####

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
                
                # Display LinkedIn link if available
                if user[4]:  
                    st.write(f"LinkedIn Profile: [Link]({user[4]})")
                
                # Chat interface
                if st.button(f"Chat with {user[0]}", key=f"chat_{user[0]}"):
                    st.session_state.chat_with = user[0]
    else:
        st.write("No similar users found yet.")

    ## Chat interface  ##
    if "chat_with" in st.session_state:
        st.subheader(f"Chat with {st.session_state.chat_with}")
        
        ## Display chat history  ##
        chat_history = get_chat_history(username, st.session_state.chat_with) or []
        for sender, message, timestamp in chat_history:
            if sender == username:
                st.write(f"You ({timestamp}): {message}")
            else:
                st.write(f"{sender} ({timestamp}): {message}")
        
        ## Message input  ##
        new_message = st.text_input("Type your message:", key="message_input")
        if st.button("Send"):
            if new_message.strip():
                save_message(username, st.session_state.chat_with, new_message)
            
    ## Initialization of the "chat_with" and "messsage_input" inputs to ensure they are not empty. Otherwise, there is a risk of a KeyError.  ##
    if "chat_with" not in st.session_state:
        st.session_state.chat_with = None

    if "message_input" not in st.session_state:
        st.session_state.message_input = ""



######################################## Menu and Page Navigations #########################################


############### Pre-login Menu ###############

def main_initial():
    st.title("Welcome to Smart Stocks!")
    menu = ["Who we are", "Register", "Login"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        register()
    elif choice == "Login":
        username = login()
        if username:
            main_after_login(username)
    elif choice == "Who we are":
        intro()


############### Post-login Menu ###############

def main_after_login(username):
    menu2 = ["Home", "Profile", "Stock Analysis", "Community", "Exit"]
    choice = st.sidebar.selectbox("Menu", menu2)

    if choice == "Home":      
        Home()
    elif choice == "Profile":
        st.title("Smart Stocks")  
        view_profile(username)
    elif choice == "Stock Analysis":
        st.title("Smart Stocks")  
        stock_analysis()
    elif choice == "Community":
        st.title("Smart Stocks")  
        community_page(username)
    else:
        st.session_state["logged_in"] = False
        st.write("You've logged out successfully. Come back anytime to explore the world of smart investments!")


######### Session state management to ensure logged in users see the logged in menu, and those that are not logged in do not see it. ######## 

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        main_after_login(st.session_state["username"])
    else:
        main_initial()
