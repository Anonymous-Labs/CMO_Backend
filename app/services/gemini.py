import os
from typing import Dict, Any, Optional, List

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger("gemini")


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
    logger.info(f"Generating social content: mode={mode}, business={business_info.get('name', 'Unknown')}")
    
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured, returning mock data")
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


def generate_autonomous_followup(
    conversation_history: List[Dict[str, Any]],
    business_info: Optional[Dict[str, Any]] = None,
    user_name: str = "User"
) -> str:
    """
    Generate an autonomous follow-up message for proactive conversation.
    """
    logger.debug("Generating autonomous follow-up message")

    if not settings.GEMINI_API_KEY:
        return "I'd love to share some more marketing insights with you. What specific area of marketing are you most interested in right now?"

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Try different models with fallback - use known working models
        models_to_try = ["gemini-2.0-flash", "gemini-pro-latest", "gemini-flash-latest"]

        # Build conversation context
        conversation_text = ""
        if conversation_history:
            for msg in conversation_history[-8:]:  # Last 8 messages for context
                # Handle both dict and ChatMessage objects
                if isinstance(msg, dict):
                    role = "User" if msg.get("role") == "user" else "CMO AI"
                    content = msg.get("content", "")
                else:
                    # Assume it's a ChatMessage object
                    role = "User" if getattr(msg, 'role', '') == "user" else "CMO AI"
                    content = getattr(msg, 'content', '')
                conversation_text += f"{role}: {content}\n\n"

        business_context = ""
        if business_info:
            business_context = f"""
BUSINESS CONTEXT:
- Business Name: {business_info.get('name', 'Not provided')}
- Industry: {business_info.get('industry', 'Not provided')}
- Target Audience: {business_info.get('target_audience', 'Not provided')}

"""

        prompt = f"""You are a proactive Chief Marketing Officer (CMO) AI assistant. You need to generate a natural follow-up message to continue the marketing conversation.

{business_context}

CONVERSATION HISTORY:
{conversation_text}

INSTRUCTIONS:
- Generate a short, engaging follow-up message (1-2 sentences)
- Ask a specific question or suggest a next topic to continue the conversation
- Be conversational and friendly, like a human marketing expert
- Reference something from the conversation history if relevant
- Keep it under 100 words
- Make it feel natural, not robotic

FOLLOW-UP MESSAGE:"""

        # Try each model until one works
        last_error = None
        for model_to_try in models_to_try:
            try:
                logger.debug(f"Trying model: {model_to_try} for autonomous followup")
                model = genai.GenerativeModel(model_to_try)
                response = model.generate_content(prompt)
                followup = response.text.strip() if response.text else "What else would you like to discuss about your marketing strategy?"
                logger.info(f"Autonomous follow-up generated using model: {model_to_try}")
                return followup
            except Exception as model_error:
                last_error = model_error
                logger.warning(f"Model {model_to_try} failed for autonomous followup: {str(model_error)}")
                continue

        # If all models failed, return fallback
        logger.error(f"All Gemini models failed for autonomous followup. Last error: {str(last_error)}")
        return "I'd love to hear more about your marketing goals. What's your biggest challenge right now?"

    except Exception as e:
        logger.error(f"Error generating autonomous followup: {str(e)}", exc_info=True)
        return "Let's continue our marketing discussion. What aspect of your strategy would you like to explore next?"

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
        logger.error(f"Gemini API error during content generation: {str(e)}", exc_info=True)
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


