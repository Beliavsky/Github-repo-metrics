import os
import sys
import shutil
import glob
import shutil
import re
import unicodedata

def copy_files(src_dir,dest_dir):
    """
    Copy all files from src_dir to dest_dir.
    """
    for root, dirs, files in os.walk(src_dir):
        for f in files:
            shutil.copy(os.path.join(root,f), dest_dir)

def files_in_dir(path,extension):
    """
    Return a list of files with the given extension in the specified directory.
    """
    os.chdir(path)
    result = [i for i in glob.glob('*.{}'.format(extension))]
    return result

def lines_in_f1_not_f2(f1,f2):
    """
    Return lines that are in f2 but not in f1.
    """
    s1 = open(f1,"r").readlines()
    s2 = open(f2,"r").readlines()
    lines = []
    for word in s2:
        if (word not in s1):
            lines.append(word)
    return lines
    
def truncated_string(original_string, sentinel):
    """ return original string up to the occurrence of sentinel """
    index = original_string.find(sentinel)
    if index != -1:
        truncated_string = original_string[:index]
        return truncated_string
    else:
        return original_string
def save_numbered_file(file_path):
    """
    Copy a file to an unused file name with a numbered suffix.
    Args:
        file_path (str): The path to the file to be copied.
    Returns:
        str: The path of the newly copied file.
    """
    base_dir = os.path.dirname(file_path)
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    new_file_path = file_path
    counter = 1
    while os.path.exists(new_file_path):
        new_file_name = f"{base_name}{counter}{ext}"
        new_file_path = os.path.join(base_dir, new_file_name)
        counter += 1
    shutil.copyfile(file_path, new_file_path)
    return new_file_path

def modify_lines(input_string, start_strings, append_char, ignore_case=False,
    ignore_spaces=False):
    """
    Modifies lines of a string that start with any string from a list.

    Args:
    input_string (str): The string to modify.
    start_strings (list of str): The list of strings to check if a line starts with.
    append_char (str): The character to append to matching lines. Defaults to '\n'.
    ignore_case (bool, optional): If True, ignores case when matching start strings. Defaults to False.
    ignore_spaces (bool, optional): If True, ignores leading spaces when matching start strings. Defaults to False.

    Returns:
    str: The modified string.
    """
    # Break the string into lines
    lines = input_string.split('\n')
    # Iterate over lines and append character if the line starts with any string from start_strings
    for i, line in enumerate(lines):
        # Remove leading spaces if ignore_spaces is True
        line_to_check = line.lstrip() if ignore_spaces else line
        # Convert to lower case if ignore_case is True
        line_to_check = line_to_check.lower() if ignore_case else line_to_check
        # Check if line starts with any string from start_strings, considering ignore_case option
        if any(line_to_check.startswith(start_str.lower() if ignore_case else start_str) for start_str in start_strings):
            lines[i] += append_char
    # Join modified lines back into a string
    output_string = '\n'.join(lines)
    return output_string

