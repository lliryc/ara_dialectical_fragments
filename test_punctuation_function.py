import re

def has_multiple_punctuation_marks(text):
    """Check if text contains more than 1 punctuation mark (adjacent punctuation counts as 1)"""
    # Define punctuation marks to look for
    punctuation_marks = r'[.!?،؛:؟!]'
    
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

# Test cases
test_cases = [
    "Hello world",  # No punctuation
    "Hello world!",  # One punctuation
    "Hello world!!",  # Adjacent punctuation (should count as 1)
    "Hello world! How are you?",  # Multiple non-adjacent punctuation
    "Hello world!! How are you?",  # Multiple with some adjacent
    "Hello world! How are you!!",  # Multiple with some adjacent
    "Hello world!! How are you!!",  # All adjacent (should count as 1)
    "مرحبا بالعالم",  # No punctuation
    "مرحبا بالعالم!",  # One punctuation
    "مرحبا بالعالم!!",  # Adjacent punctuation (should count as 1)
    "مرحبا بالعالم! كيف حالك؟",  # Multiple non-adjacent punctuation
    "مرحبا بالعالم!! كيف حالك؟",  # Multiple with some adjacent
    "مرحبا بالعالم! كيف حالك!!",  # Multiple with some adjacent
    "مرحبا بالعالم!! كيف حالك!!",  # All adjacent (should count as 1)
]

print("Testing has_multiple_punctuation_marks function:")
print("=" * 50)

for i, test_text in enumerate(test_cases, 1):
    result = has_multiple_punctuation_marks(test_text)
    print(f"{i:2d}. '{test_text}' -> {result}") 