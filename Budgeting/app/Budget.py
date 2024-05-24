import pandas as pd
import os
from sklearn.metrics import classification_report
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import plotly.express as px
from datetime import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import webbrowser
from threading import Timer

def initialize_savings_variables():
    print("Current Working Directory:", os.getcwd())
    savings = pd.read_csv("app\savings.csv")
    try:
        savings["Date"] = pd.to_datetime(savings["Date"], format="%Y-%m-%d")
    except:
        savings["Date"] = pd.to_datetime(savings["Date"], format="%d/%m/%Y")
    # Today's date
    today = datetime.now().date()

    vanguard = input("Vanguard Investments: ")
    if vanguard == "":
        vanguard = savings.loc[savings['Date'].idxmax()]["Vanguard"]
    fineco_snp = input("Fineco Investments: ")
    if fineco_snp == "":
        fineco_snp = savings.loc[savings['Date'].idxmax()]["Fineco"]
    crypto = input("Crypto Investments: ")
    if crypto == "":
        crypto = savings.loc[savings['Date'].idxmax()]["Crypto"]
    revolut = input("Revolut Total: ")
    if revolut == "":
        revolut = savings.loc[savings['Date'].idxmax()]["Revolut"]

    # New row with today's date and specific values for other columns
    new_row = pd.DataFrame({
        'Date': [pd.to_datetime(today)],
        'Vanguard': [vanguard],
        'Fineco': [fineco_snp],
        "Crypto":[crypto],
        "Revolut":[revolut]
    })

    savings = pd.concat([savings, new_row], ignore_index=True).drop_duplicates()
    savings.to_csv("app\savings.csv", index=False)
    return vanguard, fineco_snp, revolut, crypto, savings

def open_statements(bank):
    
    path = 'Statements/'
    files = os.listdir(path+bank)
    df_lst = []
                       
    for csv in files:
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(path+f"{bank}/"+csv, header=None, encoding=encoding)
                print(f"Successfully read with {encoding}")
                break
            except UnicodeDecodeError:
                print(f"Failed to decode with {encoding}")

        df = group_df(df, bank)

        df_lst.append(df)
    
    concatenated_df = pd.concat(df_lst, ignore_index=True)
    concatenated_df = concatenated_df.drop_duplicates()

    return concatenated_df

def measure_inits(vanguard, fineco_snp, revolut, revolut_crypto):
    hsbc_init = 220
    fineco_init = 1230
    initial = hsbc_init + fineco_init
    add_ons = vanguard+revolut+revolut_crypto
    total_portfolio = fineco_snp+vanguard+revolut_crypto
    return initial, add_ons, total_portfolio

def group_df(df, bank):
    if bank == "hsbc":
        df.columns = ["Date", "Payee", "Total"]
        df["Total"] = df["Total"].apply(lambda x: str(x).replace(",", "") if isinstance(x, str) else x)
        df["Total"] = df["Total"].astype("float64")
        df["Type"] = [x.split(" ")[-1] for x in df["Payee"] if type(x) == str] 
        hsbc_df = df.groupby(by=["Date", "Type", "Payee"], as_index=False).sum()
        hsbc_df["Bank"] = "HSBC"
        return hsbc_df
    elif bank == "fineco":
        fineco_df = df[~df[df.columns[1]].isna() | ~ df[df.columns[2]].isna()]
        fineco_df.columns = ["Date", "IN", "OUT", "Type", "Payee", "NA1", "NA2"]
        fineco_df = fineco_df[fineco_df["Date"] != "Data"]
        
        fineco_df["Total"] = fineco_df["IN"].fillna(fineco_df["OUT"]).astype("float64")
        fineco_df = fineco_df[["Date", "Payee", "Total", "Type"]]
        fineco_df = fineco_df.groupby(by=["Date", "Type", "Payee"], as_index=False).sum()
        fineco_df["Bank"] = "Fineco"
        #convert to pounds
        fineco_df["Total"] = fineco_df["Total"] * 0.85
        return fineco_df

