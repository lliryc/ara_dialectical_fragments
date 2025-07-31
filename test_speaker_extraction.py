import re

# Test with the example you provided
test_text = """دك محمد: الي اعرفه انه لج سياره صح

اماني: صح

دك محمد: انتي روحي لسوق السمك واشري الي تبينه

اماني: ودي بس الوالده الله يحفظها تقول لا

دك محمد: الله يحفظها لنا انتي قولي لها شوفي انا مشغول يلا سلام

اماني: مع سلامه يا اناني  بعد عشر دقايق يدق تلفون اماني

اماني : الو"""

def extract_speaker_dialogue(text):
    """Extract only paragraphs that contain speaker dialogue, excluding speaker labels"""
    paragraphs = text.strip().split('\n\n')
    speaker_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if paragraph starts with a speaker pattern (name: dialogue)
        # Pattern: word(s) followed by colon, then dialogue
        speaker_pattern = r'^([^:]+):\s*(.+)$'
        match = re.match(speaker_pattern, paragraph)
        
        if match:
            speaker_name = match.group(1).strip()
            dialogue = match.group(2).strip()
            
            print(f"Speaker: '{speaker_name}'")
            print(f"Dialogue: '{dialogue}'")
            print("---")
            
            # Only include if there's actual dialogue content
            if dialogue:
                speaker_paragraphs.append(dialogue)
    
    return '\n\n'.join(speaker_paragraphs)

result = extract_speaker_dialogue(test_text)
print("\nFINAL RESULT:")
print(result) 