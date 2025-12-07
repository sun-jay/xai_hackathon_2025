import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

load_dotenv()

EXCALIDRAW_BASE_URL = os.getenv("EXCALIDRAW_BASE_URL", "http://localhost:3010")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckDiagramRequest(BaseModel):
    conversation_id: str

def get_scene_elements():
    """Fetch all elements from the Excalidraw canvas."""
    resp = requests.get(f"{EXCALIDRAW_BASE_URL}/api/elements")
    data = resp.json()
    print(f"Fetched {len(data.get('elements', []))} elements from Excalidraw")
    # print(data)
    resp.raise_for_status()
    return data.get("elements", [])


def call_llm_for_db_highlight(elements):
    """
    Ask LLM to find the DB SPOF and return patches like:
    {
      "elements_to_update": [
        {"id": "...", "strokeColor": "#ff0000", "backgroundColor": "#ffe5e5"}
      ],
      "feedback": "Feedback message..."
    }
    """
    prompt = f"""
You are an expert system design interviewer. You are looking at a candidate's Excalidraw diagram.

You get a JSON array of elements (rectangles, arrows, text, etc.).
Each element has properties like id, type, x, y, width, height, text, strokeColor, backgroundColor, etc.

The diagram represents a 3-tier web service:
- load balancer
- business logic / application
- database

Treat the database as a single point of failure (SPOF).

Task:
1. Find the element that represents the database tier (based on its text, position, or other hints).
2. Return JSON with:
   - "elements_to_update": minimal patches to visually highlight the DB (bright red stroke, light red background).
   - "elements_to_create": a list of new elements to add:
     - A text element with text "SPOF" placed near the database.
   - "feedback": A short, constructive feedback message to the candidate about the SPOF.

Respond with **only** JSON of the form:

{{
  "feedback": "Your feedback message here...",
  "elements_to_update": [
    {{"id": "<element-id>", "strokeColor": "#ff0000", "backgroundColor": "#ffe5e5"}}
  ],
  "elements_to_create": [
    {{
      "type": "text",
      "x": <calculated-x>,
      "y": <calculated-y>,
      "text": "SPOF",
      "fontSize": 20,
      "strokeColor": "#ff0000"
    }}
  ]
}}

Here is the current elements array (pretty-printed JSON):

{json.dumps(elements, indent=2)}
    """

    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You return only valid JSON that can be parsed by Python json.loads.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = completion.choices[0].message.content.strip()
    # In case the model wraps in ```json``` fences
    if content.startswith("```"):
        content = content.strip("`")
        if content.lower().startswith("json"):
            content = content[4:].lstrip()

    data = json.loads(content)
    return data


def build_element_lookup(elements):
    return {el["id"]: el for el in elements if "id" in el}


def apply_updates(elements, updates):
    """
    For each element patch {id, ...props}, merge into original and PUT back.
    """
    by_id = build_element_lookup(elements)

    for patch in updates:
        el_id = patch.get("id")
        if not el_id or el_id not in by_id:
            print(f"Skipping unknown element id: {el_id}")
            continue

        original = by_id[el_id]
        updated = {**original, **patch}  # shallow merge, good enough for style updates

        url = f"{EXCALIDRAW_BASE_URL}/api/elements/{el_id}"
        resp = requests.put(url, json=updated)
        try:
            resp.raise_for_status()
            print(f"Updated element {el_id}")
        except Exception as e:
            print(f"Failed to update {el_id}: {e}, response={resp.text}")


def create_elements(new_elements):
    """
    POST new elements to the canvas.
    """
    if not new_elements:
        return

    url = f"{EXCALIDRAW_BASE_URL}/api/elements"
    
    success_count = 0
    for el in new_elements:
        try:
            # The API might expect a single element object
            resp = requests.post(url, json=el)
            resp.raise_for_status()
            success_count += 1
        except Exception as e:
            print(f"Failed to create element {el.get('type')}: {e}, response={resp.text}")
            
    if success_count > 0:
        print(f"Created {success_count} new elements")


@app.post("/check_diagram")
async def check_diagram(request: CheckDiagramRequest):
    try:
        print(f"Checking diagram for conversation: {request.conversation_id}")
        
        # 1) get what you drew
        elements = get_scene_elements()
        print(f"Fetched {len(elements)} elements from Excalidraw")

        # 2) send to LLM and get patches
        llm_response = call_llm_for_db_highlight(elements)
        updates = llm_response.get("elements_to_update", [])
        creates = llm_response.get("elements_to_create", [])
        feedback = llm_response.get("feedback", "I've analyzed your diagram.")

        print("LLM suggested updates:", updates)
        print("LLM suggested creates:", creates)

        # 3) apply patches back to canvas
        apply_updates(elements, updates)

        # 4) create new elements
        create_elements(creates)

        print("Done. Check your Excalidraw room; DB should be highlighted and labeled.")
        
        return {"feedback": feedback}

    except Exception as e:
        print(f"Error in check_diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting FastAPI server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)