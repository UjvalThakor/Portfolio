import logging
from typing import Dict, List, Any, Optional
from .knowledge_base import CentralKnowledgeBase
from .models import AvailabilityStatus, Conversation, Lead

logger = logging.getLogger(__name__)

# JSON schema declarations for OpenAI/Groq function calling
PORTFOLIO_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check Ujval's live, verified availability status for new projects, freelance, or full-time roles.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_projects",
            "description": "Retrieve Ujval's verified engineering projects. Can filter by technology (e.g. Django, OpenCV, Python) or category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "technology": {"type": "string", "description": "Specific technology to filter by, e.g. Python, OpenCV, Django"},
                    "category": {"type": "string", "description": "Category to filter by, e.g. AI, Computer Vision, Backend"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_detail",
            "description": "Get deep architectural details, problem statement, solution, and features of a specific project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "The name or slug of the project, e.g. beautycare-ai or fabric-fault-detection"}
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_skills",
            "description": "Retrieve Ujval's verified technical skills and proficiency levels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Optional category: backend, database, ai_cv, devops"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_services",
            "description": "Retrieve what services and systems Ujval can engineer for clients or companies.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_experience",
            "description": "Retrieve Ujval's verified academic background, computer engineering degree, and work history.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "qualify_lead",
            "description": "Save or update lead information collected from the visitor during conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Visitor's name"},
                    "email": {"type": "string", "description": "Visitor's email address"},
                    "company": {"type": "string", "description": "Visitor's company or organization name"},
                    "project_type": {"type": "string", "description": "Type of project (e.g. AI Vision, Django backend, API)"},
                    "requirements": {"type": "string", "description": "Details of the problem or requirements"},
                    "budget": {"type": "string", "description": "Budget range if mentioned"},
                    "timeline": {"type": "string", "description": "Desired delivery timeline if mentioned"},
                    "lead_type": {"type": "string", "enum": ["potential_client", "recruiter", "developer", "student", "general_visitor"]}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_human_contact",
            "description": "Trigger a request for Ujval to personally contact the visitor via email or phone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Visitor's name"},
                    "email": {"type": "string", "description": "Visitor's email address"},
                    "note": {"type": "string", "description": "Reason or message for Ujval"}
                },
                "required": ["email"]
            }
        }
    }
]


class PortfolioToolExecutor:
    """
    Executes tool calls server-side in a safe, controlled sandbox.
    Never allows arbitrary execution.
    """

    @classmethod
    def execute(cls, tool_name: str, arguments: Dict[str, Any], conversation: Optional[Conversation] = None) -> Dict[str, Any]:
        logger.info(f"Executing tool '{tool_name}' with args: {arguments}")
        try:
            if tool_name == "check_availability":
                return CentralKnowledgeBase.get_availability()

            elif tool_name == "get_projects":
                tech = arguments.get("technology")
                cat = arguments.get("category")
                projects = CentralKnowledgeBase.get_projects()
                if tech:
                    t_lower = tech.lower()
                    projects = [p for p in projects if any(t_lower in t.lower() for t in p.get('technologies', []))]
                if cat:
                    c_lower = cat.lower()
                    projects = [p for p in projects if c_lower in p.get('category', '').lower()]
                return {"projects": projects, "total_found": len(projects)}

            elif tool_name == "get_project_detail":
                p_name = arguments.get("project_name", "").lower()
                projects = CentralKnowledgeBase.get_projects()
                for p in projects:
                    if p_name in p.get('name', '').lower() or p_name in p.get('id', '').lower():
                        return {"project": p, "found": True}
                return {"found": False, "message": f"No project named '{p_name}' found in verified portfolio."}

            elif tool_name == "get_skills":
                cat = arguments.get("category")
                skills = CentralKnowledgeBase.get_skills(category=cat)
                return {"skills": skills, "total_found": len(skills)}

            elif tool_name == "get_services":
                return {"services": CentralKnowledgeBase.get_services()}

            elif tool_name == "get_experience":
                return CentralKnowledgeBase.get_experience()

            elif tool_name == "qualify_lead":
                if conversation:
                    from .lead_engine import LeadEngine
                    lead = LeadEngine.update_lead_from_data(conversation, arguments)
                    return {"success": True, "lead_id": lead.id, "score": lead.score, "temperature": lead.temperature}
                return {"success": True, "note": "No active conversation context to link lead"}

            elif tool_name == "request_human_contact":
                if conversation:
                    from .lead_engine import LeadEngine
                    lead = LeadEngine.trigger_human_handoff(conversation, arguments)
                    return {"success": True, "handoff_created": True, "lead_id": lead.id if lead else None}
                return {"success": True, "note": "Contact request noted"}

            else:
                return {"error": f"Unknown tool '{tool_name}'"}

        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}", exc_info=True)
            return {"error": f"Tool execution failed: {str(e)}"}