def replace_leading_spaces(file_path, nspaces=1, rep="", output_file=None):
    """
    Replace leading spaces in each line of a file.

    Parameters:
    file_path (str): The path to the file to be processed.
    nspaces (int): The number of leading spaces to remove from each line. Defaults to 1.
    rep (str): The string to replace the removed spaces with. Defaults to an empty string.
    output_file (str): The path to the output file. If None, the original file is overwritten.

    Notes:
    - Lines with between 1 and `nspaces-1` leading spaces will have those spaces replaced by `rep`.
    - Lines with `nspaces` or more leading spaces will have exactly `nspaces` spaces replaced by `rep`.
    - Lines with no leading spaces are left unchanged.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if output_file is None:
        output_file = file_path

    with open(output_file, 'w') as file:
        for line in lines:
            leading_spaces = len(line) - len(line.lstrip())
            if 1 <= leading_spaces < nspaces:
                # Replace between 1 and nspaces-1 leading spaces
                line = rep + line[leading_spaces:]
            elif leading_spaces >= nspaces:
                # Replace exactly nspaces leading spaces
                line = rep + line[nspaces:]
            file.write(line)

def powers(n, primes=[2, 3, 5]):
    """
    Partially factors an integer n into powers of the given primes.
    
    Args:
        n (int): The integer to factorize.
        primes (list): A list of primes to use for factorization (default: [2, 3, 5]).
    
    Returns:
        tuple: A dictionary with the prime factors and their exponents, and the remaining factor.
    """
    factors = {}
    remaining = n
    for p in primes:
        count = 0
        while remaining % p == 0:
            remaining //= p
            count += 1
        if count > 0:
            factors[p] = count    
    return factors, remaining

def print_vec(vec, fmt, label=None, end=None):
    """ print elements of a list with format fmt """
    if label is not None:
        print(label, end="")
    print("".join(fmt%x for x in vec))
    if end is not None:
        print(end=end)

def squeeze(text,lower=True,old_char=[" ","+","-","%","/"],new_char="_",remove_char=["&",",",".","'",'"',"(",")",":",";","?"]):
    # replace some characters with a new character, delete other
    # characters, and convert text to lower case if lower == True
    yy = " ".join(text.split())
    if lower:
        yy = yy.lower()
    for char in old_char:
        yy = yy.replace(char,new_char)
    for char in remove_char:
        yy = yy.replace(char,"")
    return yy

def truncate_lines_at_sentinel(input_file, output_file, sentinel):
    """
    Truncates each line of a text file before the first occurrence of '('.
    Saves the result in a new file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output text file.
    """
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Split line at '(' and take the part before it
            truncated_line = line.split(sentinel)[0].strip()
            outfile.write(truncated_line + '\n')

def expand_ranges(input_file, output_file):
    """
    Replaces lines with ranges (indicated by en dash '–') with a comma-separated list of integers.
    Normalizes text to handle inconsistent encodings and opens files with UTF-8 encoding.
    Preserves leading zeros in the numbers.
    
    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output text file.
    """
    range_pattern = re.compile(r"(\d+)\u2013(\d+)")  # Regex for range with en dash

    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Normalize the line to ensure proper Unicode representation
            line = unicodedata.normalize('NFC', line.strip())
            match = range_pattern.search(line)
            if match:
                # Extract start and end of the range, preserving leading zeros
                start, end = match.groups()
                width = len(start)  # Calculate the width of the numbers
                start, end = int(start), int(end)
                expanded_line = ', '.join(f"{num:0{width}d}" for num in range(start, end + 1))
                outfile.write(expanded_line + '\n')
            else:
                # Write the line as is if no range is found
                outfile.write(line + '\n')

def process_csv_to_lines(input_file, output_file):
    """
    Reads a CSV file where each line may contain multiple comma-separated values.
    Writes one value per line to an output file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output text file.
    """
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Split the line by commas, strip whitespace, and write each value on a new line
            values = line.strip().split(',')
            for value in values:
                outfile.write(value.strip() + '\n')

def matching_key_of_tuples_dict(x, data):
    """Return the key of the dictionary if x is in one of its tuple values,
    else None."""
    for key, values in data.items():
        if x in values:
            return key
    return None

def index(xlist, value):
    """ return the position of value in xlist, -1 if not found """
    if value in xlist:
        return xlist.index(value)
    else:
        return -1

def replace_strings_in_file(filename, replacements):
    """
    Reads a file, performs string replacements from a dictionary, and writes to stdout.
    
    Args:
        filename (str): Path to the input file
        replacements (dict): Dictionary with keys as strings to find and values as replacements
    
    Returns:
        None: Outputs directly to stdout
    
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        IOError: If there's an error reading the file
    """
    try:
        # Open and read the file
        with open(filename, 'r') as file:
            content = file.read()
        
        # Perform all replacements
        modified_content = content
        for old_string, new_string in replacements.items():
            modified_content = modified_content.replace(old_string, new_string)
        
        # Write to standard output
        sys.stdout.write(modified_content)
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)

def sort_dict_by_value_length(input_dict):
    """
    Sort a dictionary by the length of its values in descending order, breaking ties alphabetically.
    Scalars or non-iterable values are treated as having length -1 and placed at the end.
    
    Args:
        input_dict (dict): Dictionary with values that may be lists, tuples, or scalars
    
    Returns:
        dict: Sorted dictionary
    """
    def get_length(val):
        # Return length if list or tuple, -1 otherwise
        if isinstance(val, (list, tuple)):
            return len(val)
        return -1
    # Sort by length (descending) and key (ascending) as a tiebreaker
    sorted_items = sorted(
        input_dict.items(),
        key=lambda x: (-get_length(x[1]), x[0])  # Negative length for descending order
    )    
    # Convert back to dictionary
    return dict(sorted_items)
