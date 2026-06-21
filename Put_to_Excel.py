import re
import pandas as pd

file_path = "Total_Results.txt"

# Define a regular expression to match the patterns
pattern = re.compile(
    r"\*\*\*(?P<control_topology>\w+)_"
    #r"(?P<routing_method>\w+)_"
    r"(?P<packet_rate>\d+)_"
    r"(?P<packet_size>\d+)\*\*\*\n"
    r"Average Loss:\s*(?P<average_loss>[\d\.e+-]+)\n"
    r"Average Delay:\s*(?P<average_delay>[\d\.e+-]+)\n"
    r"Total Process Energy:\s*(?P<total_process_energy>[\d\.e+-]+)\n"
    r"Average Process time:\s*(?P<average_process_time>[\d\.e+-]+)\n"
    r"Total_Nodes:\s*(?P<total_nodes>[\d\.e+-]+)\n"
    r"Total Energy:\s*(?P<total_energy>[\d\.e+-]+)\n"
    r"Total Size:\s*(?P<total_size>[\d\.e+-]+)\n"
    r"Number of Dead Nodes:\s*(?P<number_dead_nodes>[\d\.e+-]+)\n"
    r"Lifetime:\s*(?P<lifetime>[\d\.e+-]+)"
)

# Read the file
with open(file_path, "r") as file:
    content = file.read()

# Extract matches
matches = list(pattern.finditer(content))

# Check if any matches were found
if not matches:
    print("No matches found. Please check the file content and format.")
else:
    print(f"Found {len(matches)} matches.")

# Create a list of dictionaries for each match
data = [
    {
        "Control Topology": match.group("control_topology"),
        #"Routing Method": match.group("routing_method"),
        "Packet Rate": int(match.group("packet_rate")),
        "Packet Size": int(match.group("packet_size")),
        "Average Loss": float(match.group("average_loss")),
        "Average Delay": float(match.group("average_delay")),
        "Total Process Energy": float(match.group("total_process_energy")),
        "Average Process Time": float(match.group("average_process_time")),
        "Total Nodes": int(match.group("total_nodes")),
        "Total Energy": float(match.group("total_energy")),
        "Total Size": float(match.group("total_size")),
        "Number of Dead Nodes": int(match.group("number_dead_nodes")),
        "Lifetime": float(match.group("lifetime")),
    }
    for match in matches
]

# Convert the data to a DataFrame
df = pd.DataFrame(data)
"""
# Save the DataFrame to an Excel file
output_file = "output.xlsx"
df.to_excel(output_file, index=False)

print(f"Data has been written to {output_file}")



import pandas as pd

# Load the Excel file
file_path =  "output.xlsx"  # Replace with your actual file path
df = pd.read_excel(file_path)
"""
# Make sure the columns are correctly named
print(df.columns)  # Print column names to verify

# Group by 'Packet Rate' and aggregate by the metrics
# List of metrics to summarize
metrics = ['Lifetime', 'Total Energy', 'Total Size','Total Nodes', 'Number of Dead Nodes', 'Average Loss', 'Average Delay', 
           'Total Process Energy', 'Average Process Time']

# Create separate files for each packet size with pivot tables
unique_packet_sizes = df["Packet Size"].unique()

for packet_size in unique_packet_sizes:
    subset = df[df["Packet Size"] == packet_size]
    output_file = f"output_packet_size_{packet_size}.xlsx"
    
    # Create pivot tables for the subset
    pivot_data = {}
    for metric in metrics:
        pivot_data[metric] = pd.pivot_table(
            subset, 
            values=metric, 
            index="Packet Rate", 
            columns="Control Topology", 
            aggfunc="mean", 
            fill_value=0
        )
    
    # Save data and pivot tables to Excel
    with pd.ExcelWriter(output_file) as writer:
        # Save raw data to the first sheet
        subset.to_excel(writer, index=False, sheet_name="Raw Data")
        # Save each pivot table to its own sheet
        for metric, pivot_table in pivot_data.items():
            pivot_table.to_excel(writer, sheet_name=f"Pivot_{metric}")
    
    print(f"Data and pivot tables for Packet Size {packet_size} have been written to {output_file}")


