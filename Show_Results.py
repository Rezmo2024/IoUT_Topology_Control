import matplotlib.pyplot as plt
import os
import random

# Function to extract data from the log file
def extract_data(fname,label):
    data = fetch_data(fname)
    plot_png_txt(data,label)
def fetch_data(file_path):
    data = {}
    method_names = set()
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if '***' in line:
            current_method = line.strip('*\n')
            method_names.add(current_method)
    with open(file_path, 'r') as file:
        lines = file.readlines()            
    current_method = None
    for line in lines:
        if '***' in line:
            current_method = line.strip('*\n')
        else:
            try:
                variable, value = line.strip().split(':')
                if variable not in data:
                    data[variable] = {method: [] for method in method_names}
                data[variable][current_method].append(float(value))
            except ValueError:
                # Ignore lines that don't have the expected format
                pass
    return data

def reverse_key(key):
    return key[::-1]
def prepare_data(data):
    # Extract the unique first parts of the key names
    key_parts = set()
    for key in data.keys():
        for sub_key in data[key].keys():
            key_part = sub_key.split('_')[0]
            key_parts.add(key_part)
    #sort dictionary
    sorted_data = {}
    for key, value in data.items():
        sorted_data[key] = dict(sorted(value.items(), key=lambda x: reverse_key(x[0])))    # Plotting each key in the dictionary as a separate plot
    data=sorted_data
    colors = ['#%06X' % random.randint(0, 0xFFFFFF) for _ in range(len(key_parts))]
    key_parts=list(key_parts)
    cl={}
    for key, values in data.items():
        x = list(values.keys())
        for it2 in x:
            for it in key_parts:
                if it in it2:
                    cl[it]=colors[key_parts.index(it)]   
    return data,cl,len(key_parts)

# Function to create a bar chart for each variable
def plot_png_txt(datadic,label):
    data,cl,nn=prepare_data(datadic)
    ncolors=list(cl.values())
    ncolors.append('#FFFF')#for distance between groups
    for key, values in data.items():
        plt.figure(figsize=(20, 8))
        x = list(values.keys())
        y = [val[0] for val in values.values()]
        j=nn
        while j<len(y):
            x.insert(j," "+str(j))#for distance between groups
            y.insert(j,0)#for distance between groups
            j+=nn+1
        plt.bar(x, y,color=ncolors)
        plt.xlabel('Methods')
        plt.ylabel(key)
        plt.title(f'Plot for {key}')
        plt.xticks(rotation=90)
        plt.tight_layout()
        # Save the plot as a PNG file
        current_dir = os.getcwd()
        plot_file = os.path.join(current_dir+"\\ResultsFigs", f"{key.replace(' ', '_')}"+label+".png")
        plt.savefig(plot_file)
        print(f"Plot saved: {plot_file}")
    # Save the values of each key in a separate text file
    for key, values in data.items():
        file_name = f"{key.replace(' ', '_')}"+label+".txt"
        file_path = os.path.join(current_dir+"\\ResultsText", file_name)
        with open(file_path, 'w') as file:
            for method, value in values.items():
                file.write(f"{method} {value[0]}\n")
        print(f"File saved: {file_path}")


if __name__ == "__main__":
    extract_data("Total_Results.txt","salam")