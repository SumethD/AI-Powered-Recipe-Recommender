import os
import logging
from dotenv import load_dotenv
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi
# Handle different versions of youtube-transcript-api
try:
    from youtube_transcript_api import TranscriptNotFoundError, VideoUnavailable
except ImportError:
    # Create fallback exception classes if they don't exist in the installed version
    class TranscriptNotFoundError(Exception):
        """Exception raised when transcript is not found"""
        pass
    
    class VideoUnavailable(Exception):
        """Exception raised when video is unavailable"""
        pass

import re
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

def extract_video_id(youtube_url):
    """
    Extract video ID from various YouTube URL formats
    
    Args:
        youtube_url: URL of the YouTube video
        
    Returns:
        Video ID as string, or None if not a valid YouTube URL
    """
    if not youtube_url:
        return None
    
    parsed_url = urlparse(youtube_url)
    
    # For URLs like https://www.youtube.com/watch?v=VIDEO_ID
    if parsed_url.netloc in ('www.youtube.com', 'youtube.com') and parsed_url.path == '/watch':
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    
    # For URLs like https://youtu.be/VIDEO_ID
    elif parsed_url.netloc == 'youtu.be':
        return parsed_url.path.lstrip('/')
    
    # For URLs like https://www.youtube.com/embed/VIDEO_ID
    elif parsed_url.netloc in ('www.youtube.com', 'youtube.com') and parsed_url.path.startswith('/embed/'):
        return parsed_url.path.split('/embed/')[1]
    
    # Not a recognized YouTube URL format
    return None

def get_video_transcript(youtube_url):
    """
    Get transcript from a YouTube video
    
    Args:
        youtube_url: URL of the YouTube video
        
    Returns:
        Dictionary containing success status, transcript text or error message
        
    Example:
        {'success': True, 'transcript': '...'}
        {'success': False, 'error': 'Invalid URL'}
    """
    try:
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            logger.error(f"Invalid YouTube URL: {youtube_url}")
            return {
                'success': False,
                'error': 'Invalid YouTube URL. Please provide a valid YouTube video URL.'
            }
        
        # Get transcript from YouTube
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine transcript segments into a single text
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        
        # Clean up the transcript (remove excessive spaces, etc.)
        transcript_text = re.sub(r'\s+', ' ', transcript_text).strip()
        
        logger.info(f"Successfully retrieved transcript for video ID: {video_id}")
        return {
            'success': True,
            'transcript': transcript_text,
            'video_id': video_id
        }
        
    except TranscriptNotFoundError:
        logger.error(f"No transcript found for video: {youtube_url}")
        return {
            'success': False,
            'error': 'No transcript found for this video. The video might not have captions available.'
        }
    except VideoUnavailable:
        logger.error(f"Video unavailable: {youtube_url}")
        return {
            'success': False,
            'error': 'The video is unavailable or private.'
        }
    except Exception as e:
        logger.error(f"Error retrieving transcript: {str(e)}")
        return {
            'success': False,
            'error': f'Error retrieving transcript: {str(e)}'
        } 