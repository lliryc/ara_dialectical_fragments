import re

# Test with various dialogue examples
test_text = """دك محمد: الي اعرفه انه لج سياره صح

اماني: صح

دك محمد: انتي روحي لسوق السمك واشري الي تبينه

اماني: ودي بس الوالده الله يحفظها تقول لا

دك محمد: الله يحفظها لنا انتي قولي لها شوفي انا مشغول يلا سلام

اماني: مع سلامه يا اناني  بعد عشر دقايق يدق تلفون اماني

اماني : الو

ضاري: انت من جدك تبي تقتلني على شي مو متاكد منه

طلال: انا كنت حاس والحين تاكدت ان انت السبب

ضاري: صالح صالح تكفى لاتموت تكفى وربي غصبن عني تكفى اصحى ادري انكتسمعني اصحى تكفى عيالك يبونك اصحى"""

def extract_speaker_dialogue_with_punctuation(text):
    """Extract only paragraphs that contain speaker dialogue with multiple punctuation marks"""
    paragraphs = text.strip().split('\n\n')
    speaker_paragraphs = []
    
    # Define punctuation marks to look for
    punctuation_marks = r'[.!?،؛:؟!]'
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if paragraph starts with a speaker pattern (name: dialogue)
        speaker_pattern = r'^([^:]+):\s*(.+)$'
        match = re.match(speaker_pattern, paragraph)
        
        if match:
            speaker_name = match.group(1).strip()
            dialogue = match.group(2).strip()
            
            print(f"Speaker: '{speaker_name}'")
            print(f"Dialogue: '{dialogue}'")
            
            # Only include if there's actual dialogue content
            if dialogue:
                # Find all punctuation marks in the dialogue
                punctuation_positions = []
                for i, char in enumerate(dialogue):
                    if re.match(punctuation_marks, char):
                        punctuation_positions.append(i)
                
                print(f"Punctuation positions: {punctuation_positions}")
                
                # Check if there are multiple punctuation marks that are not adjacent
                has_multiple_punctuation = False
                if len(punctuation_positions) >= 2:
                    for i in range(len(punctuation_positions) - 1):
                        if punctuation_positions[i+1] - punctuation_positions[i] > 1:
                            has_multiple_punctuation = True
                            break
                
                print(f"Has multiple non-adjacent punctuation: {has_multiple_punctuation}")
                
                if has_multiple_punctuation:
                    speaker_paragraphs.append(dialogue)
                    print("✓ INCLUDED")
                else:
                    print("✗ EXCLUDED")
            
            print("---")
    
    return '\n\n'.join(speaker_paragraphs)

result = extract_speaker_dialogue_with_punctuation(test_text)
print("\nFINAL RESULT (only dialogues with multiple punctuation marks):")
print(result) 