"""
Interview Grading System

This module contains rubrics and grading logic for phone screen and system design interviews.
Each interview is graded independently when its webhook is received.
"""

import json
import os
from openai import OpenAI
from datetime import datetime

# Initialize OpenAI client
openai_client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)

PHONE_SCREEN_RUBRIC = """
# Phone Screen Interview Rubric

Based on the phone screen agent prompt:
- Greet candidate and explain AI-first technical screen (~15 minutes)
- Ask: "What's the most exceptional thing you've built?"
- Deep dive: 3-5 levels down on a concrete part of their system
- Probe: how they built it, why they chose that tech, how it works
- Close with candidate questions about x.ai

## Evaluation Criteria:

1. **Technical Depth (40%)**
   - Did the candidate explain their project with sufficient technical detail?
   - Could they go 3-5 levels deep when probed?
   - Did they demonstrate understanding of the technologies they used?
   - Could they explain WHY they made specific technical decisions?
   - Did they show ownership of the technical implementation?

2. **Communication (30%)**
   - Did the candidate communicate clearly and concisely?
   - Could they explain complex technical concepts simply?
   - Were they responsive to follow-up questions?
   - Did they stay on topic and avoid rambling?
   - Could they articulate their thought process?

3. **Problem-Solving & Engineering Mindset (20%)**
   - Did they show evidence of thoughtful engineering decisions?
   - Could they discuss tradeoffs in their approach?
   - Did they demonstrate initiative and ownership?
   - Did they show curiosity and depth of understanding?
   - Did they consider alternatives and explain their choices?

4. **Cultural Fit for x.ai (10%)**
   - Do they seem aligned with fast-paced, small-team culture?
   - Did they show genuine interest in x.ai?
   - Are they comfortable with ambiguity and rapid iteration?
   - Do they demonstrate deep technical ownership?

## Scoring Guide:
- **3 (Strong Yes)**: Exceptional candidate. Clear technical depth (went 4-5 levels deep), excellent communication, strong engineering mindset. Hire immediately.
- **2 (Weak Yes)**: Solid candidate with some strengths. Went 2-3 levels deep, decent communication. May have minor gaps but overall positive. Move forward with caution.
- **1 (Weak No)**: Significant concerns. Struggled to go deep (only 1-2 levels), lacks communication skills or technical depth. Unlikely to succeed.
- **0 (Strong No)**: Clear rejection. Could not explain their work, major red flags in technical ability or communication.
"""

SYSTEM_DESIGN_RUBRIC = """
# System Design Interview Rubric

Based on the system design interviewer prompt:
- Ask candidate to design a web-based note-taking app
- Have them describe design verbally first
- Ask them to draw and submit a diagram
- Use check_diagram tool to evaluate (after confirmation)
- Read feedback and probe deeper (load balancer, app layer, database)
- Ask follow-ups on scalability, reliability, and tradeoffs

## Evaluation Criteria:

1. **Requirements Gathering & Clarification (15%)**
   - Did the candidate ask clarifying questions about the note-taking app?
   - Did they identify key requirements (auth, sync, persistence, search)?
   - Did they consider scale and constraints?
   - Did they think about functional vs non-functional requirements?

2. **Architecture Design (35%)**
   - Did they propose a reasonable high-level architecture?
   - Did they include necessary components (load balancer, app servers, database, caching)?
   - Did they consider data persistence and durability (critical for notes)?
   - Did they address authentication and authorization?
   - Was their verbal description clear before drawing?

3. **Scalability & Reliability (25%)**
   - Did they identify and address single points of failure?
   - Did they discuss replication, redundancy, and failover?
   - Did they consider how the system would scale with users?
   - Did they discuss backup and disaster recovery?
   - Did they respond well to feedback from check_diagram?

4. **Technical Depth & Tradeoffs (15%)**
   - Could they explain WHY they chose specific technologies?
   - Did they discuss tradeoffs in their design decisions?
   - Did they demonstrate understanding of the components they proposed?
   - Could they respond thoughtfully to follow-up questions about load balancer, app layer, database?
   - Did they consider alternatives?

5. **Communication & Diagram Quality (10%)**
   - Did they explain their design clearly before drawing?
   - Was their diagram clear and well-organized?
   - Did they respond well to feedback and follow-up questions?
   - Did they maintain a structured conversation?

## Scoring Guide:
- **3 (Strong Yes)**: Excellent system design. Comprehensive architecture, addressed SPOFs, showed strong understanding of tradeoffs. Clear communication. Hire.
- **2 (Weak Yes)**: Decent design with some gaps. May have missed some components but overall sound approach. Responded reasonably to feedback. Consider moving forward.
- **1 (Weak No)**: Significant architectural issues. Missing critical components or poor understanding of scalability/reliability. Struggled with follow-ups.
- **0 (Strong No)**: Poor design. Major gaps in understanding. Could not respond to feedback. Clear rejection.
"""


