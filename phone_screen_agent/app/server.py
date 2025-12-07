import json
import os
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import TimeoutError as ConnectionTimeoutError
from retell import Retell
from openai import OpenAI
from pydantic import BaseModel
from .custom_types import (
    ConfigResponse,
    ResponseRequiredRequest,
)
from .llm_with_func_calling import LlmClient  # or use .llm

load_dotenv(override=True)
app = FastAPI()
retell = Retell(api_key=os.environ["RETELL_API_KEY"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client for Excalidraw analysis
EXCALIDRAW_BASE_URL = os.getenv("EXCALIDRAW_BASE_URL", "http://localhost:3010")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

openai_client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

# In-memory storage for call data
call_data_store: Dict[str, Dict[str, Any]] = {}

# Create directories for storing data
CALL_DATA_DIR = Path("call_data")
CALL_DATA_DIR.mkdir(exist_ok=True)

TAVUS_WEBHOOK_DIR = Path("tavus_webhooks")
TAVUS_WEBHOOK_DIR.mkdir(exist_ok=True)


# Pydantic models
class CheckDiagramRequest(BaseModel):
    conversation_id: str


# Helper functions for Excalidraw
def get_scene_elements():
    """Fetch all elements from the Excalidraw canvas."""
    resp = requests.get(f"{EXCALIDRAW_BASE_URL}/api/elements")
    data = resp.json()
    print(f"Fetched {len(data.get('elements', []))} elements from Excalidraw")
    resp.raise_for_status()
    return data.get("elements", [])


def call_llm_for_db_highlight(elements):
    """Ask LLM to evaluate the architecture diagram and identify issues."""
    prompt = f"""
You are an expert system design interviewer evaluating a candidate's architecture diagram for a web-based note-taking application (similar to Google Keep or Notion).

You are given a JSON array of Excalidraw elements (rectangles, arrows, text, etc.).
Each element has properties like id, type, x, y, width, height, text, strokeColor, backgroundColor, etc.

Context - Note-Taking App Requirements:
A web-based note-taking app typically needs:
- User authentication and authorization
- Real-time or near-real-time sync across devices
- Data persistence (notes, attachments, metadata)
- Search functionality
- Potentially: rich text editing, file attachments, sharing/collaboration
- High availability and data durability (users can't lose their notes)

Your Task:
Analyze the architecture diagram and identify issues specific to a note-taking application, such as:

Critical Issues (Red - #ff0000):
- Single points of failure for data storage (no database replication/backup)
- Missing authentication/authorization layer
- No data persistence strategy
- Single application server (no redundancy for a production app)

Moderate Concerns (Orange - #ff8800):
- Missing caching layer (for frequently accessed notes)
- No CDN for static assets
- Missing search infrastructure (for note search)
- No message queue for async operations (email notifications, etc.)
- Lack of monitoring/logging infrastructure

Minor Improvements (Yellow - #ffcc00):
- Could benefit from read replicas for scaling
- Missing rate limiting
- No mention of backup strategy

Return JSON with:
- "feedback": 2-3 sentences explaining the main issues. Be specific to note-taking app needs (e.g., "Your database is a single point of failure - if it goes down, users lose access to all their notes. Consider adding replication.")
- "elements_to_update": Highlight problematic components with appropriate severity colors
- "elements_to_create": Add brief labels (1-3 words) like "SPOF", "No Auth", "Missing Cache", "Add Replicas"

Guidelines:
- Focus on 1-3 most critical issues for a production note-taking app
- Be constructive and specific
- If well-designed, acknowledge strengths and suggest minor improvements
- Position labels near (not overlapping) the components

Respond with **only** valid JSON:

{{
  "feedback": "Your specific, actionable feedback here (2-3 sentences)",
  "elements_to_update": [
    {{"id": "<element-id>", "strokeColor": "#ff0000", "backgroundColor": "#ffe5e5"}}
  ],
  "elements_to_create": [
    {{
      "type": "text",
      "x": <x-position>,
      "y": <y-position>,
      "text": "<brief-label>",
      "fontSize": 20,
      "strokeColor": "<color-matching-severity>"
    }}
  ]
}}

Here is the current elements array:

{json.dumps(elements, indent=2)}
    """

    completion = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert system design interviewer specializing in web applications. You analyze architecture diagrams for note-taking apps and provide constructive, specific feedback. You return only valid JSON that can be parsed by Python json.loads.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    content = completion.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.lower().startswith("json"):
            content = content[4:].lstrip()

    data = json.loads(content)
    return data


def build_element_lookup(elements):
    return {el["id"]: el for el in elements if "id" in el}


def apply_updates(elements, updates):
    """For each element patch {id, ...props}, merge into original and PUT back."""
    by_id = build_element_lookup(elements)

    for patch in updates:
        el_id = patch.get("id")
        if not el_id or el_id not in by_id:
            print(f"Skipping unknown element id: {el_id}")
            continue

        original = by_id[el_id]
        updated = {**original, **patch}

        url = f"{EXCALIDRAW_BASE_URL}/api/elements/{el_id}"
        resp = requests.put(url, json=updated)
        try:
            resp.raise_for_status()
            print(f"Updated element {el_id}")
        except Exception as e:
            print(f"Failed to update {el_id}: {e}, response={resp.text}")


def create_elements(new_elements):
    """POST new elements to the canvas."""
    if not new_elements:
        return

    url = f"{EXCALIDRAW_BASE_URL}/api/elements"
    
    success_count = 0
    for el in new_elements:
        try:
            resp = requests.post(url, json=el)
            resp.raise_for_status()
            success_count += 1
        except Exception as e:
            print(f"Failed to create element {el.get('type')}: {e}, response={resp.text}")
            
    if success_count > 0:
        print(f"Created {success_count} new elements")


# Helper functions for Retell call data
def fetch_retell_call_details(call_id: str) -> Optional[Dict[str, Any]]:
    """Fetch full call details from Retell API."""
    retell_api_key = os.getenv("RETELL_API_KEY")
    if not retell_api_key:
        print("RETELL_API_KEY not set, skipping API call")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {retell_api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"https://api.retellai.com/v2/get-call/{call_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching call details for {call_id}: {e}")
        return None


def save_call_data(call_id: str, data: Dict[str, Any]):
    """Save merged call data to JSON file."""
    file_path = CALL_DATA_DIR / f"{call_id}.json"
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved call data to {file_path}")
    except Exception as e:
        print(f"Error saving call data: {e}")


# Excalidraw endpoint
@app.post("/check_diagram")
async def check_diagram(request: CheckDiagramRequest):
    try:
        print(f"Checking diagram for conversation: {request.conversation_id}")
        
        elements = get_scene_elements()
        print(f"Fetched {len(elements)} elements from Excalidraw")

        llm_response = call_llm_for_db_highlight(elements)
        updates = llm_response.get("elements_to_update", [])
        creates = llm_response.get("elements_to_create", [])
        feedback = llm_response.get("feedback", "I've analyzed your diagram.")

        print("LLM suggested updates:", updates)
        print("LLM suggested creates:", creates)

        apply_updates(elements, updates)
        create_elements(creates)

        print("Done. Check your Excalidraw room; DB should be highlighted and labeled.")
        return {"feedback": feedback}

    except Exception as e:
        print(f"Error in check_diagram: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


# Handle webhook from Tavus. Dump all payloads to files for debugging.
@app.post("/tavus-webhook")
async def handle_tavus_webhook(request: Request):
    try:
        post_data = await request.json()
        
        # Extract key fields from payload
        conversation_id = post_data.get("conversation_id", "unknown")
        event_type = post_data.get("event_type", "unknown")
        
        # Log webhook receipt
        print(f"📥 Tavus webhook: {event_type} (conversation: {conversation_id})")
        
        # Generate filename: conversation_id_datetime_event.json
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        
        # Clean event_type for filename (replace dots with underscores)
        event_clean = event_type.replace(".", "_")
        
        filename = f"{conversation_id}_{timestamp}_{event_clean}.json"
        file_path = TAVUS_WEBHOOK_DIR / filename
        
        # Save full webhook data
        webhook_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "headers": dict(request.headers),
            "payload": post_data
        }
        
        with open(file_path, 'w') as f:
            json.dump(webhook_data, f, indent=2)
        
        print(f"✓ Saved to: {file_path.name}")
        
        # Check if this webhook contains a transcript (for grading)
        # Transcript comes in the payload.properties.transcript field
        properties = post_data.get("properties", {})
        has_transcript = "transcript" in properties and isinstance(properties.get("transcript"), list) and len(properties.get("transcript", [])) > 0
        
        if has_transcript:
            print("📊 Transcript detected - grading system design interview...")
            from .grading import grade_interview, extract_transcript_from_tavus
            
            # Extract Tavus transcript
            tavus_transcript = extract_transcript_from_tavus(webhook_data)
            
            if tavus_transcript:
                # Grade system design interview
                grade = grade_interview(tavus_transcript, "system_design")
                print(f"✓ System design grade: {grade['score']}/3")
                
                # Save grade to file
                grade_filename = f"{conversation_id}_{timestamp}_system_design_grade.json"
                grade_file_path = TAVUS_WEBHOOK_DIR / grade_filename
                
                with open(grade_file_path, 'w') as f:
                    json.dump(grade, f, indent=2)
                
                print(f"✓ Saved grade to: {grade_file_path}")
            else:
                print("⚠ Could not extract transcript from Tavus webhook")
        
        return JSONResponse(status_code=200, content={"received": True})
    
    except Exception as err:
        print(f"❌ Tavus webhook error: {err}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error", "error": str(err)}
        )


# Handle webhook from Retell server. This is used to receive events from Retell server.
# Including call_started, call_ended, call_analyzed
@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        post_data = await request.json()
        
        # Log webhook receipt
        event = post_data.get("event")
        call_data = post_data.get("data") or post_data.get("call", {})
        call_id = call_data.get("call_id", "unknown")
        print(f"📥 Retell webhook: {event} (call: {call_id})")
        
        # Verify signature
        skip_verification = os.getenv("SKIP_SIGNATURE_VERIFICATION", "false").lower() == "true"
        
        if skip_verification:
            print("⚠ SKIPPING signature verification (SKIP_SIGNATURE_VERIFICATION=true)")
            valid_signature = True
        else:
            try:
                valid_signature = retell.verify(
                    json.dumps(post_data, separators=(",", ":"), ensure_ascii=False),
                    api_key=str(os.environ["RETELL_API_KEY"]),
                    signature=str(request.headers.get("X-Retell-Signature")),
                )
            except Exception as verify_err:
                print(f"⚠ Signature verification error: {verify_err}")
                valid_signature = False
        
        if not valid_signature:
            print(f"❌ Unauthorized webhook")
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})
        
        if not call_id:
            print(f"❌ No call_id in payload")
            return JSONResponse(status_code=400, content={"message": "call_id missing from payload"})
        
        if event == "call_started":
            print(f"✓ Call started: {call_id}")
        elif event == "call_ended":
            print(f"✓ Call ended: {call_id}")
            # Store call data in memory
            call_data_store[call_id] = {
                "event": event,
                "call_ended_data": call_data,
                "received_at": datetime.utcnow().isoformat()
            }
            # Grade phone screen interview
            transcript = call_data.get("transcript", "")
            if transcript:
                print(f"📊 Grading phone screen...")
                from .grading import grade_interview
                
                grade = grade_interview(transcript, "phone_screen")
                print(f"✓ Grade: {grade['score']}/3 - Saved to {call_id}_phone_screen_grade.json")
                
                # Save grade to file
                grade_filename = f"{call_id}_phone_screen_grade.json"
                grade_file_path = CALL_DATA_DIR / grade_filename
                
                with open(grade_file_path, 'w') as f:
                    json.dump(grade, f, indent=2)

        elif event == "call_analyzed":
            print(f"✓ Call analyzed: {call_id}")
            # Get stored call_ended data
            stored_data = call_data_store.get(call_id, {})
            
            # Fetch full call details from Retell API
            api_call_data = fetch_retell_call_details(call_id)
            
            # Merge all data
            merged_data = {
                "call_id": call_id,
                "call_ended_webhook": stored_data.get("call_ended_data"),
                "call_analyzed_webhook": call_data,
                "retell_api_data": api_call_data,
                "timestamps": {
                    "call_ended_received": stored_data.get("received_at"),
                    "call_analyzed_received": datetime.utcnow().isoformat()
                }
            }
            
            # Save merged data to JSON file
            save_call_data(call_id, merged_data)
            
            # Clean up from memory
            if call_id in call_data_store:
                del call_data_store[call_id]
        else:
            print(f"⚠ Unknown event: {event}")
        
        return JSONResponse(status_code=200, content={"received": True})
    except Exception as err:
        print(f"❌ Retell webhook error: {err}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error", "error": str(err)}
        )


