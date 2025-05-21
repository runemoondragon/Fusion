from tools.base import BaseTool
from pathlib import Path
import os
import json
import re
from datetime import datetime

class N8nWorkflowCreator(BaseTool):
    name = "n8nworkflowcreator"
    description = """
    Generates an n8n-compatible workflow JSON code from a natural language description.
    The resulting JSON code can be saved to a file and ready for import into n8n.
    Leverages real node/action references from a local catalog and enforces complete logical flows.
    """
    input_schema = {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "Natural language description of the desired workflow"
            }
        },
        "required": ["description"]
    }

    def __init__(self):
        self.output_dir = Path("/mnt/data/generated-workflows")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_path = Path("tools/n8n-node-catalog.json")
        self.catalog = self._load_catalog()

    def _load_catalog(self):
        if self.catalog_path.exists():
            with open(self.catalog_path, 'r') as f:
                return json.load(f)
        return []

    def _slugify(self, text):
        return re.sub(r'[^a-zA-Z0-9_-]+', '-', text.lower())[:64]

    def _build_prompt(self, desc):
        known_nodes = ', '.join(sorted(set([n['name'] for n in self.catalog])))
        known_actions = ', '.join(sorted(set(a for node in self.catalog for a in node.get('actions', []))))
        return f"""
Generate a valid n8n workflow as a single JSON file. The workflow should match this description:

{desc}

Guidelines:
- The JSON must contain fields: `name`, `nodes`, `connections`.
- Use realistic node names and types (e.g., `telegramTrigger`, `httpRequest`, `gmail`, `googleCalendar`, etc.).
- Available node types include: {known_nodes}
- Known node actions include: {known_actions}
- Always use fully connected logic: no loose ends, no dangling `?` placeholders.
- Use nested Switch or IF nodes to route logic clearly.
- Include meta.description summarizing the flow purpose.

Return only raw valid JSON that is ready for import into n8n.
Do not preface, explain, or format the response.
This must be a single valid JSON object starting with `{{` and ending with `}}`.
Do not wrap it in markdown, code blocks, or comments.
"""

    def execute(self, **kwargs) -> str:
        desc = kwargs["description"]
        prompt = self._build_prompt(desc)

        try:
            response = self.llm.invoke(prompt)
            workflow_obj = json.loads(response.strip())

            filename = self._slugify(workflow_obj.get("name", "workflow-" + datetime.now().strftime("%Y%m%d%H%M%S"))) + ".json"
            filepath = self.output_dir / filename
            with open(filepath, "w") as f:
                json.dump(workflow_obj, f, indent=2)

            return f"✅ Workflow created: {filepath}"

        except json.JSONDecodeError as e:
            preview = response[:500] if isinstance(response, str) else str(response)
            return f"❌ Error: Could not decode JSON from LLM response: {str(e)}. Response preview: {preview}"
        except Exception as e:
            return f"❌ Error generating workflow: {str(e)}"
