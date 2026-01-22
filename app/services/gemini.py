import os
from typing import Dict, Any, Optional, List

from app.core.config import settings


def generate_social_content(
    business_info: Dict[str, Any],
    mode: str,
    prompt: str,
    assets: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate social media content using Gemini AI (Nano Banana / Gemini 2.5 Flash Image).

    Args:
        business_info: Business profile information
        mode: "image" or "video"
        prompt: User prompt for content generation
        assets: Optional list of uploaded asset files

    Returns:
        Dict containing generated content with title, caption, hashtags, and generation prompt
    """
    if not settings.GEMINI_API_KEY:
        # Return mock data if no API key is configured
        return {
            "mode": mode,
            "provider": "nano-banana",
            "title": f"Amazing {business_info.get('name', 'Business')} Content",
            "caption": f"Check out this incredible {mode} for {business_info.get('name', 'our business')}! {prompt}",
            "hashtags": "#Business #Content #SocialMedia",
            "generation_prompt": f"Create a {mode} showing: {prompt}. Business: {business_info.get('name', 'Unknown')}, Industry: {business_info.get('industry', 'General')}",
            "notes": "This is mock data. Configure GEMINI_API_KEY to enable real AI generation."
        }

    try:
        import google.generativeai as genai

        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Use Gemini text model for content planning and optimization
        model = genai.GenerativeModel(settings.GEMINI_TEXT_MODEL)

        # Build context from business info and assets
        business_context = f"""
        Business Name: {business_info.get('name', 'Unknown')}
        Industry: {business_info.get('industry', 'General')}
        Description: {business_info.get('description', 'No description provided')}
        Target Audience: {business_info.get('target_audience', 'General audience')}
        Brand Tone: {business_info.get('brand_tone', 'Professional')}
        Primary Products: {business_info.get('primary_products', 'Various products/services')}
        """

        asset_info = ""
        if assets:
            asset_info = f"\nAvailable Assets: {len(assets)} uploaded files for reference"

        # Create comprehensive prompt for Gemini
        planning_prompt = f"""
        You are a social media content strategist. Create optimized {mode} content for this business.

        BUSINESS CONTEXT:
        {business_context}
        {asset_info}

        USER REQUEST: {prompt}

        TASK: Generate a complete social media {mode} concept including:
        1. Catchy title (under 60 characters)
        2. Engaging caption (under 2200 characters, suitable for {mode})
        3. Relevant hashtags (5-10 hashtags)
        4. Detailed generation prompt for AI image/video creation (be very specific about style, colors, composition, mood, and {mode}-specific details)

        Make the content authentic to the business brand and optimized for social media engagement.
        """

        # Generate content plan using Gemini Flash
        response = model.generate_content(planning_prompt)
        content_plan = response.text

        # Parse the response to extract components
        # This is a simple parsing - in production, you might want more sophisticated parsing
        lines = content_plan.split('\n')
        title = ""
        caption = ""
        hashtags = ""
        generation_prompt = ""

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith('title:') or line.lower().startswith('1.'):
                current_section = 'title'
                title = line.split(':', 1)[1].strip() if ':' in line else line
            elif line.lower().startswith('caption:') or line.lower().startswith('2.'):
                current_section = 'caption'
                caption = line.split(':', 1)[1].strip() if ':' in line else line
            elif line.lower().startswith('hashtags:') or line.lower().startswith('3.'):
                current_section = 'hashtags'
                hashtags = line.split(':', 1)[1].strip() if ':' in line else line
            elif line.lower().startswith('generation prompt:') or line.lower().startswith('4.') or line.lower().startswith('detailed generation prompt'):
                current_section = 'generation'
                generation_prompt = line.split(':', 1)[1].strip() if ':' in line else line
            elif current_section:
                if current_section == 'title' and len(title) < 60:
                    title += ' ' + line
                elif current_section == 'caption' and len(caption) < 2200:
                    caption += ' ' + line
                elif current_section == 'hashtags':
                    hashtags += ' ' + line
                elif current_section == 'generation':
                    generation_prompt += ' ' + line

        # Clean up the extracted content
        title = title[:60].strip()
        caption = caption[:2200].strip()
        hashtags = hashtags.strip()
        generation_prompt = generation_prompt.strip()

        # Ensure we have defaults if parsing failed
        if not title:
            title = f"Amazing {business_info.get('name', 'Business')} {mode.title()}"
        if not caption:
            caption = f"Check out this incredible {mode} for {business_info.get('name', 'our business')}! {prompt}"
        if not hashtags:
            hashtags = "#Business #Content #SocialMedia"
        if not generation_prompt:
            generation_prompt = f"Create a {mode} showing: {prompt}. Business: {business_info.get('name', 'Unknown')}, Industry: {business_info.get('industry', 'General')}"

        return {
            "mode": mode,
            "provider": "nano-banana",  # Gemini 2.5 Flash Image
            "title": title,
            "caption": caption,
            "hashtags": hashtags,
            "generation_prompt": generation_prompt,
            "notes": "Generated using Gemini AI for optimal social media engagement"
        }

    except Exception as e:
        # Fallback to mock data if API call fails
        print(f"Gemini API error: {e}")
        return {
            "mode": mode,
            "provider": "nano-banana",
            "title": f"Amazing {business_info.get('name', 'Business')} Content",
            "caption": f"Check out this incredible {mode} for {business_info.get('name', 'our business')}! {prompt}",
            "hashtags": "#Business #Content #SocialMedia",
            "generation_prompt": f"Create a {mode} showing: {prompt}. Business: {business_info.get('name', 'Unknown')}, Industry: {business_info.get('industry', 'General')}",
            "notes": f"API Error: {str(e)}. Using fallback content."
        }


def generate_image(prompt: str) -> Optional[str]:
    """
    Generate an image using Gemini 2.5 Flash Image (Nano Banana).

    Args:
        prompt: Detailed prompt for image generation

    Returns:
        Base64 encoded image data or None if failed
    """
    if not settings.GEMINI_API_KEY:
        return None

    try:
        import google.generativeai as genai

        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Use Gemini image model for image generation
        model = genai.GenerativeModel(settings.GEMINI_IMAGE_MODEL)

        # For now, we'll use text-to-image through Gemini's capabilities
        # Note: Direct image generation might require different API calls
        image_prompt = f"Generate an image based on this description: {prompt}"

        response = model.generate_content(image_prompt)

        # This is a placeholder - actual image generation would require
        # different API calls or integrations with image generation services
        # For now, we'll return None and let the frontend handle image generation
        return None

    except Exception as e:
        print(f"Image generation error: {e}")
        return None


def generate_video(prompt: str) -> Optional[str]:
    """
    Generate a video using Gemini 2.5 Flash Image (Nano Banana).

    Args:
        prompt: Detailed prompt for video generation

    Returns:
        Video URL or None if failed
    """
    if not settings.GEMINI_API_KEY:
        return None

    try:
        import google.generativeai as genai

        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Use Gemini image model for video planning
        model = genai.GenerativeModel(settings.GEMINI_IMAGE_MODEL)

        video_planning_prompt = f"""
        Create a detailed video concept based on this description: {prompt}

        Provide:
        1. Video style and format recommendations
        2. Scene breakdown with timing
        3. Audio/music suggestions
        4. Text overlays and effects
        5. Call-to-action elements
        """

        response = model.generate_content(video_planning_prompt)

        # Return the video concept as text - actual video generation would require
        # integration with video generation services
        return response.text if response else None

    except Exception as e:
        print(f"Video generation error: {e}")
        return None


