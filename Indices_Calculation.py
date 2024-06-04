import math
# Automated Readability Index (ARI)
def calculate_ari(words, sentences, characters):
    if words == 0 or sentences == 0:
        return 0
    ari = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
    return round(ari, 2)

# Coleman-Liau Index (CLI)
def calculate_cli(words, sentences, characters):
    if words == 0 or sentences == 0:
        return 0
    L = (characters / words) * 100  # Average characters per 100 words
    S = (sentences / words) * 100  # Average sentences per 100 words
    cli = 0.0588 * L - 0.296 * S - 15.8
    return round(cli, 2)

# Flesch Reading Ease (FRE)
def calculate_fre(words, sentences, syllables):
    if words == 0 or sentences == 0:
        return 0
    fre = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return round(fre, 2)

# Flesch-Kincaid Grade Level (FKGL)
def calculate_fkgl(words, sentences, syllables):
    if words == 0 or sentences == 0:
        return 0
    fkgl = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    return round(fkgl, 2)

# Gunning Fog Index (GFI)
def calculate_gfi(words, sentences, polysyllabic_words):
    if words == 0 or sentences == 0:
        return 0
    gfi = 0.4 * ((words / sentences) + 100 * (polysyllabic_words / words))
    return round(gfi, 2)

# Simple Measure of Gobbledygook (SMOG) Index
def calculate_smog(sentences, polysyllabic_words):
    if sentences == 0:
        return 0
    smog = 1.043 * math.sqrt(polysyllabic_words * (30 / sentences)) + 3.1291
    return round(smog, 2)

# FORCAST Readability Formula
def calculate_forcast(words, monosyllabic_words):
    if words == 0:
        return 0
    forcast = 20 - (monosyllabic_words / (words / 150))
    return round(forcast, 2)


#Personalized Tamil Index
def tamilp(words, sentences, characters, monosyllabic_words, polysyllabic_words):
    if words == 0 or sentences == 0:
        return 0
    tamilp = 0.003 * characters - 0.006 * words + 0.820 * polysyllabic_words - 0.017 * monosyllabic_words - 0.066 * sentences + 8.024

    return round(tamilp, 2)

#Personalized Malayalam Index
def malayalamp(words, sentences, characters, monosyllabic_words, polysyllabic_words):
    if words == 0 or sentences == 0:
        return 0
    malayalamp = 0.010 * monosyllabic_words - 0.168 * sentences + 0.003 * characters - 0.023 * words + 4.003
    return round(malayalamp, 2)

#Personalized Telugu Index
def telugup(words, sentences, characters, monosyllabic_words, polysyllabic_words):
    if words == 0 or sentences == 0:
        return 0
    telugup = 0.025 * monosyllabic_words + 0.165 * sentences + 0.019 * characters - 0.058 * words - 14.498
    return round(telugup, 2)

def display_readability_results(words, sentences, characters, syllables, monosyllabic_words, polysyllabic_words):
    # Calculate each readability index using the respective functions
    ari = calculate_ari(words, sentences, characters)
    cli = calculate_cli(words, sentences, characters)
    fre = calculate_fre(words, sentences, syllables)
    fkgl = calculate_fkgl(words, sentences, syllables)
    gfi = calculate_gfi(words, sentences, polysyllabic_words)
    smog = calculate_smog(sentences, polysyllabic_words)
    forcast = calculate_forcast(words, monosyllabic_words)

    # Display the results
    print("\n")
    print("Readability Indices Results:")
    print(f"Automated Readability Index (ARI): {ari}")
    print(f"Coleman-Liau Index (CLI): {cli}")
    print(f"Flesch Reading Ease (FRE): {fre}")
    print(f"Flesch-Kincaid Grade Level (FKGL): {fkgl}")
    print(f"Gunning Fog Index (GFI): {gfi}")
    print(f"Simple Measure of Gobbledygook (SMOG) Index: {smog}")
    print(f"FORCAST Readability Formula: {forcast}")
