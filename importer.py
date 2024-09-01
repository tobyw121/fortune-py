import sqlite3
import argparse


### python your_script_name.py -f fortunes.txt -l de  # Import German fortunes
### python your_script_name.py -f fortunes.txt        # Import English fortunes (default)

def import_fortunes_from_file(filename, language):
    """Imports fortunes from a text file into the database."""

    conn = sqlite3.connect('sprueche.db')
    cursor = conn.cursor()

    with open(filename, 'r', encoding='utf-8') as file:
        fortunes = file.read().split('%')

    for fortune in fortunes:
        fortune = fortune.strip()
        if fortune:
            cursor.execute('INSERT INTO fortunes (language, text) VALUES (?, ?)', (language, fortune))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import fortunes into the database.")
    parser.add_argument("-f", "--file", required=True, help="The text file containing the fortunes.")
    parser.add_argument("-l", "--language", choices=["en", "de"], default="en", 
                        help="Language of the fortunes (en for English, de for German). Defaults to English.")

    args = parser.parse_args()

    language_map = {"en": "Englisch", "de": "Deutsch"}  # Map short commands to full language names
    full_language = language_map[args.language]

    import_fortunes_from_file(args.file, full_language)
    print("Fortunes imported successfully!")
