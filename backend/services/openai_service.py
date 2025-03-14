import os
import logging
import openai
import pkg_resources
from dotenv import load_dotenv
import time
import threading

# Load environment variables
load_dotenv()

# Check OpenAI package version to handle API differences
try:
    openai_version = pkg_resources.get_distribution("openai").version
    is_new_openai = openai_version.startswith(("1.", "2."))
    print(f"Detected OpenAI package version: {openai_version} ({'new API' if is_new_openai else 'legacy API'})")
except Exception as e:
    print(f"Warning: Could not determine OpenAI version: {str(e)}")
    is_new_openai = False

# Configure API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Using OpenAI API key: {OPENAI_API_KEY[:5]}..." if OPENAI_API_KEY and len(OPENAI_API_KEY) > 5 else "OpenAI API key not found or invalid")

# Set up the OpenAI client based on version
if is_new_openai:
    # New OpenAI API (>=1.0.0)
    try:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("Successfully initialized OpenAI client with new API")
    except Exception as e:
        print(f"Error initializing OpenAI client with new API: {str(e)}")
        openai_client = None
else:
    # Legacy OpenAI API (<1.0.0)
    try:
        openai.api_key = OPENAI_API_KEY
        print("Successfully configured OpenAI with legacy API")
    except Exception as e:
        print(f"Error configuring OpenAI with legacy API: {str(e)}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages conversation history for users
    """
    def __init__(self):
        # In-memory storage for conversations
        # In a production environment, this would be a database
        self._conversations = {}
        self.max_conversation_age = 3600  # 1 hour in seconds
        self.max_conversation_messages = 20  # Maximum messages to store per conversation
    
    def add_message(self, conversation_id, message):
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            message: Dict with role and content keys
        """
        if not conversation_id:
            logger.warning("No conversation ID provided, message will not be stored")
            return
        
        # Ensure message has required fields
        if not isinstance(message, dict) or 'role' not in message or 'content' not in message:
            logger.warning("Invalid message format, must be dict with 'role' and 'content' keys")
            return
        
        # Initialize conversation if it doesn't exist
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = {
                'messages': [],
                'last_updated': time.time()
            }
        
        # Add timestamp to message if not already present
        if 'timestamp' not in message:
            message_with_timestamp = message.copy()
            message_with_timestamp['timestamp'] = time.time()
        else:
            message_with_timestamp = message
        
        # Add the message
        self._conversations[conversation_id]['messages'].append(message_with_timestamp)
        self._conversations[conversation_id]['last_updated'] = time.time()
        
        # Truncate if too many messages
        if len(self._conversations[conversation_id]['messages']) > self.max_conversation_messages:
            # Keep the first message (context) and the most recent messages
            truncated = [self._conversations[conversation_id]['messages'][0]]
            truncated.extend(self._conversations[conversation_id]['messages'][-self.max_conversation_messages + 1:])
            self._conversations[conversation_id]['messages'] = truncated
    
    def get_conversation(self, conversation_id):
        """
        Get all messages in a conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message dicts, or empty list if conversation doesn't exist
        """
        if not conversation_id or conversation_id not in self._conversations:
            return []
        
        conversation = self._conversations[conversation_id]
        
        # Check if conversation has expired
        if time.time() - conversation['last_updated'] > self.max_conversation_age:
            logger.info(f"Conversation {conversation_id} has expired, removing")
            del self._conversations[conversation_id]
            return []
        
        return conversation['messages']
    
    def clear_conversation(self, conversation_id):
        """
        Clear all messages in a conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
    
    def cleanup_old_conversations(self):
        """
        Remove conversations that haven't been updated recently
        """
        current_time = time.time()
        expired_ids = [
            conv_id for conv_id, conv_data in self._conversations.items()
            if current_time - conv_data['last_updated'] > self.max_conversation_age
        ]
        
        for conv_id in expired_ids:
            del self._conversations[conv_id]
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired conversations")

# Create a singleton instance of the conversation manager
conversation_manager = ConversationManager()

# Set up periodic cleanup of old conversations
def periodic_cleanup():
    """Run conversation cleanup every hour"""
    while True:
        time.sleep(3600)  # Sleep for 1 hour
        conversation_manager.cleanup_old_conversations()

# Start the cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

# Default system message if none provided
DEFAULT_SYSTEM_MESSAGE = """You are a helpful AI assistant specializing in recipes and cooking.
Your goal is to provide helpful, accurate, and creative advice about recipes, cooking techniques, food, nutrition, and health.

When responding to users:
1. Use clear, structured formatting with headings (using markdown # for titles, ## for sections)
2. Break down complex procedures into numbered steps
3. Use bullet points (- ) for ingredients and lists
4. Bold important information using **text** format
5. Organize information in a logical sequence
6. Keep explanations concise but complete
7. Include relevant metrics and measurements when appropriate

For general questions or advice:
1. Answer directly and comprehensively without assuming the user wants a specific recipe
2. Provide educational content and explain concepts clearly
3. If the question is about techniques or principles, focus on explaining those rather than providing a full recipe
4. Only offer a specific recipe when explicitly requested or when it serves as a helpful example

For nutrition and health questions:
1. Provide evidence-based information about nutrition, foods, and health relationships
2. Explain the nutritional value of foods or ingredients when relevant
3. Offer practical ways to implement health recommendations in everyday cooking
4. Always mention that individual needs vary, and serious health concerns should be discussed with healthcare professionals
5. When discussing nutrients (like sodium, sugar, fat), explain their role in health and how to balance them

For dietary pattern questions (vegan, keto, etc.):
1. Explain the core principles of the dietary pattern
2. List foods that are included and excluded
3. Discuss potential benefits and considerations
4. Provide practical implementation tips

For recipe responses:
1. Always include a brief introduction explaining the dish
2. Structure recipes with clear sections: Ingredients, Instructions, Tips, Nutrition (if available)
3. List ingredients with quantities and preparation notes (e.g., "2 cups flour, sifted")
4. Number the steps in the cooking process
5. Add helpful tips at the end for variations or serving suggestions

When suggesting recipe modifications:
1. Be specific about ingredient substitutions (exact measurements when possible)
2. Explain why the substitution works
3. Note any changes to cooking time or temperature
4. Mention how the substitution might affect taste, texture, or appearance

Always prioritize food safety in your recommendations.
"""

def ask_openai(question, system_message=DEFAULT_SYSTEM_MESSAGE, model="gpt-4o", conversation_history=None):
    """
    Send a question to OpenAI and get a response.
    
    Args:
        question (str): The user's question
        system_message (str): The system message to set the AI's behavior
        model (str): The OpenAI model to use
        conversation_history (list): Optional list of previous messages in the conversation
        
    Returns:
        str: The AI's response with improved formatting
    """
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            logger.error("OpenAI API key not found or is the default placeholder")
            return """I'm currently unable to connect to the OpenAI service. Please make sure you've set up a valid OpenAI API key in the .env file.

# Simple Pasta with Tomato Sauce

A quick and easy pasta dish that's perfect for a weeknight dinner. This classic recipe takes about 20 minutes to prepare.

## Ingredients:
- 8 oz pasta (spaghetti, penne, or your favorite shape)
- 2 tablespoons olive oil
- 3 cloves garlic, minced
- 1 can (14 oz) crushed tomatoes
- 1 teaspoon dried basil
- 1/2 teaspoon dried oregano
- Salt and pepper to taste
- Grated Parmesan cheese for serving

## Instructions:
1. Bring a large pot of salted water to a boil. Add pasta and cook according to package directions until al dente.
2. While pasta is cooking, heat olive oil in a saucepan over medium heat.
3. Add minced garlic and sauté for 30 seconds until fragrant.
4. Add crushed tomatoes, dried basil, and oregano. Stir to combine.
5. Simmer the sauce for 10 minutes, stirring occasionally.
6. Season with salt and pepper to taste.
7. Drain the pasta and return it to the pot.
8. Pour the sauce over the pasta and toss to coat.
9. Serve hot with grated Parmesan cheese on top.

## Tips:
- For a spicier version, add 1/4 teaspoon of red pepper flakes with the garlic.
- Fresh herbs can be substituted for dried (use 1 tablespoon fresh basil and 1 teaspoon fresh oregano).
- Add cooked ground beef or Italian sausage for a heartier meal.
"""

        # Start with the system message
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history if provided
        if conversation_history and isinstance(conversation_history, list):
            # Filter out any system messages from history - we already added our own
            history_messages = [msg for msg in conversation_history if msg.get('role') != 'system']
            messages.extend(history_messages)
            
            # Log the conversation length
            logger.info(f"Including conversation history with {len(history_messages)} messages")
            
            # Check for token count (approximate)
            total_chars = sum(len(msg.get('content', '')) for msg in messages)
            if total_chars > 12000:  # Rough estimate, ~4 chars per token, ~3000 tokens limit
                logger.warning(f"Conversation history may be too long: ~{total_chars} chars")
                # We'll keep the most recent messages if needed
                # This is a simple approach - a more sophisticated one would count tokens properly
                if len(history_messages) > 4:
                    # Keep the earliest messages for context, then most recent ones
                    most_recent = history_messages[-4:]
                    messages = [messages[0]]  # system message
                    messages.extend(most_recent)
                    logger.info(f"Truncated conversation to {len(messages)-1} messages to avoid token limits")
        
        # Add the current question
        messages.append({"role": "user", "content": question})
        
        logger.info(f"Sending request to OpenAI with model: {model}")
        
        # Make the API call based on OpenAI version
        if is_new_openai and openai_client:
            # New OpenAI API (>=1.0.0)
            response = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            # Extract the response text
            response_text = response.choices[0].message.content
        else:
            # Legacy OpenAI API (<1.0.0)
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            # Extract the response text from legacy format
            response_text = response['choices'][0]['message']['content']
        
        # Post-process the response for better formatting
        formatted_response = post_process_response(response_text)
        
        logger.info("Successfully received and processed response from OpenAI")
        return formatted_response
        
    except Exception as e:
        logger.error(f"Error in ask_openai: {str(e)}")
        raise

def post_process_response(text):
    """
    Post-process the OpenAI response to improve formatting and readability
    
    Args:
        text (str): The raw response from OpenAI
        
    Returns:
        str: The formatted response
    """
    # Ensure proper markdown heading formatting
    # Replace headings without proper spacing
    for i in range(3, 0, -1):  # Start with h3 to avoid replacing parts of larger headings
        hashes = '#' * i
        text = text.replace(f"{hashes}(\\w)", f"{hashes} \\1")
    
    # Ensure ingredient lists use bullet points
    if "## Ingredients:" in text or "## Ingredients" in text:
        lines = text.split('\n')
        in_ingredients = False
        for i, line in enumerate(lines):
            if line.startswith("## Ingredients"):
                in_ingredients = True
                continue
            if in_ingredients and line.strip() and not line.startswith("-") and not line.startswith("##"):
                # This is an ingredient line without a bullet point
                if ":" in line or line[0].isdigit():  # Likely an ingredient with quantity
                    lines[i] = f"- {line}"
            if in_ingredients and (line.startswith("##") or not line.strip()):
                in_ingredients = False
        text = '\n'.join(lines)
    
    # Ensure instruction steps are numbered
    if "## Instructions:" in text or "## Instructions" in text:
        lines = text.split('\n')
        in_instructions = False
        step_number = 1
        for i, line in enumerate(lines):
            if line.startswith("## Instructions"):
                in_instructions = True
                continue
            if in_instructions and line.strip() and not line.startswith("1.") and not line.startswith("##"):
                # This is an instruction line without numbering
                if not any(line.startswith(f"{j}.") for j in range(1, 20)):  # Not already numbered
                    lines[i] = f"{step_number}. {line}"
                    step_number += 1
            if in_instructions and (line.startswith("##") or not line.strip()):
                in_instructions = False
        text = '\n'.join(lines)
    
    # Add spacing between sections for better readability
    text = text.replace("##", "\n##")
    
    # Remove any double blank lines
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    
    return text

def get_recipe_modification(recipe_details, modification_type, user_preferences=None):
    """
    Get suggestions for modifying a recipe based on specific requirements
    
    Args:
        recipe_details: Dictionary containing recipe information
        modification_type: Type of modification (e.g., 'healthier', 'vegetarian', 'low-carb')
        user_preferences: Optional user preferences to include in the request
        
    Returns:
        Modification suggestions as a string
    """
    # Extract relevant recipe information
    recipe_name = recipe_details.get('title', 'Unknown Recipe')
    ingredients = recipe_details.get('extendedIngredients', [])
    ingredient_list = [f"{ing.get('amount', '')} {ing.get('unit', '')} {ing.get('name', '')}" 
                      for ing in ingredients if ing.get('name')]
    
    instructions = recipe_details.get('instructions', 'No instructions available')
    
    # Build the prompt
    prompt = f"""I have a recipe for "{recipe_name}" with the following ingredients:
{', '.join(ingredient_list)}

Instructions: {instructions}

How can I modify this recipe to make it {modification_type}? Please provide specific substitutions and changes to the cooking method if needed.
"""
    
    # Add user preferences context if available
    if user_preferences:
        context = "Consider these preferences: "
        if user_preferences.get('dietary_restrictions'):
            context += f"Dietary restrictions: {', '.join(user_preferences['dietary_restrictions'])}. "
        if user_preferences.get('allergies'):
            context += f"Allergies: {', '.join(user_preferences['allergies'])}. "
        prompt = context + "\n\n" + prompt
    
    # Get response from OpenAI
    system_message = """You are a culinary expert specializing in recipe modifications.
Provide detailed, practical advice for modifying recipes to meet specific dietary needs or preferences.
Be specific about ingredient substitutions with exact measurements when possible.
Explain why each substitution works and how it might affect the final dish.
"""
    
    return ask_openai(prompt, system_message=system_message)

def get_culinary_advice(question):
    """
    Get culinary advice from OpenAI
    
    Args:
        question: The culinary question to ask
        
    Returns:
        The AI's response as a string
    """
    return ask_openai(question)

def transcript_to_recipe(transcript, model="gpt-4o"):
    """
    Convert a video transcript to a structured recipe format using OpenAI
    
    Args:
        transcript (str): The transcript text from a cooking video
        model (str): The OpenAI model to use
        
    Returns:
        str: A structured recipe with ingredients, instructions, and tips
    """
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            logger.error("OpenAI API key not found or is the default placeholder")
            return {
                'success': False,
                'error': 'OpenAI API key not configured. Please set up a valid OpenAI API key in the .env file.'
            }

        # Create the system message specifically for recipe extraction
        system_message = """You are a professional culinary assistant that specializes in extracting and formatting recipes from video transcripts. 
Your task is to analyze the transcript and create a well-structured, detailed recipe.

Follow these guidelines:
1. Extract the recipe title, ingredients with quantities, and cooking steps.
2. Format the recipe with clear headings using markdown (# for title, ## for sections).
3. List all ingredients with measurements using bullet points (- ).
4. Number the cooking steps clearly.
5. Include preparation time, cooking time, and servings if mentioned.
6. Add a brief introduction describing the dish.
7. Include any tips, variations, or storage instructions mentioned.
8. If the transcript has unclear or missing information, make reasonable inferences but mark them as [Estimated].
9. If the transcript doesn't contain a recipe or is unrelated to cooking, respond with "No recipe found in this video."
10. Calculate and include nutritional information per serving based on the ingredients and quantities.

Format your response as follows:
# [Recipe Title]

[Brief introduction about the dish]

## Preparation Time
- Prep: [time]
- Cook: [time]
- Total: [time]
- Servings: [number]

## Ingredients
- [quantity] [ingredient]
- [quantity] [ingredient]
...

## Instructions
1. [Step one]
2. [Step two]
...

## Nutritional Information (per serving)
- Calories: [value] kcal
- Protein: [value] g
- Carbohydrates: [value] g
- Fat: [value] g
- Fiber: [value] g
- Sugar: [value] g
- Sodium: [value] mg

## Tips (if any)
- [Tip one]
- [Tip two]
...

## Storage Instructions (if mentioned)
[Storage information]
"""

        # Create the user message prompt with the transcript
        user_message = f"""Please extract a complete recipe from the following cooking video transcript:

{transcript}

Please format the response as a complete recipe with all details mentioned in the transcript. Make sure to include nutritional information per serving based on the ingredients and their quantities."""

        # Create the messages for the chat completion
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        logger.info(f"Sending transcript to OpenAI for recipe extraction with model: {model}")
        
        # Make the API call based on OpenAI version
        try:
            if is_new_openai and openai_client:
                # New OpenAI API (>=1.0.0)
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                # Extract the response text
                recipe_text = response.choices[0].message.content
            else:
                # Legacy OpenAI API (<1.0.0)
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.5,
                    max_tokens=2000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                # Extract the response text from legacy format
                recipe_text = response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {
                'success': False,
                'error': f'Error calling OpenAI API: {str(e)}'
            }
        
        # Check if no recipe was found
        if "No recipe found in this video" in recipe_text:
            return {
                'success': False,
                'error': 'No recipe could be extracted from this video.'
            }
        
        logger.info("Successfully extracted recipe from transcript")
        return {
            'success': True,
            'recipe': recipe_text
        }
        
    except Exception as e:
        logger.error(f"Error in transcript_to_recipe: {str(e)}")
        return {
            'success': False,
            'error': f'Error processing transcript: {str(e)}'
        } 