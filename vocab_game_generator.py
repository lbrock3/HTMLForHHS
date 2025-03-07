#!/usr/bin/env python3

import sys
import os
import re

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
    current_category = ""
    
    for section in sections:
        lines = section.strip().split('\n')
        
        # Skip empty sections
        if not lines:
            continue
            
        # First line of each section is the category
        if lines[0].strip() and not lines[0].strip().startswith(('el ', 'la ', 'los ', 'las ', '¡')):
            current_category = lines[0].strip()
            lines = lines[1:]  # Remove category line
            
        # Process each vocabulary line
        for line in lines:
            if not line.strip() or line.startswith('LEVEL'):  # Skip empty lines and LEVEL headers
                continue
            
            # Clean the line
            line = clean_text(line)
            
            # Split line on equals sign
            parts = line.split('=')
            if len(parts) == 2:
                spanish = parts[0].strip()
                english = parts[1].strip()
                
                # Clean up parenthetical expressions
                spanish = re.sub(r'\s*\(([^)]+)\)', r' (\1)', spanish)
                english = re.sub(r'\s*\(([^)]+)\)', r' (\1)', english)
                
                # Verify we have both parts
                if spanish and english and not spanish.startswith('LEVEL'):
                    vocabulary.append({
                        'spanish': spanish,
                        'english': english,
                        'category': current_category
                    })
    
    return vocabulary

