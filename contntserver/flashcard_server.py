from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import random

app = Flask(__name__)
# Configure CORS to allow credentials and restrict to React app origin
CORS(app,
     origins=["http://localhost:3000"],  # Your React app's origin
     supports_credentials=True,           # This is the key setting
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Sample flash card content database
flash_card_database = {
    # Module 1 - Basic Science
    1: {
        "positive": [
            {"front": "What is the powerhouse of the cell?", "back": "The mitochondria is the powerhouse of the cell, producing energy through cellular respiration."},
            {"front": "What are the three states of matter?", "back": "The three states of matter are solid, liquid, and gas."},
            {"front": "What is photosynthesis?", "back": "Photosynthesis is the process where plants convert sunlight into energy."}
        ],
        "neutral": [
            {"front": "Define a cell.", "back": "A cell is the basic structural and functional unit of all living organisms."},
            {"front": "What is an atom?", "back": "An atom is the smallest unit of matter that retains the properties of an element."},
            {"front": "What is gravity?", "back": "Gravity is a force that attracts objects toward each other."}
        ],
        "negative": [
            {"front": "What is the simplest form of life?", "back": "A single cell is the simplest form of life."},
            {"front": "What is energy?", "back": "Energy is the ability to do work or cause change."},
            {"front": "What is matter?", "back": "Matter is anything that has mass and takes up space."}
        ]
    },
    
    # Module 2 - Mathematics
    2: {
        "positive": [
            {"front": "What is 2 + 2?", "back": "2 + 2 = 4"},
            {"front": "What is 5 × 6?", "back": "5 × 6 = 30"},
            {"front": "What is 10 ÷ 2?", "back": "10 ÷ 2 = 5"}
        ],
        "neutral": [
            {"front": "What is addition?", "back": "Addition is combining numbers to find their sum."},
            {"front": "What is multiplication?", "back": "Multiplication is repeated addition."},
            {"front": "What is division?", "back": "Division is sharing a number into equal parts."}
        ],
        "negative": [
            {"front": "What is 1 + 1?", "back": "1 + 1 = 2"},
            {"front": "What is 2 × 1?", "back": "2 × 1 = 2"},
            {"front": "What is 4 ÷ 2?", "back": "4 ÷ 2 = 2"}
        ]
    },
    
    # Module 3 - English Literature
    3: {
        "positive": [
            {"front": "Who wrote 'Romeo and Juliet'?", "back": "William Shakespeare wrote 'Romeo and Juliet'."},
            {"front": "What is a metaphor?", "back": "A metaphor is a figure of speech that compares two things without using 'like' or 'as'."},
            {"front": "What is a simile?", "back": "A simile is a figure of speech that compares two things using 'like' or 'as'."}
        ],
        "neutral": [
            {"front": "What is a noun?", "back": "A noun is a person, place, thing, or idea."},
            {"front": "What is a verb?", "back": "A verb is an action word."},
            {"front": "What is an adjective?", "back": "An adjective describes a noun."}
        ],
        "negative": [
            {"front": "What is a sentence?", "back": "A sentence is a group of words that expresses a complete thought."},
            {"front": "What is a paragraph?", "back": "A paragraph is a group of sentences about one topic."},
            {"front": "What is a story?", "back": "A story is a narrative with characters and events."}
        ]
    },
    
    # Module 4 - History
    4: {
        "positive": [
            {"front": "What is the capital of France?", "back": "Paris is the capital of France."},
            {"front": "Who was the first President of the United States?", "back": "George Washington was the first President of the United States."},
            {"front": "What year did World War II end?", "back": "World War II ended in 1945."}
        ],
        "neutral": [
            {"front": "What is history?", "back": "History is the study of past events and people."},
            {"front": "What is a civilization?", "back": "A civilization is an advanced society with culture and government."},
            {"front": "What is democracy?", "back": "Democracy is a form of government by the people."}
        ],
        "negative": [
            {"front": "What is a country?", "back": "A country is a nation with its own government and borders."},
            {"front": "What is a city?", "back": "A city is a large human settlement."},
            {"front": "What is a government?", "back": "A government is the system that rules a country."}
        ]
    },
    
    # Module 5 - Geography
    5: {
        "positive": [
            {"front": "What is the largest continent?", "back": "Asia is the largest continent."},
            {"front": "What is the longest river in the world?", "back": "The Nile River is the longest river in the world."},
            {"front": "What is the highest mountain?", "back": "Mount Everest is the highest mountain."}
        ],
        "neutral": [
            {"front": "What is geography?", "back": "Geography is the study of Earth's surface and its features."},
            {"front": "What is a continent?", "back": "A continent is a large landmass on Earth."},
            {"front": "What is an ocean?", "back": "An ocean is a large body of saltwater."}
        ],
        "negative": [
            {"front": "What is a map?", "back": "A map is a drawing of Earth's surface."},
            {"front": "What is a globe?", "back": "A globe is a round model of Earth."},
            {"front": "What is a country?", "back": "A country is a nation with its own government."}
        ]
    }
}

def get_sentiment_from_cookie(cookie_value):
    """Extract sentiment from the latestSentiment cookie value"""
    if not cookie_value:
        return "neutral"  # Default sentiment
    
    # Parse the sentiment from the cookie value
    try:
        # Try to parse as JSON first
        sentiment_data = json.loads(cookie_value)
        if isinstance(sentiment_data, dict) and 'sentiment' in sentiment_data:
            sentiment = sentiment_data['sentiment'].lower()
        else:
            sentiment = str(sentiment_data).lower()
    except (json.JSONDecodeError, TypeError):
        # If not JSON, treat as direct text
        sentiment = str(cookie_value).lower()
    
    # Map sentiment to our categories
    if any(word in sentiment for word in ['positive', 'happy', 'joy', 'excited', 'good', 'great']):
        return "positive"
    elif any(word in sentiment for word in ['negative', 'frustrated', 'angry', 'sad', 'bad', 'upset']):
        return "negative"
    else:
        return "neutral"  # Default to neutral for unclear sentiments

@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    """Get flash cards based on module number and sentiment"""
    try:
        # Get parameters from request
        module_number = request.args.get('module', type=int)
        latest_sentiment = request.cookies.get('latestSentiment')
        
        # Validate module number
        if not module_number or module_number not in flash_card_database:
            return jsonify({
                'error': 'Invalid module number',
                'available_modules': list(flash_card_database.keys())
            }), 400
        
        # Get sentiment from cookie
        sentiment = get_sentiment_from_cookie(latest_sentiment)
        
        # Get flash cards for the module and sentiment
        module_cards = flash_card_database[module_number]
        
        if sentiment not in module_cards:
            # Fallback to neutral if sentiment not found
            sentiment = "neutral"
        
        cards = module_cards[sentiment]
        
        # Return 3-5 random cards
        num_cards = min(random.randint(3, 5), len(cards))
        selected_cards = random.sample(cards, num_cards)
        
        return jsonify({
            'module': module_number,
            'sentiment': sentiment,
            'cards': selected_cards,
            'total_cards': len(selected_cards)
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/modules', methods=['GET'])
def get_available_modules():
    """Get list of available modules"""
    return jsonify({
        'modules': list(flash_card_database.keys()),
        'total_modules': len(flash_card_database)
    })

@app.route('/api/sentiment-test', methods=['GET'])
def test_sentiment():
    """Test endpoint to see what sentiment is being detected"""
    latest_sentiment = request.cookies.get('latestSentiment')
    detected_sentiment = get_sentiment_from_cookie(latest_sentiment)
    
    return jsonify({
        'raw_cookie': latest_sentiment,
        'detected_sentiment': detected_sentiment,
        'available_sentiments': ['positive', 'neutral', 'negative']
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Flash card server is running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
