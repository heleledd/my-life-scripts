import re
import logging
import argparse
import json

def remove_h_strings(input_text, regex_pattern):
    # Use re.sub to replace matches with an empty string
    result = re.sub(regex_pattern, "", input_text)
    return result

# Example usage
text = "This is a test {H1234} string with {Habcd} multiple {H5678} matches."
cleaned_text = remove_h_strings(text)
print("Original text:", text)
print("Cleaned text:", cleaned_text)

def main(text):
    regex_pattern = r"\{H.{4}\}"
    
    # clean the text by removing strings like {H....}
    cleaned_text = remove_h_strings(text, regex_pattern)
    
    
    

if __name__ == "__main__":
    # set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(asctime)s - %(message)s'
    )
    
    # set arguments
    parser = argparse.ArgumentParser(description="Remove {H....} strings from text.")
    parser.add_argument("input_file", help="Path to the input file containing text.")
    args = parser.parse_args()
    
    # read the input file
    