def generate_html(vocabulary):
    vocab_js = "const vocabulary = [\n"
    for item in vocabulary:
        vocab_js += f"    {{ spanish: \"{item['spanish']}\", "
        vocab_js += f"english: \"{item['english']}\", "
        vocab_js += f"category: \"{item['category']}\" }},\n"
    vocab_js += "];"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spanish Vocabulary Game</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f2f5;
            color: #333333;
        }}
        .game-container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
            color: #333333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: normal;
            text-transform: uppercase;
        }}
        .word-display {{
            font-size: 24px;
            margin: 20px 0;
            text-align: center;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            color: #333333;
        }}
        button {{
            background-color: #800020;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-family: 'Poppins', sans-serif;
            transition: background-color 0.2s;
            margin: 5px;
        }}
        button:hover {{
            background-color: #600018;
        }}
        .mode-select {{
            margin: 20px 0;
            text-align: center;
        }}
        .quiz-options {{
            display: none;
            margin: 20px 0;
        }}
        .quiz-option {{
            display: block;
            width: 100%;
            margin: 10px 0;
            padding: 15px;
            text-align: left;
            border: 2px solid #e0e0e0;
            background: #ffffff;
            color: #333333;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
            font-family: 'Poppins', sans-serif;
        }}
        .quiz-option:hover {{
            background: #f8f9fa;
            transform: translateY(-2px);
        }}
        .quiz-option.correct {{
            background: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }}
        .quiz-option.incorrect {{
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }}
        .practice-controls, .quiz-controls {{
            display: none;
            text-align: center;
            margin-top: 20px;
        }}
        .score-display {{
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
            color: #333333;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        .name-input-container {{
            text-align: center;
            margin: 20px 0;
            display: none;
        }}
        
        .name-input {{
            padding: 10px;
            font-size: 16px;
            border: 2px solid #800020;
            border-radius: 6px;
            margin-right: 10px;
            font-family: 'Poppins', sans-serif;
        }}

        .results-screen {{
            text-align: center;
            display: none;
        }}

        .results-screen h2 {{
            font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
            color: #333333;
            margin-bottom: 20px;
        }}

        .results-details {{
            font-size: 1.2em;
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        
        .quiz-setup-container {{
            text-align: center;
            margin: 20px 0;
            display: none;
        }}
        
        .quiz-length-select {{
            margin: 20px 0;
        }}
        
        .quiz-length-select button {{
            margin: 0 10px;
        }}
        
        .name-input {{
            padding: 10px;
            font-size: 16px;
            border: 2px solid #800020;
            border-radius: 6px;
            margin-right: 10px;
            font-family: 'Poppins', sans-serif;
            width: 200px;
        }}

        .language-select {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .language-select button.selected {{
            background-color: #600018;
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="game-container">
        <h1>Spanish Vocabulary Game</h1>
        
        <div class="mode-select">
            <button onclick="setMode('practice')">Practice Mode</button>
            <button onclick="setMode('quiz')">Quiz Mode</button>
        </div>

        <div class="language-select" id="practiceLanguageSelect" style="display: none;">
            <p>Choose your mode:</p>
            <button onclick="setLanguageDirection('spanishToEnglish', 'practice')" id="practiceSpanishBtn">Spanish → English</button>
            <button onclick="setLanguageDirection('englishToSpanish', 'practice')" id="practiceEnglishBtn">English → Spanish</button>
        </div>

        <div class="quiz-setup-container" id="quizSetupContainer">
            <input type="text" class="name-input" id="playerName" placeholder="Enter your name">
            <div class="language-select">
                <p>Choose your mode:</p>
                <button onclick="setLanguageDirection('spanishToEnglish', 'quiz')" id="quizSpanishBtn">Spanish → English</button>
                <button onclick="setLanguageDirection('englishToSpanish', 'quiz')" id="quizEnglishBtn">English → Spanish</button>
            </div>
            <div class="quiz-length-select">
                <p>Select number of questions:</p>
                <button onclick="startQuiz(10)">10 Questions</button>
                <button onclick="startQuiz(20)">20 Questions</button>
                <button onclick="startQuiz('all')">All Terms</button>
            </div>
        </div>

        <div class="word-display" id="wordDisplay"></div>
        
        <div id="practiceControls" class="practice-controls">
            <button onclick="flipWord()">Flip Word</button>
            <button onclick="nextWord()">Next Word</button>
            <div id="practiceProgress" style="margin: 20px 0; text-align: center;"></div>
            <div id="practiceComplete" style="display: none; text-align: center;">
                <p>You've reviewed all the words!</p>
                <button onclick="restartPractice()">Start Over</button>
            </div>
        </div>

        <div id="quizControls" class="quiz-controls">
            <div id="quizOptions" class="quiz-options"></div>
            <div class="score-display">Score: <span id="score">0</span> / <span id="total">0</span></div>
            <button onclick="nextQuiz()" id="nextQuizButton">Next Question</button>
        </div>

        <div class="results-screen" id="resultsScreen">
            <h2>Quiz Complete!</h2>
            <div class="results-details">
                <p>Name: <span id="resultName"></span></p>
                <p>Final Score: <span id="resultScore"></span></p>
                <p>Percentage: <span id="resultPercentage"></span>%</p>
                <p>Completed on: <span id="resultDateTime"></span></p>
                <p>Your High Score: <span id="highScore"></span></p>
                <p id="newHighScore" style="display: none; color: #800020; font-weight: bold;">
                    🎉 New High Score! 🎉
                </p>
            </div>
            <button onclick="setMode('quiz')">Try Again</button>
            <button onclick="setMode('practice')">Practice Mode</button>
        </div>
    </div>

    <script>
    {vocab_js}
    
    let currentIndex = -1;
    let showingSpanish = true;
    let currentMode = 'practice';
    let score = 0;
    let totalQuestions = 0;
    let correctAnswer = '';
    let playerName = '';
    let QUIZ_LENGTH = 10;
    let unusedIndices = [];
    let currentWord = null;
    let languageDirection = 'spanishToEnglish';
    let highScores = {{}};  // Object to store high scores for different quiz lengths

    function shuffleArray(array) {{
        for (let i = array.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }}
        return array;
    }}

    function resetUnusedIndices() {{
        unusedIndices = Array.from(Array(vocabulary.length).keys());
        shuffleArray(unusedIndices);
    }}

    function getRandomIndex() {{
        if (unusedIndices.length === 0) {{
            resetUnusedIndices();
        }}
        return unusedIndices.pop();
    }}

    function getRandomIndices(count, exclude) {{
        let indices = [];
        let tempUnused = unusedIndices.filter(idx => idx !== exclude);
        
        // If we don't have enough unused indices, reset the pool
        if (tempUnused.length < count) {{
            resetUnusedIndices();
            tempUnused = unusedIndices.filter(idx => idx !== exclude);
        }}
        
        // Get random indices for quiz options
        while (indices.length < count && tempUnused.length > 0) {{
            const randomIndex = Math.floor(Math.random() * tempUnused.length);
            indices.push(tempUnused[randomIndex]);
            tempUnused.splice(randomIndex, 1);
        }}
        
        return indices;
    }}

    function setLanguageDirection(direction, mode) {{
        languageDirection = direction;
        showingSpanish = direction === 'spanishToEnglish';
        
        // Update button styles
        const prefix = mode === 'practice' ? 'practice' : 'quiz';
        document.getElementById(`${{prefix}}SpanishBtn`).classList.toggle('selected', direction === 'spanishToEnglish');
        document.getElementById(`${{prefix}}EnglishBtn`).classList.toggle('selected', direction === 'englishToSpanish');
        
        if (mode === 'practice') {{
            nextWord();
        }}
    }}

    function showWord() {{
        currentWord = vocabulary[currentIndex];
        // Show the question language based on direction
        const display = languageDirection === 'spanishToEnglish' ? 
            currentWord.spanish : currentWord.english;
        document.getElementById('wordDisplay').textContent = display;
        updatePracticeProgress();
    }}

    function flipWord() {{
        if (!currentWord) return;
        const currentDisplay = document.getElementById('wordDisplay').textContent;
        // Show the answer language based on direction
        const display = currentDisplay === (languageDirection === 'spanishToEnglish' ? 
            currentWord.spanish : currentWord.english) ?
            (languageDirection === 'spanishToEnglish' ? currentWord.english : currentWord.spanish) :
            (languageDirection === 'spanishToEnglish' ? currentWord.spanish : currentWord.english);
        document.getElementById('wordDisplay').textContent = display;
    }}

    function updatePracticeProgress() {{
        if (currentMode === 'practice') {{
            const remaining = unusedIndices.length;
            const total = vocabulary.length;
            const reviewed = total - remaining;
            document.getElementById('practiceProgress').textContent = 
                `Words reviewed: ${{reviewed}} / ${{total}}`;
            
            // Show or hide the completion message and restart button
            document.getElementById('practiceComplete').style.display = 
                remaining === 0 ? 'block' : 'none';
        }}
    }}

    function restartPractice() {{
        resetUnusedIndices();
        showingSpanish = true;
        nextWord();
        document.getElementById('practiceComplete').style.display = 'none';
    }}

    function nextWord() {{
        if (unusedIndices.length === 0) {{
            document.getElementById('wordDisplay').textContent = "All words reviewed!";
            document.getElementById('practiceComplete').style.display = 'block';
            return;
        }}
        currentIndex = getRandomIndex();
        showingSpanish = true;  // Reset to Spanish for new word
        showWord();
    }}

    function getHighScore(quizLength) {{
        const key = `${{playerName}}_${{quizLength}}`;
        return highScores[key] || 0;
    }}

    function updateHighScore(quizLength, newScore) {{
        const key = `${{playerName}}_${{quizLength}}`;
        const currentHigh = getHighScore(quizLength);
        if (newScore > currentHigh) {{
            highScores[key] = newScore;
            return true;
        }}
        return false;
    }}

    function startQuiz(length) {{
        playerName = document.getElementById('playerName').value.trim();
        if (!playerName) {{
            alert('Please enter your name to start the quiz');
            return;
        }}
        
        // Reset indices and set quiz length
        resetUnusedIndices();
        QUIZ_LENGTH = length === 'all' ? vocabulary.length : length;
        
        document.getElementById('quizSetupContainer').style.display = 'none';
        document.getElementById('quizControls').style.display = 'block';
        document.querySelector('.quiz-options').style.display = 'block';
        score = 0;
        totalQuestions = 0;
        updateScore();
        nextQuiz();
    }}

    function showResults() {{
        const percentage = Math.round((score / QUIZ_LENGTH) * 100);
        const now = new Date();
        const dateString = now.toLocaleDateString();
        const timeString = now.toLocaleTimeString();
        
        const isNewHighScore = updateHighScore(QUIZ_LENGTH, score);
        const highScore = getHighScore(QUIZ_LENGTH);
        
        document.getElementById('resultName').textContent = playerName;
        document.getElementById('resultScore').textContent = `${{score}} out of ${{QUIZ_LENGTH}}`;
        document.getElementById('resultPercentage').textContent = percentage;
        document.getElementById('resultDateTime').textContent = `${{dateString}} at ${{timeString}}`;
        document.getElementById('highScore').textContent = `${{highScore}} out of ${{QUIZ_LENGTH}}`;
        document.getElementById('newHighScore').style.display = isNewHighScore ? 'block' : 'none';
        
        document.getElementById('quizControls').style.display = 'none';
        document.getElementById('wordDisplay').style.display = 'none';
        document.getElementById('resultsScreen').style.display = 'block';
    }}

    function nextQuiz() {{
        if (totalQuestions >= QUIZ_LENGTH) {{
            showResults();
            return;
        }}

        // Get next unused index for the question
        if (unusedIndices.length === 0) {{
            resetUnusedIndices();
        }}
        currentIndex = unusedIndices.pop();
        const word = vocabulary[currentIndex];
        
        const optionsDiv = document.getElementById('quizOptions');
        optionsDiv.innerHTML = '';
        
        // Show question based on language direction
        const questionWord = languageDirection === 'spanishToEnglish' ? word.spanish : word.english;
        correctAnswer = languageDirection === 'spanishToEnglish' ? word.english : word.spanish;
        
        document.getElementById('wordDisplay').textContent = questionWord;
        
        // Get wrong answers, using all available vocabulary if needed
        let options = [correctAnswer];
        let allPossibleAnswers = vocabulary
            .map((item, index) => {{
                return {{
                    answer: languageDirection === 'spanishToEnglish' ? item.english : item.spanish,
                    index: index
                }};
            }})
            .filter(item => 
                item.answer !== correctAnswer && // Not the correct answer
                item.index !== currentIndex      // Not the current word
            );
        
        // Shuffle all possible wrong answers
        shuffleArray(allPossibleAnswers);
        
        // Take the first 3 wrong answers
        let wrongAnswers = allPossibleAnswers.slice(0, 3).map(item => item.answer);
        
        options = options.concat(wrongAnswers);
        shuffleArray(options);
        
        options.forEach(option => {{
            const button = document.createElement('button');
            button.className = 'quiz-option';
            button.textContent = option;
            button.onclick = () => checkAnswer(option);
            optionsDiv.appendChild(button);
        }});
    }}

    function checkAnswer(selected) {{
        totalQuestions++;
        const options = document.querySelectorAll('.quiz-option');
        
        options.forEach(option => {{
            option.disabled = true;
            if (option.textContent === correctAnswer) {{
                option.classList.add('correct');
            }}
            if (option.textContent === selected && selected !== correctAnswer) {{
                option.classList.add('incorrect');
            }}
        }});
        
        if (selected === correctAnswer) {{
            score++;
        }}
        
        updateScore();
    }}

    function updateScore() {{
        document.getElementById('score').textContent = score;
        document.getElementById('total').textContent = totalQuestions;
    }}

    function setMode(mode) {{
        currentMode = mode;
        document.querySelector('.practice-controls').style.display = 'none';
        document.querySelector('.quiz-controls').style.display = 'none';
        document.querySelector('.quiz-options').style.display = 'none';
        document.getElementById('quizSetupContainer').style.display = 'none';
        document.getElementById('resultsScreen').style.display = 'none';
        document.getElementById('practiceLanguageSelect').style.display = 'none';
        document.getElementById('wordDisplay').style.display = 'block';
        document.getElementById('practiceComplete').style.display = 'none';
        
        resetUnusedIndices();
        
        if (mode === 'practice') {{
            document.getElementById('practiceLanguageSelect').style.display = 'block';
            document.querySelector('.practice-controls').style.display = 'block';
            setLanguageDirection('spanishToEnglish', 'practice');
        }} else {{
            document.getElementById('quizSetupContainer').style.display = 'block';
            setLanguageDirection('spanishToEnglish', 'quiz');
        }}
    }}

    // Initialize
    resetUnusedIndices();
    setMode('practice');
    </script>
</body>
</html>'''
    
    return html

def main():
    print("Enter your vocabulary text (press Ctrl+D or Ctrl+Z when finished):")
    text = ""
    try:
        while True:
            line = input()
            text += line + "\n"
    except (EOFError, KeyboardInterrupt):
        pass
    
    # Parse vocabulary
    vocabulary = parse_vocabulary(text)
    
    # Generate HTML
    html = generate_html(vocabulary)
    
    # Write to file
    with open('VocabularyGame.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nVocabularyGame.html has been created with {len(vocabulary)} vocabulary items!")

if __name__ == "__main__":
    main() 