def transform_statements(hsbc_df, fineco_df):
    
    tot = pd.concat([hsbc_df, fineco_df], ignore_index=True)
    
    tot["Total"] = tot["Total"].apply(lambda x: str(x).replace(",", "") if isinstance(x, str) else x)
    tot["Total"] = tot["Total"].astype("float64")

    tot["Date"] = pd.to_datetime(tot["Date"], format="%d/%m/%Y")
    
    tot['Year'] = pd.DatetimeIndex(tot['Date']).year.astype(str)
    tot['Month'] = pd.DatetimeIndex(tot['Date']).month.astype(str).str.zfill(2)
    tot["Day"] = pd.DatetimeIndex(tot['Date']).day.astype(str)
    
    tot['Year-Month'] = tot["Year"] + '-' + tot["Month"]
    tot['Year-Month-Day'] = tot["Year"] + '-' + tot["Month"] + "-" + tot["Day"]

    return tot


def reset_types(df):
    
    replace_types = {
    "Visa" : ["Pagamento Visa Debit", "VIS", ")))", "Utilizzo carta di credito"],
    "Bank Transfer" : ["CR", "Bonifico SEPA Italia", 'Accr.su carta FinecoCard Debit', "BP","Bonifico Istantaneo", "Comm. Bonifico Istantaneo", "OBP"],
    "ATM" : ["ATM", "Comm.Prel.FinecoCard Debit ATM", "Pr.FinecoCard ATM extra Gruppo", "Comm.Prel.FinecoCard Debit ATM"],
    "Dividends" : ["Dividendo Italia","Sconto Canone Mensile"],
    "Bank Fees" : ["Imposta bollo dossier titoli", "Spese Riemissione Bancomat","Riten.DIVIDENDI ETF armoniz.", "DR", "CHG", "Canone Mensile Conto"],
    "Direct Debit" : ["DD", "SEPA Direct Debit"] 
    }

    reverse_mapping = {old_value: new_value for new_value, old_values in replace_types.items() for old_value in old_values}
    
    df["Type"].replace(reverse_mapping, inplace=True)
    
    return df


def get_group(row):
    
    map_payees = {
    "Bills & Subscriptions" : ["H3G DD", "Thames Water", "Council", "Resumegenius","Virgin Media", "bill", "ESTRATTO CONTO", "iliad", "rekordbox"],
    "Transport" : ["TFL", "WizzAir", "Cadorna", "Bus", "Train", "Treno", "Uber", "Bike", 
                   "Human Forest", "Malpensa", "Freenow", "Railcard", "LUL ", "Bolt",
                  "Ryanair", "Dott Pass", "LIME", "Voi", "MXP", "Wizz Air"],
    "Going Out / Food Out" : ["Blues", "Kitchen", "Cinema", "Comedy", "Wetherspoon", 
                              "Bar", "Restaurant", "Cafe", "Coffee", "Caffe", "Five Guys", 
                              "Shakeshuka", "Deliveroo", "Zettle", "Thai", "Vietnam", "Arms", 
                              "Mcdonald", "Patty", "Bun", "Wok to Walk", "Starbucks", "Top Secret", 
                              "Escape Room", "Taste", "Keba", "Wasabi", "Thorpe Park", "The Duke Of",
                             "Nandos", "Fun", "Horse", "Ticketmaster", "ticketswap", "dice", " Tap ",
                            "Rum ", "Vodka", "Gin ", "Kebab", "Gelat", "Drayton", "Alton", "Legoland",
                              "Netil 360", "Five Points", "KFC", "Tabacch", "Sushi", "Catering", "Cheese", 
                              "Dalston Roof", "Pret ", "Stories", "Dirty ", "Resident Advisor", "Crown and",
                              "French's", "Mercato Metro", "BB&K", "King's", "Shawa", "Fresko", "Bermondsey Arts",
                              "Woolpack", "Elephant and castle london gb", "Tavern", "Com Amor", "Film", "Archives",
                              "Ice wharf", "Leisure", "Chop", "Gosnell", "Drumsheds", "Arabica", "GBK", "Arabica",
                              "Village Under", "Boom:", "Simple health", "Beigel", "wahaca", "Slice", "E1", "Beer"
                             ],
    "Shopping" : ["Zara", "Vinted", "Uniqlo", "H & m", "Natural East", "Amazon", "Totally Wicked", "Mail", "Mall", "Shop", "ebay"],
    "Salary" : ["Merlin"],
    "Dad" : ["ANTONELLI PIER"],
    "Mom" : ["Tondelli"],
    "Sports, Hobbies & Lifestyle" : ["VAUXWALL", "New Beda Bazar", "Climbing", "Climb", "gym", "Playstation", "Cutters Yard", "Barber", "Wall", "Grooming"],
    "Groceries" : ["Sainsbury", "Tesco", "CO-OP","Food", "WH Smith", "NISA Local", "Marks&spencer", "News", "Aldi", 
                   "Lidl", "Waitrose", "Select and Save", "Supermar", "Mini M", "Market", "Morrison", "Wine"],
    "Accommodation" : ["Airbnb", "Hostel", "Booking.com", "Hotel"],
    "Savings" : ["Vanguard", "Plum"],
    "Other" : ["Metropolitan", "Selecta", "NYX", "Sumup", "Enterprises" "Youngs", "Madame", "Darwen","Mind","doghouse", 
               "ramona", "teg mjr", "la fama", "brondes age", "MOTO DONNINGTON", "Freemount", "Jacks", "Harry", "Kara",
              "Pommeler", "Enterprises", "Revolut", "Sergio Antonelli"]
    
    }
    payee = row['Payee']
    payee_groups = [key for key, values in map_payees.items() if any(val.lower() in payee.lower() for val in values)]
    payee_group = ', '.join(payee_groups) if payee_groups else None

    # Apply additional logic based on the "Type" column
    if row['Type'] == "Direct Debit":
        if payee_group not in ["Savings"]:
            return "Bills & Subscriptions"
    elif row['Type'] == "Bank Transfer":
        if "Sergio Antonelli" in row["Payee"] and "Savings" not in payee_groups:
            return "Other"
        elif row['Total'] < -750:
            return "Accommodation"
        elif row["Total"] < 0:
            return "Friends OUT"
        elif row["Total"] > 0:
            if "Salary" not in payee_groups and "Savings" not in payee_groups and "Dad" not in payee_groups and "Mom" not in payee_groups:
                return "Friends IN"
    elif row['Type'] == "ATM":
        return "Cash"
    elif row['Type'] == "Dividends":
        return "Salary"
    elif row['Type'] == "Bank Fees":
        return "Bills & Subscriptions"
    
    if payee_group == None:
        return "Unclassified"
    
    if "," in payee_group:
        if "Going Out" in payee_group and row["Type"] == "Visa":
            return "Going Out / Food Out"
        else:
            return [x for x in payee_groups if x != "Going Out / Food Out"][0]

    return payee_group