def chat_with_cmo(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    business_info: Optional[Dict[str, Any]] = None,
    user_name: str = "User",
    is_greeting: bool = False,
    autonomous_mode: bool = False
) -> Dict[str, Any]:
    """
    Chat with CMO AI for marketing advice and assistance.
    
    Args:
        user_message: The user's message
        conversation_history: Previous conversation messages
        business_info: Business profile information
        user_name: Name of the user
        is_greeting: Whether this is an initial greeting
    
    Returns:
        CMO AI's response message
    """
    logger.info(f"Chat request: is_greeting={is_greeting}, user={user_name}, message_length={len(user_message)}")
    
    if is_greeting:
        logger.debug("Generating greeting message")
        # Generate personalized greeting
        if business_info and business_info.get('name'):
            greeting = f"Hello! I'm your CMO AI assistant. I see you're working with {business_info.get('name')}. I'm here to help you with all your marketing needs - from content strategy to social media campaigns. What would you like to work on today?"
        else:
            greeting = "Hello! I'm your CMO AI assistant. I'm here to help you with all your marketing needs - from content strategy and social media campaigns to brand positioning and audience engagement. How can I assist you today?"
        
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured, using default greeting")
            return {
                "message": greeting,
                "role": "assistant",
                "autonomous_followup": None
            }
        
        # Use Gemini to make greeting more personalized and engaging
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            
            context = ""
            if business_info:
                context = f"\nUser's business: {business_info.get('name', 'Unknown')} in {business_info.get('industry', 'general')} industry."
    
            prompt = f"""You are a friendly, proactive Chief Marketing Officer (CMO) AI assistant. Your role is to help businesses with marketing strategy, content creation, social media, and brand growth.

{context}

Create a warm, engaging greeting that:
1. Introduces yourself as their CMO AI
2. Shows enthusiasm about helping with marketing
3. Mentions 2-3 key areas you can help with (content strategy, social media, campaigns, etc.)
4. Asks an open-ended question to start the conversation
5. Keep it conversational and friendly, not robotic

Keep the response under 150 words and make it feel personal and proactive."""
            
            # Try each model until one works
            last_error = None
            for model_to_try in models_to_try:
                try:
                    logger.debug(f"Trying model: {model_to_try}")
                    model = genai.GenerativeModel(model_to_try)
                    logger.debug("Calling Gemini API for personalized greeting")
                    response = model.generate_content(prompt)
                    result = response.text.strip() if response.text else greeting
                    logger.info(f"Greeting generated successfully via Gemini using model: {model_to_try}")
                    return {
                        "message": result,
                        "role": "assistant",
                        "autonomous_followup": None
                    }
                except Exception as model_error:
                    last_error = model_error
                    logger.warning(f"Model {model_to_try} failed: {str(model_error)}")
                    continue
            
            # If all models failed, log and return default
            logger.error(f"All Gemini models failed. Last error: {str(last_error)}")
            return {
                "message": greeting,
                "role": "assistant",
                "autonomous_followup": None
            }
        except Exception as e:
            logger.error(f"Error generating greeting via Gemini: {str(e)}", exc_info=True)
            return greeting
    
    # Regular chat conversation
    logger.debug(f"Processing chat message with history length: {len(conversation_history) if conversation_history else 0}")

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured, returning fallback response")
        # Fallback response
        return {
            "message": "I'd love to help you with your marketing needs! To enable full AI capabilities, please configure your GEMINI_API_KEY. In the meantime, I can help you think through marketing strategies, content ideas, and campaign planning. What specific marketing challenge are you facing?",
            "role": "assistant",
            "autonomous_followup": None
        }
    
    try:
        logger.debug("Initializing Gemini API")
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Try different models with fallback - use known working models
        models_to_try = ["gemini-2.0-flash", "gemini-pro-latest", "gemini-flash-latest"]
        
        models_to_try = ["gemini-2.0-flash", "gemini-pro-latest", "gemini-flash-latest"]
#            models_to_try = ["gemini-1.0-pro", "gemini-pro-vision"]

        # Build system prompt
        system_prompt = """You are a Chief Marketing Officer (CMO) AI assistant - an autonomous, proactive marketing expert. Your personality is:
- Friendly, enthusiastic, and genuinely interested in helping businesses grow
- Strategic and knowledgeable about modern marketing (social media, content marketing, SEO, email marketing, branding, etc.)
- Proactive - you don't just answer questions, you offer insights and suggestions
- Conversational and approachable, not overly formal
- Focused on practical, actionable marketing advice

Your expertise includes:
- Social media strategy (Instagram, Facebook, LinkedIn, TikTok, Twitter)
- Content creation and content calendars
- Brand positioning and messaging
- Audience targeting and engagement
- Marketing campaigns and analytics
- SEO and digital marketing
- Email marketing and automation

Always provide helpful, actionable advice. Ask follow-up questions when appropriate. Be proactive in suggesting next steps."""
        
        # Build context from business info
        business_context = ""
        if business_info:
            business_context = f"""
BUSINESS CONTEXT:
- Business Name: {business_info.get('name', 'Not provided')}
- Industry: {business_info.get('industry', 'Not provided')}
- Description: {business_info.get('description', 'Not provided')}
- Target Audience: {business_info.get('target_audience', 'Not provided')}
- Brand Tone: {business_info.get('brand_tone', 'Not provided')}

Use this context to provide personalized marketing advice."""
        
        # Build conversation history
        conversation_text = ""
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                # Handle both dict and ChatMessage objects
                if isinstance(msg, dict):
                    role = "User" if msg.get("role") == "user" else "CMO AI"
                    content = msg.get("content", "")
                else:
                    # Assume it's a ChatMessage object
                    role = "User" if getattr(msg, 'role', '') == "user" else "CMO AI"
                    content = getattr(msg, 'content', '')
                conversation_text += f"{role}: {content}\n\n"
        
        # Create the full prompt
        full_prompt = f"""{system_prompt}

{business_context}

{conversation_text if conversation_text else ""}User: {user_message}

CMO AI:"""
        
        # Try each model until one works
        last_error = None
        for model_to_try in models_to_try:
            try:
                logger.debug(f"Trying model: {model_to_try}")
                model = genai.GenerativeModel(model_to_try)
                logger.debug("Calling Gemini API for chat response")
                response = model.generate_content(full_prompt)
                result = response.text.strip() if response.text else "I'm here to help! Could you tell me more about what you'd like to work on?"
                logger.info(f"Chat response generated successfully using model: {model_to_try} (length: {len(result)} chars)")
                return result
            except Exception as model_error:
                last_error = model_error
                logger.warning(f"Model {model_to_try} failed: {str(model_error)}")
                continue

        # If all models failed, log and return fallback
        logger.error(f"All Gemini models failed. Last error: {str(last_error)}")
        return {
            "message": "I apologize, but I'm having trouble processing that right now. Could you try rephrasing your question? I'm here to help with all your marketing needs!",
            "role": "assistant",
            "autonomous_followup": None
        }
    
    except Exception as e:
        logger.error(f"Error in chat_with_cmo: {str(e)}", exc_info=True)
        return {
            "message": "I apologize, but I'm having trouble processing that right now. Could you try rephrasing your question? I'm here to help with all your marketing needs!",
            "role": "assistant",
            "autonomous_followup": None
        }

