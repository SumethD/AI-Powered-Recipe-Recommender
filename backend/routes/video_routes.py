from flask import Blueprint, request, jsonify, current_app
from services.youtube_service import get_video_transcript
from services.openai_service import transcript_to_recipe
import logging

video_bp = Blueprint('video', __name__)

@video_bp.route('/transcribe', methods=['POST'])
def transcribe_video():
    """
    Transcribe a YouTube video URL
    
    Expects a JSON with:
    - 'youtube_url': URL of the YouTube video (required)
    
    Returns:
    - The video transcript
    """
    current_app.logger.info("Video transcription endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    # Validate YouTube URL
    youtube_url = data.get('youtube_url')
    if not youtube_url:
        current_app.logger.warning("No YouTube URL provided in request")
        return jsonify({"success": False, "error": "No YouTube URL provided"}), 400
    
    # Log the parameters
    current_app.logger.info(f"YouTube URL: {youtube_url}")
    
    # Get transcript
    transcript_result = get_video_transcript(youtube_url)
    
    # Return error if transcription failed
    if not transcript_result.get('success'):
        return jsonify(transcript_result), 400
    
    # Return the transcript
    return jsonify(transcript_result)

@video_bp.route('/to-recipe', methods=['POST'])
def video_to_recipe():
    """
    Convert a YouTube video to a recipe
    
    Expects a JSON with:
    - 'youtube_url': URL of the YouTube video (required)
    - 'model': The OpenAI model to use (optional, default: gpt-4o)
    
    Returns:
    - The extracted recipe
    """
    current_app.logger.info("Video to recipe endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    # Validate YouTube URL
    youtube_url = data.get('youtube_url')
    if not youtube_url:
        current_app.logger.warning("No YouTube URL provided in request")
        return jsonify({"success": False, "error": "No YouTube URL provided"}), 400
    
    # Get optional parameters
    model = data.get('model', 'gpt-4o')  # Default to gpt-4o
    
    # Log the parameters
    current_app.logger.info(f"YouTube URL: {youtube_url}")
    current_app.logger.info(f"Model: {model}")
    
    try:
        # First, get the transcript
        transcript_result = get_video_transcript(youtube_url)
        
        # Return error if transcription failed
        if not transcript_result.get('success'):
            return jsonify(transcript_result), 400
        
        # Get the transcript text
        transcript = transcript_result.get('transcript')
        video_id = transcript_result.get('video_id')
        
        # Convert transcript to recipe
        recipe_result = transcript_to_recipe(transcript, model)
        
        # Add video_id to the result
        if recipe_result.get('success'):
            recipe_result['video_id'] = video_id
            
        # Return the result
        return jsonify(recipe_result)
        
    except Exception as e:
        current_app.logger.error(f"Error in video_to_recipe: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to convert video to recipe: {str(e)}"
        }), 500 