def current_total(df, add_ons):
    amount = add_ons+df["Total"].sum()
    return amount


def split_statement(df):
    # Apply the function to the DataFrame
    df['Group'] = df.apply(get_group, axis=1)
    df = df[~df["Group"].isin(["Savings"])]
    
    expenses = df[df["Total"] <0]
    expenses["Total"] = abs(expenses["Total"])
    income = df[df["Total"] >0]
    
    return expenses, income

def monthly_split(df, time_period = "Year-Month"):
    return df.groupby(by=[time_period, "Group"])["Total"].sum().reset_index()

def savings_visualized(df):
    df = df.drop('Revolut', axis=1)
    df["Total"] = df.drop('Date', axis=1).sum(axis=1)
    df = df.melt(id_vars=["Date"], var_name = "Asset")
    # Create the line graph using Plotly
    fig = px.line(
        df,
        x='Date',
        y='value',
        color = "Asset",
        title='Cumulative savings over time',
        labels={'Date': 'Date', 'Total': 'Total Savings'},
        markers=True
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Savings",
        hovermode="x unified"
    )

    # Show the plot
    return fig


def visualize_expenses(df):
    
    fig = px.bar(
        df,
        x='Year-Month',
        y='Total',
        color='Group',
        title='Montly Expenses Split By Group',
        labels={'Year-Month': 'Month', 'Total': 'Total Amount'},
        barmode='stack',
        height=600
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Amount",
        legend_title="Group",
        xaxis_tickangle=-45,
        hovermode="x unified"
    )

    # Show the plot
    return fig


def visualize_income(df):
    fig = px.bar(
        df,
        x='Year-Month',
        y='Total',
        color='Group',
        title='Montly Income By Group',
        labels={'Year-Month': 'Month', 'Total': 'Total Amount'},
        barmode='stack',
        height=600
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Amount",
        legend_title="Group",
        xaxis_tickangle=-45,
        hovermode="x unified"
    )

    # Show the plot
    return fig


def avg_monthly_movements(df):
    monthly = df.groupby(by="Year-Month").sum(numeric_only=True)
    monthly_total = monthly["Total"].mean()
    return monthly_total



