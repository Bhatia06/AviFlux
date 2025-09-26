import pandas as pd

# The same URL for the comprehensive dataset
AIRPORTS_CSV_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"

# Load the entire dataset without any filters first
print("Loading the full dataset for inspection...")
df = pd.read_csv(AIRPORTS_CSV_URL)

# --- Verification Step 1: See all unique airport types ---
print("\nUnique values in the 'type' column:")
print(df['type'].unique())

# --- Verification Step 2: Count how many of each type exist ---
print("\nCounts for each airport type:")
print(df['type'].value_counts())

# --- Verification Step 3: Find a specific large airport (Bengaluru) ---
print("\nSearching for Bengaluru's Kempegowda International Airport (VOBL)...")
bengaluru_airport = df[df['ident'] == 'VIDP']
print(bengaluru_airport[['ident', 'name', 'type']])