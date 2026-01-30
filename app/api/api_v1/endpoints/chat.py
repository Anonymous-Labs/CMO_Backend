from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services.gemini import chat_with_cmo
from app.core.logging_config import get_logger

logger = get_logger("chat")
router = APIRouter()


@router.post("/chat", response_model=schemas.ChatResponse)
def chat(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    req: schemas.ChatRequest,
) -> Any:
    """
    Chat with CMO AI for marketing advice and assistance.
    """
    logger.info(f"Chat request from user {current_user.id} ({current_user.email}) - Autonomous mode: {req.autonomous_mode}")
    logger.debug(f"User message length: {len(req.message)} chars, history length: {len(req.conversation_history)}")

    try:
        # Get business profile if available
        from app import crud
        business = crud.business.get_by_user_id(db, user_id=current_user.id)

        business_info = None
        if business:
            business_info = {
                "name": business.name,
                "industry": business.industry,
                "description": business.description,
                "target_audience": business.target_audience,
                "brand_tone": business.brand_tone,
            }
            logger.debug(f"Business context loaded: {business.name} ({business.industry})")
        else:
            logger.debug("No business profile found for user")

        # Get chat response from CMO AI
        logger.debug("Calling chat_with_cmo service")
        response = chat_with_cmo(
            user_message=req.message,
            conversation_history=req.conversation_history,
            business_info=business_info,
            user_name=current_user.full_name or current_user.email,
            autonomous_mode=req.autonomous_mode
        )

        logger.info(f"Chat response generated successfully (length: {len(response)} chars)")
        return response

    except Exception as e:
        logger.error(f"Chat error for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/greeting", response_model=schemas.ChatResponse)
def get_greeting(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get initial greeting message from CMO AI.
    """
    logger.info(f"Greeting request from user {current_user.id} ({current_user.email})")
    
    try:
        from app import crud
        business = crud.business.get_by_user_id(db, user_id=current_user.id)
        
        business_info = None
        if business:
            business_info = {
                "name": business.name,
                "industry": business.industry,
            }
            logger.debug(f"Business context for greeting: {business.name}")
        
        # Generate personalized greeting
        logger.debug("Generating personalized greeting")
        greeting = chat_with_cmo(
            user_message="",  # Empty message for greeting
            conversation_history=[],
            business_info=business_info,
            user_name=current_user.full_name or current_user.email,
            is_greeting=True
        )
        
        logger.info("Greeting generated successfully")
        return schemas.ChatResponse(message=greeting, role="assistant")
    
    except Exception as e:
        logger.warning(f"Error generating greeting, using fallback: {str(e)}")
        # Fallback greeting
        return schemas.ChatResponse(
            message="Hello! I'm your CMO AI assistant. I'm here to help you with all your marketing needs. How can I assist you today?",
            role="assistant"
        )