def predict_unclassified_groups(df):
    
    testing_set = df[df["Group"] != "Unclassified"]
    prediction_set = df[df["Group"] == "Unclassified"]
    
    if prediction_set.empty:
        print("Dataframe Already Complete")
        return df
    
    preprocessor = ColumnTransformer(
    transformers=[
        ('desc', TfidfVectorizer(), 'Payee'),
        ('bank', OneHotEncoder(), ['Bank']),
        ('trans_type', OneHotEncoder(), ['Type']),
        ('date', StandardScaler(), ['Day', 'Month', 'Year'])
        ])

    # Define the pipeline with the preprocessor and Random Forest classifier
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Split the data into training and testing sets
    X = testing_set.drop(columns=['Group'])
    y = testing_set['Group']
    X_pred = prediction_set.drop(columns="Group")
    
    pipeline.fit(X, y)
    
    y_pred = pipeline.predict(X_pred)
    
    prediction_set.loc[:, 'Group'] = y_pred
    
    return pd.concat([testing_set, prediction_set], ignore_index=True)

def visualize_cumulative_spend(df, initial):
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    # Aggregate the data to get the total amount for each day
    daily_totals = df.groupby('Date')['Total'].sum().reset_index()

    # Sort the DataFrame by the 'Date' column
    daily_totals = daily_totals.sort_values(by='Date')
    daily_totals['Cumulative Total'] = daily_totals['Total'].cumsum() + initial
    
    # Create the line graph using Plotly
    fig = px.line(
        daily_totals,
        x='Date',
        y='Cumulative Total',
        title='Cumulative Total Spend Over Time (Daily)',
        labels={'Date': 'Date', 'Cumulative Total': 'Cumulative Total Spend'},
        markers=True
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative Total Spend",
        hovermode="x unified"
    )

    # Show the plot
    return fig

def spent_this_month(df):
    curr = str(datetime.today().year) + "-" + str(datetime.today().month).zfill(2)
    current_spent_month = df[df["Year-Month"] == curr]
    current_spent_month = current_spent_month[~current_spent_month["Group"].isin(["Savings", "Myself", "Accommodation"])]
    return current_spent_month["Total"].sum()

def create_app(monthly_spend, monthly_income, cumulative_spend, str1, str2, str3, str4, savings_fig):
    app = dash.Dash(__name__)

    # Define the layout of the dashboard
    app.layout = html.Div(children=[
        html.H1(children='Finances'),

        html.Div(children='''
            Quick picture of recent and current finances.
        '''),

        dcc.Graph(
            id='spent_monthly',
            figure=monthly_spend
        ),

        dcc.Graph(
            id='gained_monthly',
            figure=monthly_income
        ),

        dcc.Graph(
            id='cumulative_spend',
            figure=cumulative_spend
        ),
        
        dcc.Graph(
            id='cumulative_savings',
            figure=savings_fig
        ),

        html.Div(children=[
            html.P(str1),
            html.P(str2),
            html.P(str3),
            html.P(str4)
        ])
    ])

    return app

def run_full_pipeline():
    Vanguard, Fineco_snp, Revolut, Revolut_crypto, savings = initialize_savings_variables()
    initial, add_ons, total_portfolio = measure_inits(Vanguard, Fineco_snp, Revolut, Revolut_crypto)
    hsbc = open_statements("hsbc")
    fineco = open_statements("fineco")
    statements = transform_statements(hsbc_df=hsbc, fineco_df=fineco)
    statements = reset_types(statements)

    expenses, income = split_statement(statements)
    expenses = predict_unclassified_groups(expenses)
    income = predict_unclassified_groups(income)
    agg_expenses = monthly_split(expenses)
    agg_income = monthly_split(income)
    OUT = avg_monthly_movements(expenses)
    IN = avg_monthly_movements(income)

    monthly_spend = visualize_expenses(agg_expenses)
    monthly_income = visualize_income(agg_income)
    cumulative_spend = visualize_cumulative_spend(statements, initial)
    savings_fig = savings_visualized(savings)
    spent = spent_this_month(expenses)
    str1 = "Average monthly spend is " + str(round(OUT)) + "£, Average monthly income is " + str(round(IN)) +  "£"
    str2 = str(round(spent)) + "£ Spent This Month (no savings, revolut or accommodation)"
    str3 = "Current total is " + str(round(current_total(statements, add_ons+initial))) + "£"
    str4 = "Current Portfolio is " + str(round(total_portfolio)) + "£"
    app = create_app(monthly_spend, monthly_income, cumulative_spend, str1, str2, str3, str4, savings_fig)
    return app
