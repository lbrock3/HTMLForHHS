import re
import sys

def clean_text(text):
    # Remove any special characters that might interfere with parsing
    text = re.sub(r'["""]', '"', text)
    return text

def parse_vocabulary(text):
    # Clean the input text
    text = clean_text(text)
    
    # Split into sections by double newlines
    sections = text.strip().split('\n\n')
    vocabulary = []
    
    for section in sections:
        lines = section.strip().split('\n')
        
        # Skip empty sections
        if not lines:
            continue
            
        # Process each line
        for line in lines:
            # Skip section headers (lines without =)
            if '=' not in line:
                continue
                
            # Split line on equals sign
            parts = line.split('=')
            if len(parts) == 2:
                spanish = parts[0].strip()
                english = parts[1].strip()
                
                # Clean up parenthetical expressions
                spanish = re.sub(r'\s*\(([^)]+)\)', r' (\1)', spanish)
                english = re.sub(r'\s*\(([^)]+)\)', r' (\1)', english)
                
                if spanish and english:
                    vocabulary.append({
                        'spanish': spanish,
                        'english': english
                    })
    
    return vocabulary

def generate_html(vocabulary):
    # Create word list and hints from vocabulary
    word_list = []
    word_hints = {}
    
    for item in vocabulary:
        spanish = item['spanish'].lower().strip()
        english = item['english'].strip()
        
        # Skip if it's just an article
        if spanish in ['el', 'la', 'los', 'las']:
            continue
            
        # Clean the phrase while preserving spaces
        clean_phrase = ''.join(c for c in spanish if c.isalpha() or c == 'ñ' or c == ' ')
        clean_phrase = ' '.join(clean_phrase.split())  # Normalize spaces
        
        # Skip very short single words and articles
        if (len(clean_phrase.split()) == 1 and 
            (len(clean_phrase) <= 2 or 
             clean_phrase in ['el', 'la', 'los', 'las', 'de', 'al', 'un', 'una'])):
            continue
            
        if clean_phrase:
            word_list.append(clean_phrase)
            word_hints[clean_phrase] = english
    
    if not word_list:
        print("Error: No valid words found in vocabulary!")
        return None

    # Print the word list for debugging
    print("\nPhrases and words in the game:")
    for word in sorted(word_list, key=len):
        print(f"- {word} = {word_hints[word]}")

    # Convert word list to JavaScript array string
    word_list_js = "[\n        \"" + "\",\n        \"".join(word_list) + "\"\n    ]"
    
    # Convert hints to JavaScript object string
    hints_js = "{\n"
    for word in word_list:
        hints_js += f"        '{word}': '{word_hints[word]}',\n"
    hints_js += "    }"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spanish Wordle</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #f0f2f5;
        }}
        
        .game-board {{
            display: grid;
            grid-template-rows: repeat(6, 1fr);
            gap: 5px;
            margin: 20px;
        }}
        
        .row {{
            display: grid;
            grid-auto-flow: column;
            gap: 5px;
        }}
        
        .tile {{
            width: 40px;
            height: 40px;
            border: 2px solid #d3d6da;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.5rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .space-tile {{
            background-color: #e8e8e8;
            border: none;
        }}
        
        .keyboard {{
            display: grid;
            gap: 5px;
            margin: 20px;
        }}
        
        .keyboard-row {{
            display: flex;
            justify-content: center;
            gap: 5px;
        }}
        
        .key {{
            padding: 15px;
            min-width: 20px;
            border: none;
            border-radius: 4px;
            background-color: #d3d6da;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
        }}
        
        .correct {{
            background-color: #6aaa64;
            color: white;
            border-color: #6aaa64;
        }}
        
        .present {{
            background-color: #c9b458;
            color: white;
            border-color: #c9b458;
        }}
        
        .absent {{
            background-color: #787c7e;
            color: white;
            border-color: #787c7e;
        }}
        
        .message {{
            margin: 20px;
            padding: 10px;
            border-radius: 4px;
            display: none;
            text-align: center;
        }}
        
        .hint {{
            margin: 10px;
            font-style: italic;
            color: #666;
            text-align: center;
            max-width: 400px;
        }}

        .word-length {{
            margin: 10px;
            font-weight: bold;
            color: #444;
        }}
        
        .button-container {{
            display: flex;
            gap: 10px;
            margin: 10px;
        }}
        
        .control-button {{
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }}
        
        .control-button:hover {{
            background-color: #45a049;
        }}
        
        .hidden {{
            display: none !important;
        }}
        
        #newWordButton {{
            margin-top: 20px;
            padding: 15px 30px;
            font-size: 1.2em;
        }}
        
        #spaceKey {{
            width: 200px;
        }}
    </style>
