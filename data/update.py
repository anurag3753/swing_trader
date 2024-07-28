import pandas as pd

# Load the CSV file
file_path = 'v200.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Ensure all values are treated as strings
df['old_list'] = df['old_list'].astype(str).str.strip().str.rstrip(',')
df['new_list'] = df['new_list'].astype(str).str.strip().str.rstrip(',')

# Create a dictionary for quick lookup
old_dict = dict(zip(df['old_list'], df['old']))

# Initialize lists for output
new_symbols = []
not_in_new_list = []

# Process new_list
for new_item in df['new_list']:
    if new_item in old_dict:
        new_symbols.append(old_dict[new_item])
    else:
        new_symbols.append('nan')

# Find items in old_list but not in new_list
for old_item in df['old_list']:
    if old_item not in df['new_list'].values:
        not_in_new_list.append(old_item)

# Write results to out.txt
with open('out.txt', 'w') as f:
    f.write("Symbols for new list:\n")
    for symbol in new_symbols:
        f.write(f"{symbol}\n")
    
    f.write("\nItems in old list but not in new list:\n")
    for item in not_in_new_list:
        f.write(f"{item}\n")

print("Comparison results have been written to out.txt.")
