import os
import logging
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Using OpenAI API key: {OPENAI_API_KEY[:5]}..." if OPENAI_API_KEY and len(OPENAI_API_KEY) > 5 else "OpenAI API key not found or invalid")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default system message if none provided
DEFAULT_SYSTEM_MESSAGE = """You are a helpful AI assistant specializing in recipes and cooking.
Your goal is to provide helpful, accurate, and creative advice about recipes, cooking techniques, and food.

When responding to users:
1. Use clear, structured formatting with headings (using markdown # for titles, ## for sections)
2. Break down complex procedures into numbered steps
3. Use bullet points (- ) for ingredients and lists
4. Bold important information using **text** format
5. Organize information in a logical sequence (ingredients, then preparation, then cooking, then serving)
6. Keep explanations concise but complete
7. Include cooking times, temperatures, and serving sizes when relevant

When suggesting recipe modifications:
1. Be specific about ingredient substitutions (exact measurements when possible)
2. Explain why the substitution works
3. Note any changes to cooking time or temperature
4. Mention how the substitution might affect taste, texture, or appearance

For recipe responses:
1. Always include a brief introduction explaining the dish
2. Structure recipes with clear sections: Ingredients, Instructions, Tips, Nutrition (if available)
3. List ingredients with quantities and preparation notes (e.g., "2 cups flour, sifted")
4. Number the steps in the cooking process
5. Add helpful tips at the end for variations or serving suggestions

Always prioritize food safety in your recommendations.
"""

def ask_openai(question, system_message=DEFAULT_SYSTEM_MESSAGE, model="gpt-4o-mini"):
    """
    Send a question to OpenAI and get a response.
    
    Args:
        question (str): The user's question
        system_message (str): The system message to set the AI's behavior
        model (str): The OpenAI model to use
    
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

        # Configure the OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Create the messages for the chat completion
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
        
        logger.info(f"Sending request to OpenAI with model: {model}")
        
        # Make the API call
        response = client.chat.completions.create(
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