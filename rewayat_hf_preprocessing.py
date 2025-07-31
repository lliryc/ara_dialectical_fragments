import os
import glob
import html
import re
import warnings
import pandas as pd
from lingua import Language, LanguageDetectorBuilder

languages = [Language.ARABIC]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


REWAYAT_SEARCH_DIR = "rewayat/rewayat-files-pos-segmented-html-cleaned/*"

def clean_html_entities(text):
    """Convert HTML entities to their proper characters"""
    return html.unescape(text)

def process_backslashes(text):
    """Process backslash escape sequences manually"""
    text = text.replace('\\n', '\n')
    text = text.replace('\\t', '\t')
    text = text.replace('\\r', '\r')
    text = text.replace('\\"', '"')
    text = text.replace("\\'", "'")
    text = text.replace('\\\\', '\\')
    return text

def has_multiple_punctuation_marks(text):
    """Check if text contains more than 1 punctuation mark (adjacent punctuation counts as 1)"""
    # Define punctuation marks to look for
    punctuation_marks = r'[.!?،؛؟!]'
    
    # Find all punctuation marks in the text
    punctuation_positions = []
    for i, char in enumerate(text):
        if re.match(punctuation_marks, char):
            punctuation_positions.append(i)
    
    # If less than 2 punctuation marks, return False
    if len(punctuation_positions) < 2:
        return False
    
    # Group adjacent punctuation marks together
    punctuation_groups = []
    current_group = [punctuation_positions[0]]
    
    for i in range(1, len(punctuation_positions)):
        if punctuation_positions[i] - punctuation_positions[i-1] == 1:
            # Adjacent punctuation, add to current group
            current_group.append(punctuation_positions[i])
        else:
            # Non-adjacent punctuation, start new group
            punctuation_groups.append(current_group)
            current_group = [punctuation_positions[i]]
    
    # Add the last group
    punctuation_groups.append(current_group)
    
    # Return True if there are at least 2 groups of punctuation marks
    return len(punctuation_groups) >= 2

def extract_speaker_paragraphs_with_punctuation(text):
    """Extract only paragraphs that contain speaker dialogue with multiple punctuation marks"""
    # First clean HTML entities and process backslashes
    text = clean_html_entities(text)
    text = process_backslashes(text)
    
    # Split into sections
    sections = text.split('##########')
    speaker_paragraphs = []
    
    for section in sections:
        if not section.strip():
            continue
            
        paragraphs = section.strip().split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if paragraph starts with a speaker pattern (name: dialogue)
            # Pattern: word(s) followed by colon, then dialogue
            speaker_pattern = r'^([^:]+):\s*(.+)$'
            match = re.match(speaker_pattern, paragraph)
            
            if not match:
                continue
            
            dialogue = match.group(2).strip()
            
            if not dialogue:
                continue
            
            paragraphs = dialogue.split('\n\n')
            for paragraph in paragraphs:
                if not paragraph.strip():
                    continue
                
                if not has_multiple_punctuation_marks(paragraph):
                    continue
                # Check if dialogue is in Arabic
                lang_detected = detector.detect_language_of(dialogue)
                if lang_detected != Language.ARABIC:
                    continue

                if not has_multiple_punctuation_marks(dialogue):
                    continue
                
                speaker_paragraphs.append(dialogue)

    return speaker_paragraphs


OUTPUT_DIR = "rewayat_tsv"

if __name__ == "__main__":
    for file in glob.glob(REWAYAT_SEARCH_DIR):
        basename = os.path.basename(file).replace(".txt", "")
        target_file = f"{OUTPUT_DIR}/{basename}.tsv"

        with open(file, 'r') as f:
            text = f.read()

        speaker_paragraphs = extract_speaker_paragraphs_with_punctuation(text)
        pd.DataFrame(speaker_paragraphs, columns=["text"]).to_csv(target_file, index=False, sep='\t', quoting=1)
