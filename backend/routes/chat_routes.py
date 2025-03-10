from flask import Blueprint, request, jsonify, current_app
from services.openai_service import ask_openai
from services.user_service import get_user_preferences
import logging

chat_bp = Blueprint('chat', __name__)

# System message template with placeholders for user preferences
SYSTEM_MESSAGE_TEMPLATE = """You are a helpful AI assistant specializing in recipes and cooking.
Your goal is to provide helpful, accurate, and creative advice about recipes, cooking techniques, and food.

{dietary_context}

{allergy_context}

{cuisine_preferences}

{cooking_skill}

When responding to users:
1. Use clear, structured formatting with markdown headings (# for titles, ## for sections)
2. Break down complex procedures into numbered steps
3. Use bullet points (- ) for ingredients and lists
4. Bold important information using **text** format
5. Organize information in a logical sequence (ingredients, then preparation, then cooking, then serving)
6. Keep explanations concise but complete
7. Include cooking times, temperatures, and serving sizes when relevant

For recipe responses:
1. Always include a brief introduction explaining the dish
2. Structure recipes with clear sections: ## Ingredients, ## Instructions, ## Tips, ## Nutrition (if available)
3. List ingredients with quantities and preparation notes (e.g., "- 2 cups flour, sifted")
4. Number the steps in the cooking process
5. Add helpful tips at the end for variations or serving suggestions

When suggesting recipe modifications:
1. Be specific about ingredient substitutions (exact measurements when possible)
2. Explain why the substitution works
3. Note any changes to cooking time or temperature
4. Mention how the substitution might affect taste, texture, or appearance

Always prioritize food safety in your recommendations.
"""

