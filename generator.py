# Script to convert encodings from HTML to CSV

# Import the csv module
import csv

# Open the text file for reading
with open("market_source.txt", "r") as text_file:
  # Open the csv file for writing
  with open("market_source.csv", "w", newline='') as csv_file:
    # Create a csv writer object
    csv_writer = csv.writer(csv_file)
    # Loop through each line in the text file
    for line in text_file:
      # Strip the whitespace and newline characters from the line
      line = line.strip()
      # Check if the line contains an option tag
      if "<option" in line and "</option>" in line:
        # Split the line by the ">" character and get the second part
        value_text = line.split(">")[1]
        # Split the value_text by the "<" character and get the first part
        text = value_text.split("<")[0]
        # Check if the text is not "--Select--"
        if text != "--Select--":
          # Split the line by the "=" character and get the second part
          value_quote = line.split("=")[1]
          # Split the value_quote by the ">" character and get the first part
          quote = value_quote.split(">")[0]
          # Remove the quotation marks from the quote
          value = quote.replace('"', '')
          # Write the value and text to the csv file as a row
          csv_writer.writerow([text, value])