import asyncio
from contextlib import asynccontextmanager
import json
import os, csv
from random import choice
import sys
import traceback
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import re
from bs4 import BeautifulSoup
import time
import requests
try:
    import httpx
    from selectolax.parser import HTMLParser
    from pydash import get as _
    from loguru import logger
    import pendulum
except:
    print("Installing dependencies...")
    os.system("pip install -U httpx pydash selectolax loguru pendulum")
    import httpx
    from selectolax.parser import HTMLParser
    from pydash import get as _
    from loguru import logger
    import pendulum

    

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
]

scraped_urls = set()
authorkey = ""
chapterNo = ""
verseNo = ""










def get_date(offset):
    now = pendulum.now()
    if offset:
        now = now.add(days=offset)

    return now.format('D MMMM', locale='pt_br').upper()


def scrape_detail(authorkey,chapterNo, verse_number):
    
    
    searchStr = "https://www.bibliaonline.com.br/acf/{}/{}".format(authorkey,chapterNo)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    response = requests.get(searchStr, headers=headers)
    time.sleep(0.2)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    print(searchStr)
    
    # Find the verse number
    # Specify the verse number you want to find

    # Find the corresponding <p> tag with the given verse number
    verse_element = soup.find('p', {'data-v': f'.{verse_number}.'})

    verse_text =""
    # Extract the text of the verse
    if verse_element:
        verse_text = verse_element.get_text(strip=True)
        print(verse_text)
    else:
        print(f"Verse {verse_number} not found.")

    return verse_text






    
def run_script():
    output = "VERSICULOS_CAFE_COM_FE.txt"
    authors = versiculos_entry.get("1.0", "end-1c")
    day_offset = int(dia_var.get().split("_")[0][1:])  # Removes the first character '{'
    asyncio.run(main(output, authors, day_offset))
    convert_txt_to_json()  # Add this line here to call the second script after your first script

def reset_window():
    versiculos_entry.delete("1.0", "end")

def validate_inputr():
    selected_value = int(dia_var.get().split(' ')[-1])
    print(selected_value)
    return selected_value

def process_entry(entry):
    try:
        print(entry)

        # Splitting the entry by space to separate book name and chapter:verse number
        parts = entry.strip().split(' ')
        if len(parts) >= 2:
            book_name = parts[0].strip()
            chapter_verse = parts[1].strip().split(':')
            if len(chapter_verse) >= 2:
                chapter_number = int(chapter_verse[0].strip())
                verse_number = int(chapter_verse[1].strip())
                
                value_variable = ""

                for item in data:
                    key = list(item.keys())[0]  # Extract the key from the dictionary
                    value = item[key]  # Extract the value from the dictionary
                    if key == book_name:
                        value_variable = value
                        break

                verse = scrape_detail(value_variable,chapter_number, verse_number)
                selected_val = validate_inputr() 
                date = get_date(selected_val)
                print(date)
                verse_dict = {}
                verse_dict['Date'] = date
                verse_dict['Citation'] = verse
                verse_dict['Chapter'] = entry
                return verse_dict
            else:
                print("Invalid input format. Expected format: book chapter:verse")
        else:
            print("Invalid input format. Expected format: book chapter:verse")
    except:
        print("something fishy")
        verse_dict ={}
        return verse_dict
        
    # Call your function with the extracted values
    #your_function(book_name, chapter_number, verse_number)


# Create a new function to validate input:
def validate_input():
    authors = versiculos_entry.get("1.0", "end-1c")
    print (authors)
    # Validate authors:
    if not authors.strip():
        messagebox.showerror("Input Error", "Versiculos input cannot be empty.")
        return

    entries = authors.split(',')

    # Iterate through the entries
    with open("VERSICULOS_CAFE_COM_FE_NEW.json", "r",encoding='utf-8') as file:
        entry_list = json.load(file)

    # Process each entry and append the results to entry_list
    for entry in entries:
        verse_dict = process_entry(entry)
        print(verse_dict)
        entry_list.append(verse_dict)

    # Save the updated entry_list back to the JSON file
    with open("VERSICULOS_CAFE_COM_FE_NEW.json", "w",encoding='utf-8') as file:
        json.dump(entry_list, file, indent=4, ensure_ascii=False)



    

    

# Create a GUI:
root = tk.Tk()
root.title("Biblia Unifé TV")
data = []
with open('AbreviaturasURL.txt', 'r' , encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line:
            key, value = line.split(' - ')
            data.append({key: value})

print(data)

# Create a label and text box for Versiculos:
tk.Label(root, text="Versiculos:").pack()
versiculos_entry = tk.Text(root, height=7, width=75)
versiculos_entry.insert("1.0", "Versiculos")
versiculos_entry.pack()

# Create a label and dropdown for Dia:
tk.Label(root, text="Dia:").pack()
dia_var = tk.StringVar()
dia_dropdown = ttk.Combobox(root, textvariable=dia_var)  # Create a dropdown
dia_dropdown['values'] = [("00_Hoje", 0),
                          ("01_Amanhã", 1),
                          ("02_Depois de Amanhã", 2),
                          ("03_Dia 4", 3),
                          ("04_Dia 5", 4),
                          ("05_Dia 6", 5),
                          ("06_Dia 7", 6),
                          ("07_Dia 8", 7),
                          ("08_Dia 9", 8),
                          ("09_Dia 10", 9)]
dia_dropdown.current(0)  # Set the default option to the first one
dia_dropdown.pack()


# Create a button to run the script:
tk.Button(root, text="Run Script", command=validate_input).pack()
#selected_value = dia_var.get()
#print(selected_value)
#selected_value = selected_value.split(' ')[-1]

#print(selected_value)
#selected_value = int(selected_value)


#comentAuthorScript
tk.Label(root, text="Feito por: Dinu Granaci").pack()
tk.Label(root, text="Contacto: dinu_granaci@hotmail.com").pack()

# Run the GUI:
root.mainloop()
