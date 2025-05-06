# llm_handler.py
"""
Handles interaction with the Google Generative AI (Gemini) API
to generate social media replies.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# LLM Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY environment variable not set. LLM features will be disabled.")
    genai_configured = False
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash') 
        genai_configured = True
        logger.info("Google Generative AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Google Generative AI: {e}", exc_info=True)
        genai_configured = False


#Prompting
def create_prompt(platform: str, post_text: str) -> str:
    platform_guidance = {
        "Twitter": "Keep it concise, possibly witty or conversational. Hashtags are common.",
        "LinkedIn": "Maintain a professional but engaging tone. Focus on insights, encouragement, or relevant questions.",
        "Instagram": "Be visually oriented (even if text-only reply), friendly, and often use emojis. Keep it relatively short and positive.",
        "Generic": "Be authentic, engaging, and relevant to the post." 
    }

    guidance = platform_guidance.get(platform, platform_guidance["Generic"])

    prompt = f"""
    You are an expert social media user tasked with writing replies.
    Your goal is to generate a reply that is indistinguishable from one written by a real, thoughtful human.

    **Context:**
    - **Platform:** {platform}
    - **Original Post:** "{post_text}"

    **Instructions:**
    1.  **Analyze:** Understand the tone, style, intent (e.g., sharing news, asking question, expressing opinion), and context of the original post.
    2.  **Platform Nuance:** Consider the typical communication style for {platform}. {guidance}
    3.  **Generate Reply:** Write a reply that:
        - Is authentic and sounds like a real person genuinely engaging with the post.
        - Directly relates to the content of the original post.
        - Matches the likely tone and context (unless a contrasting tone is clearly appropriate and human-like, e.g., gentle disagreement).
        - Is concise and easy to read.
        - **Crucially, avoids AI giveaways:** Do NOT use overly formal language, generic phrases ("That's interesting!", "Great post!"), repetitive sentence structures, or language that feels unnaturally objective or detached. Do not sound like a chatbot or assistant.
        - If appropriate for the platform and context, consider adding relevant emojis or hashtags, but don't overdo it.
    4.  **Output ONLY the reply text.** Do not include any preamble, explanation, or quotation marks around the reply itself.

    **Example Scenario (Internal Thought Process - DO NOT replicate in output):**
    - *If Post is:* "Just finished a marathon! So tired but proud. #running" (on Instagram)
    - *Your thought:* "Okay, Instagram post, celebratory and personal. Reply should be encouraging, maybe use an emoji. Keep it short."
    - *Good Reply:* "Wow, congratulations! That's amazing! Rest up!"
    - *Bad Reply (AI giveaway):* "Acknowledged. Completing a marathon is a significant achievement demonstrating physical endurance. Well done."

    **Generate the human-like reply now based on the provided Platform and Original Post:**
    """
    return prompt.strip()

#Reply Generation#
async def generate_reply(platform: str, post_text: str) -> Optional[str]:

    if not genai_configured:
        logger.warning("LLM generation skipped: Google Generative AI is not configured.")
        return None

    prompt = create_prompt(platform, post_text)
    logger.debug(f"Generated Prompt:\n{prompt}") # Log the prompt for debugging if needed (consider privacy)

    try:
        # Set safety settings to avoid blocking potentially harmless content,
        # adjust as needed based on your use case and risk tolerance.
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = await model.generate_content_async(
            prompt,
            safety_settings=safety_settings,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8, 
                top_p=0.9,      
                top_k=40        
            )
        )

        # Accessing the generated text safely
        # Check if response.parts exists and is not empty
        if response.parts:
            generated_text = response.text.strip()
            logger.info(f"Successfully generated reply for platform '{platform}'")
            # Basic post-processing: remove potential quotation marks if the model added them
            if generated_text.startswith('"') and generated_text.endswith('"'):
                generated_text = generated_text[1:-1]
            elif generated_text.startswith("'") and generated_text.endswith("'"):
                 generated_text = generated_text[1:-1]
            return generated_text
        else:
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 logger.warning(f"LLM generation blocked. Reason: {response.prompt_feedback.block_reason}")
            else:
                 logger.warning("LLM generation failed: No content generated (potentially blocked or empty response).")
            return None

    except Exception as e:
        logger.error(f"Error generating reply using LLM: {e}", exc_info=True)
        return None

# --- Helper to check LLM configuration ---
def is_llm_available() -> bool:
    return genai_configured