def grade_interview(transcript: str, interview_type: str) -> dict:
    """
    Grade an interview transcript using the appropriate rubric.
    
    Args:
        transcript: The full interview transcript
        interview_type: Either "phone_screen" or "system_design"
    
    Returns:
        dict with score (0-3), reasoning, and summary
    """
    rubric = PHONE_SCREEN_RUBRIC if interview_type == "phone_screen" else SYSTEM_DESIGN_RUBRIC
    
    prompt = f"""
You are an expert technical interviewer at x.ai. You are grading a {interview_type.replace('_', ' ')} interview.

Here is the rubric to use:

{rubric}

Here is the interview transcript:

{transcript}

Based on the rubric, provide your evaluation in the following JSON format:

{{
  "score": <0-3>,
  "reasoning": "<2-3 paragraphs explaining your score, referencing specific examples from the transcript>",
  "summary": "<1 paragraph summary of the interview covering what was discussed and the candidate's performance>"
}}

Be specific and reference actual examples from the transcript in your reasoning.
Return ONLY valid JSON, no other text.
"""

    try:
        completion = openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert technical interviewer. You evaluate candidates fairly and provide detailed, specific feedback. You return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
        )
        
        content = completion.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.strip("`")
            if content.lower().startswith("json"):
                content = content[4:].lstrip()
        
        result = json.loads(content)
        result["interview_type"] = interview_type
        result["graded_at"] = datetime.utcnow().isoformat()
        
        return result
        
    except Exception as e:
        print(f"Error grading interview: {e}")
        return {
            "score": -1,
            "reasoning": f"Error during grading: {str(e)}",
            "summary": "Grading failed",
            "interview_type": interview_type,
            "graded_at": datetime.utcnow().isoformat()
        }


def extract_transcript_from_retell(call_data: dict) -> str:
    """Extract transcript from Retell call data."""
    if not call_data:
        return ""
    
    # Try different possible locations for transcript
    transcript = call_data.get("call_analyzed_webhook", {}).get("transcript", "")
    if not transcript:
        transcript = call_data.get("retell_api_data", {}).get("transcript", "")
    if not transcript:
        transcript = call_data.get("call_ended_webhook", {}).get("transcript", "")
    
    return transcript


def extract_transcript_from_tavus(webhook_data: dict) -> str:
    """Extract transcript from Tavus webhook data."""
    try:
        # Tavus transcript is in payload -> properties -> transcript
        # First try the nested structure (from saved webhook files)
        transcript_obj = webhook_data.get("payload", {}).get("properties", {}).get("transcript", [])
        
        # If not found, try direct properties (from raw webhook)
        if not transcript_obj:
            transcript_obj = webhook_data.get("properties", {}).get("transcript", [])
        
        # Transcript is an array of messages with role and content
        if isinstance(transcript_obj, list):
            lines = []
            for msg in transcript_obj:
                role = msg.get("role", "Unknown")
                content = msg.get("content", "")
                
                # Skip empty content and system messages
                if content and role != "system":
                    lines.append(f"{role}: {content}")
            return "\n".join(lines)
        elif isinstance(transcript_obj, str):
            return transcript_obj
        else:
            return ""
    except Exception as e:
        print(f"Error extracting Tavus transcript: {e}")
        return ""
