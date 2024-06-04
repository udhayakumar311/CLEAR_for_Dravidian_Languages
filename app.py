from flask import Flask, render_template, request, jsonify, render_template_string
import re
import string
import Indices_Calculation
from indicnlp import common, loader, syllable
import datetime
import sqlite3
import os



# app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')


def analyze_tamil_text(text):
    # The path to the local git repo for Indic NLP library
    INDIC_NLP_LIB_HOME=r"C:\Users\Udhaya\indic_nlp_library"
    
    # The path to the local git repo for Indic NLP Resources
    INDIC_NLP_RESOURCES=r"C:\Users\Udhaya\indic_nlp_resources-master"
    
    import sys
    sys.path.append(r'{}'.format(INDIC_NLP_LIB_HOME))
    
    from indicnlp import common
    common.set_resources_path(INDIC_NLP_RESOURCES)
    
    from indicnlp import loader
    loader.load()
    
    from indicnlp.syllable import syllabifier

    # Declare global variables without initial values
    num_words_f = None
    num_sentences_f = None
    correct_chars_f = None
    syllable_count_f = 0
    monosyllabic_count_f = 0
    polysyllabic_count_f = 0
    ch100 = None
    s100 = None
    s_pattern = ""
    punctuation_marks = string.punctuation

    def count_main_tamil_characters(text):
        # List of main Tamil characters
        main_tamil_chars = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',
                            'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம', 'ய', 'ர',
                            'ல', 'ள', 'ழ', 'வ', 'ற', 'ன', 'ஷ', 'ஸ', 'ஹ', 'ஃ', 'ஜ', 'க்ஷ', 'ஸ்ரீ' ]
        
        # Count the number of main Tamil characters in the text
        num_main_tamil_chars = 0
        skip_next = False  # Flag to skip the next character if 'ஒ' is followed by 'ள' or 'ௌ'
        for i, char in enumerate(text):
            if skip_next:
                skip_next = False
                continue
            
            if char == 'ஒ' and i < len(text) - 2 and text[i+2] == 'ி' and text[i+1] in main_tamil_chars:
                num_main_tamil_chars += 2
                skip_next = True
            elif char == 'ஒ' and i < len(text) - 1 and text[i+1] == 'ள':
                num_main_tamil_chars += 1
                skip_next = True
            elif char in main_tamil_chars and i < len(text) - 1 and text[i+1] == 'ௌ':
                num_main_tamil_chars += 1
                skip_next = True
            elif char in main_tamil_chars:
                num_main_tamil_chars += 1
        return num_main_tamil_chars

    def count_main_tamil_characters100(text):
        # List of main Tamil characters
        main_tamil_chars = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',
                            'க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம', 'ய', 'ர',
                            'ல', 'ள', 'ழ', 'வ', 'ற', 'ன', 'ஷ', 'ஸ', 'ஹ', 'ஃ', 'ஜ', 'க்ஷ', 'ஸ்ரீ' ]
        
        # Count the number of main Tamil characters in the text
        num_main_tamil_chars = 0
        skip_next = False  # Flag to skip the next character if 'ஒ' is followed by 'ள' or 'ௌ'
        for i, char in enumerate(text):
            if skip_next:
                skip_next = False
                continue
            
            if char == 'ஒ' and i < len(text) - 2 and text[i+2] == 'ி' and text[i+1] in main_tamil_chars:
                num_main_tamil_chars += 2
                skip_next = True
            elif char == 'ஒ' and i < len(text) - 1 and text[i+1] == 'ள':
                num_main_tamil_chars += 1
                skip_next = True
            elif char in main_tamil_chars and i < len(text) - 1 and text[i+1] == 'ௌ':
                num_main_tamil_chars += 1
                skip_next = True
            elif char in main_tamil_chars:
                num_main_tamil_chars += 1
        return num_main_tamil_chars

    def count_tamil_text(text):
        # Number of Words
        words = text.split()
        num_words = len(words)

        # Number of Sentences
        sentences = re.split(r'[.!?]+', text)
        num_sentences = len([sentence for sentence in sentences if sentence.strip()])

        # Number of Characters in first 100 Words
        first_100_words = ' '.join(words[:100])
        num_characters_100_words = count_main_tamil_characters100(first_100_words)

        # Number of Sentences per 100 Words
        first_100_words_sentences = re.split(r'[.!?]+', first_100_words)
        num_sentences_per_100_words = len([sentence for sentence in first_100_words_sentences if sentence.strip()])

        return num_words, num_sentences, num_characters_100_words, num_sentences_per_100_words

    def syllablepattern(sentence):
        nonlocal s_pattern, monosyllabic_count_f, polysyllabic_count_f, syllable_count_f

        # Split the sentence into words
        words = sentence.split()

        # Process each word in the sentence
        for word in words:
            V = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ']
            C = ['க்', 'ங்', 'ச்', 'ஞ்', 'ட்', 'ண்', 'த்', 'ந்', 'ப்', 'ம்', 'ர்', 'ல்', 'வ்', 'ழ்', 'ள்', 'ற்', 'ன்', 'ஸ்', 'ஷ்', 'ஜ்', 'ஹ்','ஃ']

            CV1 = ['க', 'ங', 'ச', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ப', 'ம', 'ய', 'ர', 'ல', 'வ', 'ழ', 'ள', 'ற', 'ன','ஸ', 'ஷ', 'ஜ', 'ஹ']

            CV2 = [
            'கா', 'ஙா', 'சா', 'ஞா', 'டா', 'ணா', 'தா', 'நா', 'பா', 'மா', 'யா', 'ரா', 'லா', 'வா', 'ழா', 'ளா', 'றா', 'னா',
            'கி', 'ஙி', 'சி', 'ஞி', 'டி', 'ணி', 'தி', 'நி', 'பி', 'மி', 'யி', 'ரி', 'லி', 'வி', 'ழி', 'ளி', 'றி', 'னி',
            'கீ', 'ஙீ', 'சீ', 'ஞீ', 'டீ', 'ணீ', 'தீ', 'நீ', 'பீ', 'மீ', 'யீ', 'ரீ', 'லீ', 'வீ', 'ழீ', 'ளீ', 'றீ', 'னீ',
            'கு', 'ஙு', 'சு', 'ஞு', 'டு', 'ணு', 'து', 'நு', 'பு', 'மு', 'யு', 'ரு', 'லு', 'வு', 'ழு', 'ளு', 'று', 'னு',
            'கூ', 'ஙூ', 'சூ', 'ஞூ', 'டூ', 'ணூ', 'தூ', 'நூ', 'பூ', 'மூ', 'யூ', 'ரூ', 'லூ', 'வூ', 'ழூ', 'ளூ', 'றூ', 'னூ',
            'கெ', 'ஙெ', 'செ', 'ஞெ', 'டெ', 'ணெ', 'தெ', 'நெ', 'பெ', 'மெ', 'யெ', 'ரெ', 'லெ', 'வெ', 'ழெ', 'ளெ', 'றெ', 'னெ',
            'கே', 'ஙே', 'சே', 'ஞே', 'டே', 'ணே', 'தே', 'நே', 'பே', 'மே', 'யே', 'ரே', 'லே', 'வே', 'ழே', 'ளே', 'றே', 'னே',
            'கை', 'ஙை', 'சை', 'ஞை', 'டை', 'ணை', 'தை', 'நை', 'பை', 'மை', 'யை', 'ரை', 'லை', 'வை', 'ழை', 'ளை', 'றை', 'னை',
            'கொ', 'ஙொ', 'சொ', 'ஞொ', 'டொ', 'ணொ', 'தொ', 'நொ', 'பொ', 'மொ', 'யொ', 'ரொ', 'லொ', 'வொ', 'ழொ', 'ளொ', 'றொ', 'னொ',
            'கோ', 'ஙோ', 'சோ', 'ஞோ', 'டோ', 'ணோ', 'தோ', 'நோ', 'போ', 'மோ', 'யோ', 'ரோ', 'லோ', 'வோ', 'ழோ', 'ளோ', 'றோ', 'னோ',
            'கௌ', 'ஙௌ', 'சௌ', 'ஞௌ', 'டௌ', 'ணௌ', 'தௌ', 'நௌ', 'பௌ', 'மௌ', 'யௌ', 'ரௌ', 'லௌ', 'வௌ', 'ழௌ', 'ளௌ', 'றௌ', 'னௌ',
            'ஸா', 'ஸி', 'ஸீ', 'ஸு', 'ஸூ', 'ஸெ', 'ஸே', 'ஸை', 'ஸொ', 'ஸோ', 'ஸௌ', 'ஷா', 'ஷி', 'ஷீ', 'ஷு', 'ஷூ', 'ஷெ', 'ஷே', 'ஷை', 'ஷொ', 'ஷோ', 'ஷௌ', 'ஜா', 'ஜி', 'ஜீ', 'ஜு', 'ஜூ', 'ஜெ', 'ஜே', 'ஜை', 'ஜொ', 'ஜோ', 'ஜௌ', 'ஹா', 'ஹி', 'ஹீ', 'ஹு', 'ஹூ', 'ஹெ', 'ஹே', 'ஹை', 'ஹொ', 'ஹோ', 'ஹௌ'
            ]

            replaced_word = ""
            i = 0
            while i < len(word):        
                if word[i:i+2] in C:
                    replaced_word += 'C'
                    i += 2
                elif word[i] == 'ஒ' and i + 1 < len(word) and word[i + 1] == 'ள':
                    replaced_word += 'V'
                    i += 2  # Skip the next character 'ள'
                elif word[i] in V:
                    replaced_word += 'V'
                    i += 1
                elif word[i] in CV1 or (i + 1 < len(word) and word[i:i + 2] in CV2):
                    replaced_word += 'CV'
                    i += 2 if word[i:i + 2] in CV2 else 1
                else:
                    replaced_word += word[i]
                    i += 1
            
            s_pattern = replaced_word  # Store the replaced word in the global variable
            split_pattern(s_pattern)  # Call split_pattern function for each word pattern

        return replaced_word


    def split_pattern(pattern):
        nonlocal monosyllabic_count_f, polysyllabic_count_f, syllable_count_f
        combinations = ['CVCC', 'CVC', 'CV', 'V']
        result = []
        num_splits = 0
        i = 0
        while i < len(pattern):
            found = False
            for combo in combinations:
                if pattern[i:i+len(combo)] == combo:
                    result.append(combo)
                    i += len(combo)
                    found = True
                    num_splits += 1
                    break
            if not found:
                result.append(pattern[i])
                i += 1
        
        # Check the number of splits and update global variables accordingly
        if num_splits == 1:
            monosyllabic_count_f += 1
        elif num_splits > 1:
            polysyllabic_count_f += 1
        
        
        # Increment syllable count
        syllable_count_f += num_splits
    
        split_pattern_str = '-'.join(result)
        return split_pattern_str, num_splits, monosyllabic_count_f, polysyllabic_count_f, syllable_count_f

    
    # Get input Tamil text
    text = text.strip()

    # Call the functions
    correct_chars_f = count_main_tamil_characters(text)
    num_words_f, num_sentences_f, ch100, s100 = count_tamil_text(text)
    syllablepattern(text)
     # Calculate readability indices
    ari = Indices_Calculation.calculate_ari(num_words_f, num_sentences_f, correct_chars_f)
    cli = Indices_Calculation.calculate_cli(num_words_f, num_sentences_f, correct_chars_f)
    fre = Indices_Calculation.calculate_fre(num_words_f, num_sentences_f, syllable_count_f)
    fkgl = Indices_Calculation.calculate_fkgl(num_words_f, num_sentences_f, syllable_count_f)
    gfi = Indices_Calculation.calculate_gfi(num_words_f, num_sentences_f, polysyllabic_count_f)
    smog = Indices_Calculation.calculate_smog(num_sentences_f, polysyllabic_count_f)
    forcast = Indices_Calculation.calculate_forcast(num_words_f, monosyllabic_count_f)

    # Personalized indices
    tamilp_index = Indices_Calculation.tamilp(num_words_f, num_sentences_f, correct_chars_f, monosyllabic_count_f, polysyllabic_count_f)

    if correct_chars_f > 0:
        # Construct results dictionary
        results = {
            "Number of Characters": correct_chars_f,
        "Number of Words": num_words_f,
        "Number of Sentences": num_sentences_f,
        "Number of Characters in first 100 Words": ch100,
        "Number of Sentences per 100 Words": s100,
        "Total Syllable Count": syllable_count_f,
        "Monosyllabic Words Count": monosyllabic_count_f,
        "Polysyllabic Words Count": polysyllabic_count_f,
        "ARI": ari,
        "CLI": cli,
        "FRE": fre,
        "FKGL": fkgl,
        "GFI": gfi,
        "SMOG": smog,
        "FORCAST": forcast,
        "Personalized Tamil Index": tamilp_index,
        "Language": "Tamil",
        }

        
    else:
        results={"Error":"Provide the text in Tamil language to analyze"}
    # Return the results
    return results



def analyze_malayalam_text(text):

    # The path to the local git repo for Indic NLP library
    INDIC_NLP_LIB_HOME=r"C:\Users\Udhaya\indic_nlp_library"
    
    # The path to the local git repo for Indic NLP Resources
    INDIC_NLP_RESOURCES=r"C:\Users\Udhaya\indic_nlp_resources-master"
    
    import sys
    sys.path.append(r'{}'.format(INDIC_NLP_LIB_HOME))
    
    from indicnlp import common
    common.set_resources_path(INDIC_NLP_RESOURCES)
    
    from indicnlp import loader
    loader.load()
    
    from indicnlp.syllable import syllabifier
    
    # Declaring global variables without initial values
    num_words_f = None
    num_sentences_f = None
    correct_chars_f = None
    syllable_count_f = 0
    monosyllabic_count_f = 0
    polysyllabic_count_f = 0
    ch100 = None
    s100 = None
    punctuation_marks = string.punctuation
    
    def count_main_malayalam_characters(text):
        characters = ['അ', 'ആ', 'ഇ', 'ഈ', 'ഉ', 'ഊ', 'ഋ', 'ൠ', 'ഌ', 'ൡ', 'എ', 'ഏ', 'ഒ', 'ഓ', 'ഐ', 'ഔ', 'ക', 'ഖ', 'ഗ', 'ഘ', 'ങ', 'ച', 'ഛ', 'ജ', 'ഝ', 'ഞ', 'ട', 'ഠ', 'ഡ', 'ഢ', 'ണ', 'ത', 'ഥ', 'ദ', 'ധ', 'ന', 'ഩ', 'പ', 'ഫ', 'ബ', 'ഭ', 'മ', 'യ', 'ര', 'റ', 'ല', 'ള', 'ഴ', 'വ', 'ശ', 'ഷ', 'സ', 'ഹ', 'ഺ','ൻ','ർ','ൽ','ൾ','ൺ','അം','അഃ']
        charactersfound = []
        malayalam_count = 0
        for char in text:
            if char in characters:
                charactersfound.append(char)
                malayalam_count += 1
        nonlocal correct_chars_f
        correct_chars_f = malayalam_count
        return malayalam_count

    def count_main_malayalam_characters100(text):
        characters = ['അ', 'ആ', 'ഇ', 'ഈ', 'ഉ', 'ഊ', 'ഋ', 'ൠ', 'ഌ', 'ൡ', 'എ', 'ഏ', 'ഒ', 'ഓ', 'ഐ', 'ഔ', 'ക', 'ഖ', 'ഗ', 'ഘ', 'ങ', 'ച', 'ഛ', 'ജ', 'ഝ', 'ഞ', 'ട', 'ഠ', 'ഡ', 'ഢ', 'ണ', 'ത', 'ഥ', 'ദ', 'ധ', 'ന', 'ഩ', 'പ', 'ഫ', 'ബ', 'ഭ', 'മ', 'യ', 'ര', 'റ', 'ല', 'ള', 'ഴ', 'വ', 'ശ', 'ഷ', 'സ', 'ഹ', 'ഺ','ൻ','ർ','ൽ','ൾ','ൺ','അം','അഃ']
        charactersfound = []
        malayalam_count = 0
        for char in text:
            if char in characters:
                charactersfound.append(char)
                malayalam_count += 1
        return malayalam_count
    
    def count_malayalam_text(text):
        # Number of Words
        words = text.split()
        num_words = len(words)
    
        # Number of Sentences
        sentences = re.split(r'[.!?]+', text)
        num_sentences = len([sentence for sentence in sentences if sentence.strip()])
    
        # Number of Characters in first 100 Words
        first_100_words = ' '.join(words[:100])
        num_characters_100_words = count_main_malayalam_characters100(first_100_words)
    
        # Number of Sentences per 100 Words
        first_100_words_sentences = re.split(r'[.!?]+', first_100_words)
        num_sentences_per_100_words = len([sentence for sentence in first_100_words_sentences if sentence.strip()])
    
        # Assign calculated values
        nonlocal num_words_f, num_sentences_f, ch100, s100
        num_words_f = num_words
        num_sentences_f = num_sentences
        ch100 = num_characters_100_words
        s100 = num_sentences_per_100_words
    
        return num_words, num_sentences, num_characters_100_words, num_sentences_per_100_words
    
    def count_syllables(sentence):
        nonlocal monosyllabic_count_f, polysyllabic_count_f, syllable_count_f
        
        # Create a translation table that maps punctuation characters to None
        translator = str.maketrans('', '', string.punctuation)
        # Split the sentence into words
        words = sentence.split()
    
        # Iterate through each word in the sentence
        for word in words:
            # Remove punctuation from the word
            clean_word = word.translate(translator)
            # Get the syllable count for the word
            syllables = syllabifier.orthographic_syllabify(word, 'ml')
            syllable_count = len(syllables)
            
            # Update global syllable count
            syllable_count_f += syllable_count
            
            # Count monosyllabic and polysyllabic words
            if syllable_count == 1:
                monosyllabic_count_f += 1
            elif syllable_count >= 2:
                polysyllabic_count_f += 1
        
        return monosyllabic_count_f, polysyllabic_count_f, syllable_count_f
    
    # Call the functions
    count_main_malayalam_characters(text)
    count_malayalam_text(text)
    count_syllables(text)
    
      # Calculate readability indices
    ari = Indices_Calculation.calculate_ari(num_words_f, num_sentences_f, correct_chars_f)
    cli = Indices_Calculation.calculate_cli(num_words_f, num_sentences_f, correct_chars_f)
    fre = Indices_Calculation.calculate_fre(num_words_f, num_sentences_f, syllable_count_f)
    fkgl = Indices_Calculation.calculate_fkgl(num_words_f, num_sentences_f, syllable_count_f)
    gfi = Indices_Calculation.calculate_gfi(num_words_f, num_sentences_f, polysyllabic_count_f)
    smog = Indices_Calculation.calculate_smog(num_sentences_f, polysyllabic_count_f)
    forcast = Indices_Calculation.calculate_forcast(num_words_f, monosyllabic_count_f)

    # Personalized indices
    malayalamp_index = Indices_Calculation.malayalamp(num_words_f, num_sentences_f, correct_chars_f, monosyllabic_count_f, polysyllabic_count_f)

    if correct_chars_f > 0:
        # Construct results dictionary
        results = {
            "Number of Characters": correct_chars_f,
        "Number of Words": num_words_f,
        "Number of Sentences": num_sentences_f,
        "Number of Characters in first 100 Words": ch100,
        "Number of Sentences per 100 Words": s100,
        "Total Syllable Count": syllable_count_f,
        "Monosyllabic Words Count": monosyllabic_count_f,
        "Polysyllabic Words Count": polysyllabic_count_f,
        "ARI": ari,
        "CLI": cli,
        "FRE": fre,
        "FKGL": fkgl,
        "GFI": gfi,
        "SMOG": smog,
        "FORCAST": forcast,
        "Personalized Malayalam Index": malayalamp_index,
        "Language": "Malayalam",
        }

        
    else:
        results={"Error":"Provide the text in Malayalam language to analyze"}
    # Return the results
    return results



def analyze_telugu_text(text):

    # The path to the local git repo for Indic NLP library
    INDIC_NLP_LIB_HOME=r"C:\Users\Udhaya\indic_nlp_library"
    
    # The path to the local git repo for Indic NLP Resources
    INDIC_NLP_RESOURCES=r"C:\Users\Udhaya\indic_nlp_resources-master"
    
    import sys
    sys.path.append(r'{}'.format(INDIC_NLP_LIB_HOME))
    
    from indicnlp import common
    common.set_resources_path(INDIC_NLP_RESOURCES)
    
    from indicnlp import loader
    loader.load()
    
    from indicnlp.syllable import syllabifier
    
    # Declaring global variables without initial values
    num_words_f = None
    num_sentences_f = None
    correct_chars_f = None
    syllable_count_f = 0
    monosyllabic_count_f = 0
    polysyllabic_count_f = 0
    ch100 = None
    s100 = None
    punctuation_marks = string.punctuation
    
    def count_main_telugu_characters(text):
        characters = ['అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఌ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ', 'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ', 'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ఱ', 'ల', 'ళ', 'ఴ', 'వ', 'శ', 'ష', 'స', 'హ', '౸', '౹', '౺', '౻', '౼', '౽', '౾', '౿', 'ౘ', 'ౙ', 'ౚ', '౦', '౧', '౨', '౩', '౪', '౫', '౬', '౭', '౮', '౯']
        charactersfound = []
        telugu_count = 0
        for char in text:
            if char in characters:
                charactersfound.append(char)
                telugu_count += 1
        nonlocal correct_chars_f
        correct_chars_f = telugu_count
        return telugu_count

    def count_main_telugu_characters100(text):
        characters = ['అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఌ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ', 'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ', 'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ఱ', 'ల', 'ళ', 'ఴ', 'వ', 'శ', 'ష', 'స', 'హ', '౸', '౹', '౺', '౻', '౼', '౽', '౾', '౿', 'ౘ', 'ౙ', 'ౚ', '౦', '౧', '౨', '౩', '౪', '౫', '౬', '౭', '౮', '౯']
        charactersfound = []
        telugu_count = 0
        for char in text:
            if char in characters:
                charactersfound.append(char)
                telugu_count += 1
        
        return telugu_count
    
    def count_telugu_text(text):
        # Number of Words
        words = text.split()
        num_words = len(words)

        # Number of Sentences
        sentences = re.split(r'[.!?]+', text)
        num_sentences = len([sentence for sentence in sentences if sentence.strip()])

        # Number of Characters in first 100 Words
        first_100_words = ' '.join(words[:100])
        num_characters_100_words = count_main_telugu_characters100(first_100_words)

        # Number of Sentences per 100 Words
        first_100_words_sentences = re.split(r'[.!?]+', first_100_words)
        num_sentences_per_100_words = len([sentence for sentence in first_100_words_sentences if sentence.strip()])

        # Assign calculated values to global variables
        nonlocal num_words_f, num_sentences_f, ch100, s100
        num_words_f = num_words
        num_sentences_f = num_sentences
        ch100 = num_characters_100_words
        s100 = num_sentences_per_100_words

        return num_words, num_sentences, num_characters_100_words, num_sentences_per_100_words

    def count_syllables(sentence):
        nonlocal monosyllabic_count_f, polysyllabic_count_f, syllable_count_f
        
        # Create a translation table that maps punctuation characters to None
        translator = str.maketrans('', '', string.punctuation)

        # Split the sentence into words
        words = sentence.split()

        # Iterate through each word in the sentence
        for word in words:
            # Remove punctuation from the word
            clean_word = word.translate(translator)
            # Get the syllable count for the word
            syllables = syllabifier.orthographic_syllabify(word, 'te')
            syllable_count = len(syllables)
            
            # Update global syllable count
            syllable_count_f += syllable_count
            
            # Count monosyllabic and polysyllabic words
            if syllable_count == 1:
                monosyllabic_count_f += 1
            elif syllable_count >= 2:
                polysyllabic_count_f += 1
        
        return monosyllabic_count_f, polysyllabic_count_f, syllable_count_f    

    # Call the functions
    count_main_telugu_characters(text)
    count_telugu_text(text)
    count_syllables(text)
    
      # Calculate readability indices
    ari = Indices_Calculation.calculate_ari(num_words_f, num_sentences_f, correct_chars_f)
    cli = Indices_Calculation.calculate_cli(num_words_f, num_sentences_f, correct_chars_f)
    fre = Indices_Calculation.calculate_fre(num_words_f, num_sentences_f, syllable_count_f)
    fkgl = Indices_Calculation.calculate_fkgl(num_words_f, num_sentences_f, syllable_count_f)
    gfi = Indices_Calculation.calculate_gfi(num_words_f, num_sentences_f, polysyllabic_count_f)
    smog = Indices_Calculation.calculate_smog(num_sentences_f, polysyllabic_count_f)
    forcast = Indices_Calculation.calculate_forcast(num_words_f, monosyllabic_count_f)

    # Personalized indices
    telugup_index = Indices_Calculation.telugup(num_words_f, num_sentences_f, correct_chars_f, monosyllabic_count_f, polysyllabic_count_f)

    if correct_chars_f > 0:
        # Construct results dictionary
        results = {
            "Number of Characters": correct_chars_f,
        "Number of Words": num_words_f,
        "Number of Sentences": num_sentences_f,
        "Number of Characters in first 100 Words": ch100,
        "Number of Sentences per 100 Words": s100,
        "Total Syllable Count": syllable_count_f,
        "Monosyllabic Words Count": monosyllabic_count_f,
        "Polysyllabic Words Count": polysyllabic_count_f,
        "ARI": ari,
        "CLI": cli,
        "FRE": fre,
        "FKGL": fkgl,
        "GFI": gfi,
        "SMOG": smog,
        "FORCAST": forcast,
        "Personalized Telugu Index": telugup_index,
        "Language": "Telugu",
        }

        
    else:
        results={"Error":"Provide the text in Telugu language to analyze"}
    # Return the results
    return results

# Function to handle database creation, table creation, and data insertion
def handle_feedback(name, email, subject, message):
    db_path = 'feedback.db'
    
    # Create the database and table if they don't exist
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT,
                feedback TEXT NOT NULL
            )
        ''')
        conn.commit()

        # Check if the subject is empty and replace it with '-'
        if not subject:
            subject = '-'
        
        # Insert the feedback data
        cursor.execute('''
            INSERT INTO feedback (name, email, subject, feedback)
            VALUES (?, ?, ?, ?)
        ''', (name, email, subject, message))
        conn.commit()
    pass



# Define a route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit_feedback', methods=['POST'])
def feedback():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    
    # Call the function to handle feedback
    handle_feedback(name, email, subject, message)

    # Return a JSON response indicating success
    return jsonify({'success': True, 'message': 'Feedback submitted successfully!'})

    
    
# Define a route to handle form submission
@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the text from the form submission
    text = request.form['text']
    language = request.form['language']
     # Get current date and time
    current_datetime = datetime.datetime.now()
# Extract date and time separately
    datedb = current_datetime.date()
    #timedb = current_datetime.time()
    # Convert time to string representation
    timedb = current_datetime.strftime('%H:%M:%S')

    # Call your analysis function
    if language == 'tamil':
        results = analyze_tamil_text(text)
    elif language == 'telugu':
        results = analyze_telugu_text(text)
    elif language == 'malayalam':
        results = analyze_malayalam_text(text)
    else:
        results = {'Error': 'Invalid language selection'}
    
    if 'Error' in results:
        print("Error: Database operation not performed.")
        return jsonify(results), 400

   


    try:
        # Store results in SQLite database
        conn = sqlite3.connect('analysis_results.db')
        cursor = conn.cursor()

        # Insert results into database
        cursor.execute('''
            INSERT INTO analysis_results (date, time, text, language, num_characters, num_words, num_sentences,
            num_characters_100_words, num_sentences_per_100_words, total_syllable_count, monosyllabic_words_count,
            polysyllabic_words_count, ARI, CLI, FRE, FKGL, GFI, SMOG, FORCAST, personalized_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datedb, timedb, text, language, results['Number of Characters'], results['Number of Words'],
            results['Number of Sentences'], results['Number of Characters in first 100 Words'],
            results['Number of Sentences per 100 Words'], results['Total Syllable Count'],
            results['Monosyllabic Words Count'], results['Polysyllabic Words Count'], results['ARI'],
            results['CLI'], results['FRE'], results['FKGL'], results['GFI'], results['SMOG'], results['FORCAST'],
            results['Personalized Tamil Index'] if language == 'tamil' else
            results['Personalized Malayalam Index'] if language == 'malayalam' else
            results['Personalized Telugu Index']))

        # Commit changes and close connection
        conn.commit()
        conn.close()
        print("Database operation performed successfully.")

    except sqlite3.Error as e:
        print("Error executing database operation:", e)
        return jsonify({'Error': 'Database operation failed'}), 500

    # Return the results as JSON
    return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True)