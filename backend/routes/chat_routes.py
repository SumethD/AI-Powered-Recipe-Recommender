from flask import Blueprint, request, jsonify, current_app
from services.openai_service import ask_openai, conversation_manager
from services.user_service import get_user_preferences
import logging
import uuid
import time

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

For general questions or advice:
1. Answer directly and comprehensively without assuming the user wants a specific recipe
2. Provide educational content and explain concepts clearly
3. If the question is about techniques or principles, focus on explaining those rather than providing a full recipe
4. Only offer a specific recipe when explicitly requested or when it serves as a helpful example

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
    - 'model': The OpenAI model to use (optional, default: gpt-4o)
    - 'context': Additional context for the question (optional)
    - 'conversation_id': ID to maintain conversation continuity (optional)
    - 'clear_conversation': Boolean to clear conversation history (optional)
    
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
    context = data.get('context', '')
    system_message = data.get('system_message', '')
    model = data.get('model', 'gpt-4o')  # Default to gpt-4o
    
    # Get or create conversation ID
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        # Generate a unique ID if none provided
        conversation_id = f"conv_{str(uuid.uuid4())}"
        current_app.logger.info(f"Created new conversation ID: {conversation_id}")
    else:
        current_app.logger.info(f"Using existing conversation ID: {conversation_id}")
    
    # Check if we should clear conversation history
    if data.get('clear_conversation'):
        conversation_manager.clear_conversation(conversation_id)
        current_app.logger.info(f"Cleared conversation history for {conversation_id}")
    
    # Log the parameters
    current_app.logger.info(f"Question: {question}")
    current_app.logger.info(f"Parameters: user_id={user_id}, model={model}, conversation_id={conversation_id}")
    
    try:
        # Build system message with user preferences if available
        system_message = build_system_message(user_id)
        
        # Get conversation history
        conversation_history = conversation_manager.get_conversation(conversation_id)
        
        # Enhance the question with better context and formatting instructions
        enhanced_question = format_question(question, context)
        
        # Log the enhanced question for debugging
        current_app.logger.info(f"Enhanced question: {enhanced_question}")
        
        # Add user message to conversation history
        conversation_manager.add_message(conversation_id, {
            "role": "user",
            "content": enhanced_question
        })
        
        # Get response from OpenAI, including conversation history
        response = ask_openai(
            question=enhanced_question,
            system_message=system_message,
            model=model,
            conversation_history=conversation_history
        )
        
        # Add assistant response to conversation history
        conversation_manager.add_message(conversation_id, {
            "role": "assistant",
            "content": response
        })
        
        # Periodically clean up old conversations
        if time.time() % 10 < 1:  # ~10% chance to run cleanup on each request
            conversation_manager.cleanup_old_conversations()
        
        current_app.logger.info("Successfully received response from OpenAI")
        
        # Return the response with metadata
        return jsonify({
            "success": True,
            "data": {
                "response": response,
                "model_used": model,
                "personalized": user_id is not None,
                "conversation_id": conversation_id
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
            
            # Still add the fallback response to conversation history
            conversation_manager.add_message(conversation_id, {
                "role": "assistant",
                "content": fallback_response
            })
            
            return jsonify({
                "success": True,
                "data": {
                    "response": fallback_response,
                    "model_used": "gpt-3.5-turbo (fallback)",
                    "personalized": False,
                    "conversation_id": conversation_id
                },
                "warning": "Used fallback model due to an error with the primary model"
            })
        except:
            # If all else fails, return the error
            return jsonify({
                "success": False,
                "error": f"Unable to get a response: {str(e)}",
                "conversation_id": conversation_id
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
    
    # Determine question type for better classification
    general_advice_keywords = [
        'how can i', 'what are ways to', 'tips for', 'advice', 'recommend', 'suggestion',
        'benefits', 'healthy', 'nutrition', 'nutrients', 'reduce', 'increase', 'lower',
        'diet', 'alternative', 'substitute', 'instead of', 'avoid', 'without'
    ]
    recipe_keywords = [
        'recipe for', 'how to make', 'how do i make', 'ingredients for', 'how to cook',
        'how to prepare', 'recipe using', 'recipe with'
    ]
    modification_keywords = ['substitute', 'alternative', 'instead of', 'replace', 'modification']
    technique_keywords = ['technique', 'method', 'how do i', 'process', 'best way to']
    health_keywords = [
        'calories', 'protein', 'fat', 'carbs', 'sodium', 'sugar', 'cholesterol', 'weight', 'diet',
        'nutrition', 'nutrient', 'vitamin', 'mineral', 'fiber', 'antioxidant', 'health', 'healthy',
        'heart', 'diabetes', 'blood pressure', 'low-fat', 'low-carb', 'low-sodium', 'gluten',
        'keto', 'paleo', 'vegan', 'vegetarian'
    ]
    
    # More specific categories
    nutrient_reduction_keywords = ['reduce', 'lower', 'decrease', 'cut', 'less', 'without', 'low']
    nutrient_increase_keywords = ['increase', 'boost', 'more', 'higher', 'rich in', 'good source']
    specific_nutrients = [
        'sodium', 'salt', 'sugar', 'fat', 'carbs', 'carbohydrates', 'protein', 'fiber', 
        'calcium', 'iron', 'potassium', 'zinc', 'vitamin', 'magnesium', 'cholesterol'
    ]
    specific_diets = [
        'keto', 'paleo', 'vegan', 'vegetarian', 'pescatarian', 'mediterranean', 
        'dash', 'gluten-free', 'dairy-free', 'low fodmap', 'whole30'
    ]
    
    # Check for specific question types
    is_explicit_recipe_request = any(keyword in formatted_question.lower() for keyword in recipe_keywords)
    is_general_advice = any(keyword in formatted_question.lower() for keyword in general_advice_keywords)
    is_health_related = any(keyword in formatted_question.lower() for keyword in health_keywords)
    is_technique_question = any(keyword in formatted_question.lower() for keyword in technique_keywords)
    
    # Specific nutrient/health categorization
    is_nutrient_reduction = any(keyword in formatted_question.lower() for keyword in nutrient_reduction_keywords)
    is_nutrient_increase = any(keyword in formatted_question.lower() for keyword in nutrient_increase_keywords)
    mentioned_nutrients = [nutrient for nutrient in specific_nutrients if nutrient in formatted_question.lower()]
    mentioned_diets = [diet for diet in specific_diets if diet in formatted_question.lower()]
    
    # Log the question classification
    logger = logging.getLogger(__name__)
    logger.info(f"Question classification: explicit_recipe={is_explicit_recipe_request}, general_advice={is_general_advice}, health_related={is_health_related}")
    if mentioned_nutrients:
        logger.info(f"Mentioned nutrients: {', '.join(mentioned_nutrients)}")
    if mentioned_diets:
        logger.info(f"Mentioned diets: {', '.join(mentioned_diets)}")
    
    # Handle nutrition and health-related questions
    if is_health_related and not is_explicit_recipe_request:
        logger.info("Applying health/nutrition specific formatting")
        
        # Nutrient reduction questions (like reducing sodium, sugar, fat, etc.)
        if is_nutrient_reduction and mentioned_nutrients:
            nutrient_list = ', '.join(mentioned_nutrients)
            logger.info(f"Applying nutrient reduction advice for: {nutrient_list}")
            formatted_question += f"""
            
Please provide comprehensive advice on reducing {nutrient_list} in food and cooking. Include:
1. General principles for reducing {nutrient_list}
2. Specific techniques and flavor-enhancing alternatives
3. List of substitute ingredients or cooking methods
4. Brief examples of how to apply these principles

The user is looking for practical, educational content about {nutrient_list} reduction, not a complete recipe. Only include brief recipe examples if they effectively demonstrate important principles."""
        
        # Nutrient increase questions (like boosting protein, fiber, etc.)
        elif is_nutrient_increase and mentioned_nutrients:
            nutrient_list = ', '.join(mentioned_nutrients)
            logger.info(f"Applying nutrient increase advice for: {nutrient_list}")
            formatted_question += f"""
            
Please provide comprehensive advice on increasing {nutrient_list} in food and cooking. Include:
1. General principles for incorporating more {nutrient_list} in meals
2. List of foods that are rich in {nutrient_list}
3. Practical cooking and meal planning strategies
4. Brief examples of how to apply these principles

The user is looking for practical, educational content about increasing {nutrient_list}, not a complete recipe. Only include brief recipe examples if they effectively demonstrate important principles."""
        
        # Specific diet questions
        elif mentioned_diets:
            diet_list = ', '.join(mentioned_diets)
            logger.info(f"Applying specific diet advice for: {diet_list}")
            formatted_question += f"""
            
Please provide comprehensive information about the {diet_list} diet or eating pattern. Include:
1. Key principles and guidelines of this eating pattern
2. Foods to include and avoid
3. Potential health benefits and considerations
4. Practical tips for following this eating pattern

The user is looking for educational content about {diet_list} eating, not a complete recipe. Only include brief recipe examples if they effectively demonstrate important principles."""
        
        # General health/nutrition questions
        else:
            logger.info("Applying general health/nutrition advice formatting")
            formatted_question += """
            
Please provide comprehensive, evidence-based nutrition or health information on this topic. Include:
1. Clear explanation of key concepts and principles
2. Practical guidance that can be applied in everyday cooking and eating
3. Context for why this information is important for health
4. Brief examples to illustrate the concepts

The user is looking for educational content, not a complete recipe. Only include brief recipe examples if they effectively demonstrate important principles."""
    
    # For general advice questions that aren't explicitly health-related
    elif is_general_advice and not is_explicit_recipe_request:
        logger.info("Applying general advice formatting")
        formatted_question += "\n\nPlease provide comprehensive advice on this topic. Focus on explaining principles and techniques rather than giving a specific recipe unless it's necessary as a brief example. The user is looking for general guidance, not a complete recipe."
    
    # For explicit recipe requests
    elif is_explicit_recipe_request:
        logger.info("Applying recipe request formatting")
        formatted_question += "\n\nPlease provide a complete recipe with ingredients, instructions, and helpful tips. Format your response with clear sections and steps."
    
    # For modification requests
    if any(keyword in formatted_question.lower() for keyword in modification_keywords):
        logger.info("Adding modification request guidance")
        formatted_question += "\n\nPlease explain why the substitution works and how it might affect the recipe."
    
    # For technique questions
    if is_technique_question:
        logger.info("Adding technique question guidance")
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

@chat_bp.route('/test-classification', methods=['POST'])
def test_classification():
    """
    Test endpoint to see how a question would be classified and formatted
    without actually sending it to the OpenAI API
    
    Expects a JSON with:
    - 'question': The user's question (required)
    - 'context': Additional context for the question (optional)
    
    Returns:
    - The classification and formatted question
    """
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    # Validate question
    question = data.get('question')
    if not question:
        return jsonify({"success": False, "error": "No question provided"}), 400
    
    # Get optional parameters
    context = data.get('context', '')
    
    # Enhance the question with better context and formatting instructions
    formatted_question = format_question(question, context)
    
    # Analyze the question using the same keywords as in format_question
    general_advice_keywords = [
        'how can i', 'what are ways to', 'tips for', 'advice', 'recommend', 'suggestion',
        'benefits', 'healthy', 'nutrition', 'nutrients', 'reduce', 'increase', 'lower',
        'diet', 'alternative', 'substitute', 'instead of', 'avoid', 'without'
    ]
    recipe_keywords = [
        'recipe for', 'how to make', 'how do i make', 'ingredients for', 'how to cook',
        'how to prepare', 'recipe using', 'recipe with'
    ]
    modification_keywords = ['substitute', 'alternative', 'instead of', 'replace', 'modification']
    technique_keywords = ['technique', 'method', 'how do i', 'process', 'best way to']
    health_keywords = [
        'calories', 'protein', 'fat', 'carbs', 'sodium', 'sugar', 'cholesterol', 'weight', 'diet',
        'nutrition', 'nutrient', 'vitamin', 'mineral', 'fiber', 'antioxidant', 'health', 'healthy',
        'heart', 'diabetes', 'blood pressure', 'low-fat', 'low-carb', 'low-sodium', 'gluten',
        'keto', 'paleo', 'vegan', 'vegetarian'
    ]
    
    # More specific categories
    nutrient_reduction_keywords = ['reduce', 'lower', 'decrease', 'cut', 'less', 'without', 'low']
    nutrient_increase_keywords = ['increase', 'boost', 'more', 'higher', 'rich in', 'good source']
    specific_nutrients = [
        'sodium', 'salt', 'sugar', 'fat', 'carbs', 'carbohydrates', 'protein', 'fiber', 
        'calcium', 'iron', 'potassium', 'zinc', 'vitamin', 'magnesium', 'cholesterol'
    ]
    specific_diets = [
        'keto', 'paleo', 'vegan', 'vegetarian', 'pescatarian', 'mediterranean', 
        'dash', 'gluten-free', 'dairy-free', 'low fodmap', 'whole30'
    ]
    
    # Check for specific question types
    is_explicit_recipe_request = any(keyword in question.lower() for keyword in recipe_keywords)
    is_general_advice = any(keyword in question.lower() for keyword in general_advice_keywords)
    is_health_related = any(keyword in question.lower() for keyword in health_keywords)
    is_technique_question = any(keyword in question.lower() for keyword in technique_keywords)
    is_modification_question = any(keyword in question.lower() for keyword in modification_keywords)
    
    # Specific nutrient/health categorization
    is_nutrient_reduction = any(keyword in question.lower() for keyword in nutrient_reduction_keywords)
    is_nutrient_increase = any(keyword in question.lower() for keyword in nutrient_increase_keywords)
    mentioned_nutrients = [nutrient for nutrient in specific_nutrients if nutrient in question.lower()]
    mentioned_diets = [diet for diet in specific_diets if diet in question.lower()]
    
    # Return the classification and formatted question
    return jsonify({
        "success": True,
        "classification": {
            "explicit_recipe_request": is_explicit_recipe_request,
            "general_advice": is_general_advice,
            "health_related": is_health_related,
            "technique_question": is_technique_question,
            "modification_question": is_modification_question,
            "nutrient_reduction": is_nutrient_reduction,
            "nutrient_increase": is_nutrient_increase,
            "mentioned_nutrients": mentioned_nutrients,
            "mentioned_diets": mentioned_diets,
            "matched_keywords": {
                "general_advice": [kw for kw in general_advice_keywords if kw in question.lower()],
                "recipe": [kw for kw in recipe_keywords if kw in question.lower()],
                "modification": [kw for kw in modification_keywords if kw in question.lower()],
                "technique": [kw for kw in technique_keywords if kw in question.lower()],
                "health": [kw for kw in health_keywords if kw in question.lower()],
                "nutrient_reduction": [kw for kw in nutrient_reduction_keywords if kw in question.lower()],
                "nutrient_increase": [kw for kw in nutrient_increase_keywords if kw in question.lower()]
            }
        },
        "formatted_question": formatted_question
    })

@chat_bp.route('/conversation', methods=['POST'])
def manage_conversation():
    """
    Manage a conversation - view history, clear, or get summary
    
    Expects a JSON with:
    - 'conversation_id': ID of the conversation to manage (required)
    - 'action': Action to perform (optional, default: 'view')
      - 'view': Get the conversation history
      - 'clear': Clear the conversation history
      - 'summarize': Get a summary of the conversation
    
    Returns:
    - Success status and requested data
    """
    current_app.logger.info("Conversation management endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    # Validate conversation ID
    conversation_id = data.get('conversation_id')
    if not conversation_id:
        current_app.logger.warning("No conversation ID provided")
        return jsonify({"success": False, "error": "No conversation ID provided"}), 400
    
    # Get action (default to 'view')
    action = data.get('action', 'view').lower()
    
    # Handle different actions
    if action == 'view':
        # Get conversation history
        messages = conversation_manager.get_conversation(conversation_id)
        
        # Format for easier reading
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'role': msg.get('role', ''),
                'content': msg.get('content', ''),
                'timestamp': msg.get('timestamp', None)
            })
        
        return jsonify({
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "messages": formatted_messages
            }
        })
    
    elif action == 'clear':
        # Clear conversation history
        conversation_manager.clear_conversation(conversation_id)
        current_app.logger.info(f"Cleared conversation {conversation_id}")
        
        return jsonify({
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "message": "Conversation history cleared"
            }
        })
    
    elif action == 'summarize':
        # Get conversation history
        messages = conversation_manager.get_conversation(conversation_id)
        
        if not messages:
            return jsonify({
                "success": False,
                "error": "No conversation history found"
            }), 404
        
        try:
            # Create a summary prompt
            summary_prompt = "Please provide a brief summary of our conversation so far. Focus on the main topics we've discussed and any important information shared."
            
            # Get summary from OpenAI
            summary = ask_openai(
                question=summary_prompt,
                conversation_history=messages,
                model="gpt-3.5-turbo"  # Use a smaller model for summaries to save costs
            )
            
            return jsonify({
                "success": True,
                "data": {
                    "conversation_id": conversation_id,
                    "message_count": len(messages),
                    "summary": summary
                }
            })
        except Exception as e:
            current_app.logger.error(f"Error generating conversation summary: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Error generating conversation summary: {str(e)}"
            }), 500
    
    else:
        # Invalid action
        return jsonify({
            "success": False,
            "error": f"Invalid action: {action}"
        }), 400 