@chat_bp.route('/ask', methods=['POST'])
def ask():
    """
    Ask a question to the AI assistant
    
    Expects a JSON with:
    - 'question': The user's question (required)
    - 'user_id': User ID for personalized responses (optional)
    - 'model': The OpenAI model to use (optional, default: gpt-4o-mini)
    - 'context': Additional context for the question (optional)
    
    Returns:
    - AI assistant's response with improved formatting
    """
    current_app.logger.info("Chat ask endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    # Validate question
    question = data.get('question')
    if not question:
        current_app.logger.warning("No question provided in request")
        return jsonify({"success": False, "error": "No question provided"}), 400
    
    # Get optional parameters
    user_id = data.get('user_id')
    model = data.get('model', 'gpt-4o-mini')  # Default to gpt-4o-mini
    context = data.get('context', '')
    
    # Log the parameters
    current_app.logger.info(f"Question: {question}")
    current_app.logger.info(f"Parameters: user_id={user_id}, model={model}")
    
    try:
        # Build system message with user preferences if available
        system_message = build_system_message(user_id)
        
        # Enhance the question with better context and formatting instructions
        enhanced_question = format_question(question, context)
        
        # Get response from OpenAI
        response = ask_openai(
            question=enhanced_question,
            system_message=system_message,
            model=model
        )
        
        current_app.logger.info("Successfully received response from OpenAI")
        
        # Return the response with metadata
        return jsonify({
            "success": True,
            "data": {
                "response": response,
                "model_used": model,
                "personalized": user_id is not None
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error in chat: {str(e)}")
        
        # Try to get a fallback response
        try:
            # Use a simpler question format for the fallback
            fallback_response = ask_openai(
                question=question,
                system_message=SYSTEM_MESSAGE_TEMPLATE.format(
                    dietary_context="",
                    allergy_context="",
                    cuisine_preferences="",
                    cooking_skill=""
                ),
                model="gpt-3.5-turbo"  # Try a different model as fallback
            )
            return jsonify({
                "success": True,
                "data": {
                    "response": fallback_response,
                    "model_used": "gpt-3.5-turbo (fallback)",
                    "personalized": False
                },
                "warning": "Used fallback model due to an error with the primary model"
            })
        except:
            # If all else fails, return the error
            return jsonify({
                "success": False,
                "error": f"Unable to get a response: {str(e)}"
            }), 500

def format_question(question, context=''):
    """
    Format the user's question with additional context to improve the AI response
    
    Args:
        question: The user's original question
        context: Additional context provided in the request
        
    Returns:
        An enhanced question with better context
    """
    # Start with the original question
    formatted_question = question.strip()
    
    # Add context if provided
    if context:
        formatted_question = f"Context: {context}\n\nQuestion: {formatted_question}"
    
    # Determine if this is likely a recipe request
    recipe_keywords = ['recipe', 'how to make', 'how do i make', 'cook', 'prepare', 'ingredients']
    is_recipe_request = any(keyword in formatted_question.lower() for keyword in recipe_keywords)
    
    if is_recipe_request:
        formatted_question += "\n\nPlease provide a complete recipe with ingredients, instructions, and helpful tips. Format your response with clear sections and steps."
    
    # For modification requests
    if 'substitute' in formatted_question.lower() or 'alternative' in formatted_question.lower() or 'instead of' in formatted_question.lower():
        formatted_question += "\n\nPlease explain why the substitution works and how it might affect the recipe."
    
    # For technique questions
    if 'technique' in formatted_question.lower() or 'method' in formatted_question.lower() or 'how do i' in formatted_question.lower():
        formatted_question += "\n\nPlease provide step-by-step instructions with any relevant tips or warnings."
    
    return formatted_question

def build_system_message(user_id=None):
    """
    Build a system message for the AI assistant based on user preferences
    
    Args:
        user_id: The user ID to get preferences for
        
    Returns:
        A system message with user preferences included
    """
    # Default values
    dietary_context = ""
    allergy_context = ""
    cuisine_preferences = ""
    cooking_skill = ""
    
    # Get user preferences if user_id is provided
    if user_id:
        try:
            preferences = get_user_preferences(user_id)
            
            # Build dietary context
            if preferences.get('dietary_restrictions'):
                restrictions = preferences['dietary_restrictions']
                if isinstance(restrictions, list) and restrictions:
                    dietary_context = f"The user follows these dietary restrictions: {', '.join(restrictions)}. "
                    dietary_context += "Please ensure all recommendations comply with these restrictions."
            
            # Build allergy context
            if preferences.get('allergies'):
                allergies = preferences['allergies']
                if isinstance(allergies, list) and allergies:
                    allergy_context = f"The user has allergies to: {', '.join(allergies)}. "
                    allergy_context += "Always avoid these ingredients and be cautious about cross-contamination."
            
            # Build cuisine preferences
            if preferences.get('favorite_cuisines'):
                cuisines = preferences['favorite_cuisines']
                if isinstance(cuisines, list) and cuisines:
                    cuisine_preferences = f"The user enjoys these cuisines: {', '.join(cuisines)}. "
                    cuisine_preferences += "Consider these preferences when suggesting recipes or techniques."
            
            # Build cooking skill level
            if preferences.get('cooking_skill'):
                skill = preferences['cooking_skill']
                if skill:
                    skill_descriptions = {
                        'beginner': "The user is a beginner cook. Provide simple explanations and basic techniques.",
                        'intermediate': "The user has intermediate cooking skills. You can suggest moderately complex techniques.",
                        'advanced': "The user is an advanced cook. Feel free to suggest complex techniques and gourmet recipes."
                    }
                    cooking_skill = skill_descriptions.get(skill.lower(), "")
            
        except Exception as e:
            current_app.logger.error(f"Error getting user preferences: {str(e)}")
            # Continue with default system message if there's an error
    
    # Format the system message with the available context
    system_message = SYSTEM_MESSAGE_TEMPLATE.format(
        dietary_context=dietary_context,
        allergy_context=allergy_context,
        cuisine_preferences=cuisine_preferences,
        cooking_skill=cooking_skill
    )
    
    return system_message

@chat_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for an AI response
    
    Expects a JSON with:
    - 'user_id': User ID (required)
    - 'question': The original question (required)
    - 'response': The AI's response (required)
    - 'rating': Rating from 1-5 (required)
    - 'feedback': Additional feedback text (optional)
    
    Returns:
    - Success message
    """
    current_app.logger.info("Feedback endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    user_id = data.get('user_id')
    question = data.get('question')
    response = data.get('response')
    rating = data.get('rating')
    
    if not all([user_id, question, response, rating]):
        current_app.logger.warning("Missing required fields in request")
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate rating
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            current_app.logger.warning("Invalid rating provided")
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
    except (ValueError, TypeError):
        current_app.logger.warning("Invalid rating format")
        return jsonify({"error": "Rating must be an integer"}), 400
    
    # Get optional feedback text
    feedback_text = data.get('feedback', '')
    
    # Log the feedback
    current_app.logger.info(f"Feedback received from user {user_id}")
    current_app.logger.info(f"Rating: {rating}")
    if feedback_text:
        current_app.logger.info(f"Feedback text: {feedback_text}")
    
    # TODO: Store feedback in database for future analysis
    # For now, just log it
    
    # Return success response
    return jsonify({
        "success": True,
        "message": "Feedback received"
    }) 