</head>
<body>
    <h1>Spanish Wordle</h1>
    <div class="button-container">
        <button class="control-button" id="toggleHint">Show Hint</button>
    </div>
    <div class="word-length" id="wordLength"></div>
    <div class="hint hidden" id="hint"></div>
    <div class="game-board" id="gameBoard"></div>
    <div class="keyboard" id="keyboard"></div>
    <div class="message" id="message"></div>
    <button class="control-button hidden" id="newWordButton">New Word</button>

    <script>
    const WORDS = {word_list_js};
    const WORD_HINTS = {hints_js};
    
    function normalizeString(str) {{
        return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }}
    
    const MAX_ATTEMPTS = 6;
    let currentAttempt = 0;
    let currentWord = '';
    let gameOver = false;
    let targetWord = WORDS[Math.floor(Math.random() * WORDS.length)];
    let hintShown = false;
    
    function initializeGame() {{
        currentAttempt = 0;
        currentWord = '';
        gameOver = false;
        targetWord = WORDS[Math.floor(Math.random() * WORDS.length)];
        hintShown = false;
        
        const gameBoard = document.getElementById('gameBoard');
        gameBoard.innerHTML = '';
        
        const hintElement = document.getElementById('hint');
        hintElement.classList.add('hidden');
        document.getElementById('toggleHint').textContent = 'Show Hint';
        
        document.getElementById('newWordButton').classList.add('hidden');
        
        const wordCount = targetWord.split(' ').length;
        document.getElementById('wordLength').textContent = 
            `Phrase length: ${{targetWord.length}} characters (${{wordCount}} word${{wordCount > 1 ? 's' : ''}})`;
        
        for (let i = 0; i < MAX_ATTEMPTS; i++) {{
            const row = document.createElement('div');
            row.className = 'row';
            for (let j = 0; j < targetWord.length; j++) {{
                const tile = document.createElement('div');
                tile.className = 'tile';
                if (targetWord[j] === ' ') {{
                    tile.classList.add('space-tile');
                }}
                row.appendChild(tile);
            }}
            gameBoard.appendChild(row);
        }}
        
        createKeyboard();
        document.getElementById('hint').textContent = WORD_HINTS[targetWord];
    }}
    
    function createKeyboard() {{
        const keyboard = document.getElementById('keyboard');
        keyboard.innerHTML = '';
        const keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ñ'],
            ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '⌫'],
            ['SPACE']
        ];
        
        keys.forEach(row => {{
            const keyboardRow = document.createElement('div');
            keyboardRow.className = 'keyboard-row';
            row.forEach(key => {{
                const button = document.createElement('button');
                button.className = 'key';
                if (key === 'SPACE') {{
                    button.textContent = '␣';
                    button.id = 'spaceKey';
                }} else {{
                    button.textContent = key;
                }}
                button.onclick = () => handleKeyInput(key === 'SPACE' ? ' ' : key);
                keyboardRow.appendChild(button);
            }});
            keyboard.appendChild(keyboardRow);
        }});
    }}
    
    function handleKeyInput(key) {{
        if (gameOver) return;
        
        if (key === '⌫') {{
            currentWord = currentWord.slice(0, -1);
        }} else if (key === 'ENTER') {{
            if (currentWord.length === targetWord.length) {{
                checkWord();
            }}
        }} else if (currentWord.length < targetWord.length) {{
            currentWord += key.toLowerCase();
        }}
        
        updateDisplay();
    }}
    
    function updateDisplay() {{
        const row = document.querySelectorAll('.row')[currentAttempt];
        const tiles = row.querySelectorAll('.tile');
        
        tiles.forEach((tile, i) => {{
            tile.textContent = currentWord[i] || '';
            if (!tile.classList.contains('space-tile')) {{
                tile.className = 'tile';
            }}
        }});
    }}
    
    function checkWord() {{
        const row = document.querySelectorAll('.row')[currentAttempt];
        const tiles = row.querySelectorAll('.tile');
        
        let correct = 0;
        const letterCounts = {{}};
        const normalizedTarget = normalizeString(targetWord);
        
        normalizedTarget.split('').forEach(letter => {{
            letterCounts[letter] = (letterCounts[letter] || 0) + 1;
        }});
        
        const normalizedGuess = normalizeString(currentWord);
        
        normalizedGuess.split('').forEach((letter, i) => {{
            if (letter === normalizedTarget[i]) {{
                tiles[i].classList.add('correct');
                correct++;
                letterCounts[letter]--;
            }}
        }});
        
        normalizedGuess.split('').forEach((letter, i) => {{
            if (letter !== normalizedTarget[i] && !tiles[i].classList.contains('space-tile')) {{
                if (letterCounts[letter] > 0) {{
                    tiles[i].classList.add('present');
                    letterCounts[letter]--;
                }} else {{
                    tiles[i].classList.add('absent');
                }}
            }}
        }});
        
        if (correct === targetWord.length) {{
            gameOver = true;
            showMessage('¡Felicitaciones! Click "New Word" to play again', 'success');
            document.getElementById('newWordButton').classList.remove('hidden');
        }} else if (currentAttempt === MAX_ATTEMPTS - 1) {{
            gameOver = true;
            showMessage(`Game Over! The word was "${{targetWord}}". Click "New Word" to try again`, 'error');
            document.getElementById('newWordButton').classList.remove('hidden');
        }}
        
        currentAttempt++;
        currentWord = '';
    }}
    
    function showMessage(text, type) {{
        const message = document.getElementById('message');
        message.textContent = text;
        message.style.display = 'block';
        message.style.backgroundColor = type === 'error' ? '#f44336' : '#4caf50';
        message.style.color = 'white';
    }}
    
    function toggleHint() {{
        const hintElement = document.getElementById('hint');
        const toggleButton = document.getElementById('toggleHint');
        hintShown = !hintShown;
        
        if (hintShown) {{
            hintElement.classList.remove('hidden');
            toggleButton.textContent = 'Hide Hint';
        }} else {{
            hintElement.classList.add('hidden');
            toggleButton.textContent = 'Show Hint';
        }}
    }}
    
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') {{
            handleKeyInput('ENTER');
        }} else if (e.key === 'Backspace') {{
            handleKeyInput('⌫');
        }} else if (e.key === ' ') {{
            handleKeyInput(' ');
        }} else if (/^[a-zñ]$/i.test(e.key)) {{
            handleKeyInput(e.key.toUpperCase());
        }}
    }});
    
    document.getElementById('toggleHint').addEventListener('click', toggleHint);
    document.getElementById('newWordButton').addEventListener('click', initializeGame);
    
    initializeGame();
    </script>
</body>
</html>'''

    return html

def get_multiline_input():
    print("\nPaste your Spanish vocabulary below (format: spanish = english)")
    print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:")
    
    # Read all lines from stdin
    try:
        if sys.platform == 'win32':
            import msvcrt
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            return '\n'.join(lines)
        else:
            return sys.stdin.read()
    except KeyboardInterrupt:
        print("\nInput cancelled.")
        return None

def main():
    print("Choose input method:")
    print("1. Paste vocabulary")
    print("2. Import from file")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        text = get_multiline_input()
        if text is None:
            return
        
    elif choice == "2":
        filename = input("\nEnter the path to your vocabulary file: ")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found!")
            return
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
    else:
        print("Invalid choice!")
        return
    
    # Parse vocabulary
    vocabulary = parse_vocabulary(text)
    
    if not vocabulary:
        print("Error: No valid vocabulary entries found!")
        return
    
    # Generate HTML
    html_content = generate_html(vocabulary)
    
    if html_content:
        # Write to file
        with open('spanish_wordle.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\nSpanish Wordle game has been created with {len(vocabulary)} vocabulary terms!")
        print("Open 'spanish_wordle.html' in your browser to play.")

if __name__ == "__main__":
    main()