# Start a websocket server to exchange text input and output with Retell server. Retell server
# will send over transcriptions and other information. This server here will be responsible for
# generating responses with LLM and send back to Retell server.
@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    try:
        await websocket.accept()
        llm_client = LlmClient()

        # Send optional config to Retell server
        config = ConfigResponse(
            response_type="config",
            config={
                "auto_reconnect": True,
                "call_details": True,
            },
            response_id=1,
        )
        await websocket.send_json(config.__dict__)

        # Send first message to signal ready of server
        response_id = 0
        first_event = llm_client.draft_begin_message()
        await websocket.send_json(first_event.__dict__)

        async def handle_message(request_json):
            nonlocal response_id

            # There are 5 types of interaction_type: call_details, pingpong, update_only, response_required, and reminder_required.
            # Not all of them need to be handled, only response_required and reminder_required.
            if request_json["interaction_type"] == "call_details":
                print(json.dumps(request_json, indent=2))
                return
            if request_json["interaction_type"] == "ping_pong":
                await websocket.send_json(
                    {
                        "response_type": "ping_pong",
                        "timestamp": request_json["timestamp"],
                    }
                )
                return
            if request_json["interaction_type"] == "update_only":
                return
            if (
                request_json["interaction_type"] == "response_required"
                or request_json["interaction_type"] == "reminder_required"
            ):
                response_id = request_json["response_id"]
                request = ResponseRequiredRequest(
                    interaction_type=request_json["interaction_type"],
                    response_id=response_id,
                    transcript=request_json["transcript"],
                )
                print(
                    f"""Received interaction_type={request_json['interaction_type']}, response_id={response_id}, last_transcript={request_json['transcript'][-1]['content']}"""
                )

                async for event in llm_client.draft_response(request):
                    await websocket.send_json(event.__dict__)
                    if request.response_id < response_id:
                        break  # new response needed, abandon this one

        async for data in websocket.iter_json():
            asyncio.create_task(handle_message(data))

    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_id}")
    except ConnectionTimeoutError as e:
        print("Connection timeout error for {call_id}")
    except Exception as e:
        print(f"Error in LLM WebSocket: {e} for {call_id}")
        await websocket.close(1011, "Server error")
    finally:
        print(f"LLM WebSocket connection closed for {call_id}")
