import requests
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        """Check connection to FastAPI backend."""
        try:
            res = requests.get(f"{self.base_url}/api/health", timeout=4)
            if res.status_code == 200:
                return res.json()
            return {"status": "unhealthy", "error": f"HTTP {res.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"status": "offline", "error": f"Cannot connect to backend at {self.base_url}"}

    def detect_disease(self, file_bytes: bytes, filename: str, confidence: float = 0.5, language: str = "en") -> Dict[str, Any]:
        """Post uploaded image file to backend /api/detect endpoint."""
        url = f"{self.base_url}/api/detect"
        params = {"confidence": confidence, "language": language}
        files = {"file": (filename, file_bytes, "image/jpeg")}

        try:
            res = requests.post(url, params=params, files=files, timeout=20)
            if res.status_code == 200:
                return res.json()
            else:
                try:
                    err_detail = res.json().get("detail", res.text)
                except Exception:
                    err_detail = res.text
                return {"success": False, "error": f"Backend Error (HTTP {res.status_code}): {err_detail}"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Detection request timed out after 20 seconds."}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Failed to connect to FastAPI backend: {str(e)}"}

    def get_history(self, limit: int = 50, search: Optional[str] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch detection scan history."""
        url = f"{self.base_url}/api/history"
        params = {"limit": limit}
        if search:
            params["search"] = search
        if status_filter:
            params["status_filter"] = status_filter

        try:
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                return res.json()
            return []
        except Exception:
            return []

    def get_history_detail(self, detection_id: int) -> Optional[Dict[str, Any]]:
        """Fetch detailed scan record."""
        url = f"{self.base_url}/api/history/{detection_id}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    def delete_history_item(self, detection_id: int) -> Dict[str, Any]:
        """Delete single detection scan."""
        url = f"{self.base_url}/api/history/{detection_id}"
        try:
            res = requests.delete(url, timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "message": f"Failed to delete record (HTTP {res.status_code})"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def clear_all_history(self) -> Dict[str, Any]:
        """Clear all detection history."""
        url = f"{self.base_url}/api/history/clear-all"
        try:
            res = requests.delete(url, timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "message": f"Failed to clear history (HTTP {res.status_code})"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """Fetch analytics statistics."""
        url = f"{self.base_url}/api/statistics"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return res.json()
            return {}
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Chat (Multilingual Groq AI Assistant)
    # ------------------------------------------------------------------
    def send_chat_message(
        self,
        message: str,
        language: str = "en",
        history: Optional[list] = None,
        user_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a chat message to the CoconutCare AI assistant."""
        url = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {"message": message, "language": language}
        if history:
            payload["history"] = history
        if user_context:
            payload["user_context"] = user_context

        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "reply": f"Error (HTTP {res.status_code})"}
        except requests.exceptions.Timeout:
            return {"success": False, "reply": "Request timed out. Please try again."}
        except requests.exceptions.RequestException as e:
            return {"success": False, "reply": f"Connection error: {str(e)}"}

    # ------------------------------------------------------------------
    # Auth & Language Preference
    # ------------------------------------------------------------------
    def signup(self, username: str, password: str, preferred_language: str = "en") -> Dict[str, Any]:
        """Register a new user."""
        url = f"{self.base_url}/api/auth/signup"
        try:
            res = requests.post(url, json={
                "username": username,
                "password": password,
                "preferred_language": preferred_language,
            }, timeout=5)
            if res.status_code == 200:
                return res.json()
            try:
                return {"error": res.json().get("detail", "Signup failed")}
            except Exception:
                return {"error": f"Signup failed (HTTP {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return profile."""
        url = f"{self.base_url}/api/auth/login"
        try:
            res = requests.post(url, json={
                "username": username,
                "password": password,
            }, timeout=5)
            if res.status_code == 200:
                return res.json()
            try:
                return {"error": res.json().get("detail", "Login failed")}
            except Exception:
                return {"error": f"Login failed (HTTP {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user profile (includes preferred_language)."""
        url = f"{self.base_url}/api/auth/me/{user_id}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    def update_language(self, user_id: int, language: str) -> Dict[str, Any]:
        """Update user's preferred language."""
        url = f"{self.base_url}/api/auth/language"
        try:
            res = requests.patch(
                url,
                json={"preferred_language": language},
                params={"user_id": user_id},
                timeout=5,
            )
            if res.status_code == 200:
                return res.json()
            return {"error": f"Failed to update language (HTTP {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Farm Profile & Setup
    # ------------------------------------------------------------------
    def get_farm(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch farm profile by user ID."""
        url = f"{self.base_url}/api/farm/user/{user_id}"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception:
            return None

    def create_farm(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or replace farm profile."""
        url = f"{self.base_url}/api/farm"
        try:
            res = requests.post(url, json=farm_data, timeout=5)
            if res.status_code == 200:
                return res.json()
            try:
                return {"error": res.json().get("detail", "Failed to save farm profile")}
            except Exception:
                return {"error": f"Failed to save farm profile (HTTP {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

    def update_farm(self, farm_id: int, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update farm profile."""
        url = f"{self.base_url}/api/farm/{farm_id}"
        try:
            res = requests.put(url, json=farm_data, timeout=5)
            if res.status_code == 200:
                return res.json()
            try:
                return {"error": res.json().get("detail", "Failed to update farm profile")}
            except Exception:
                return {"error": f"Failed to update farm profile (HTTP {res.status_code})"}
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Phase 2 — Irrigation, Soil, Fertilizer & Calendar
    # ------------------------------------------------------------------
    def create_irrigation_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/irrigation"
        try:
            res = requests.post(url, json=data, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def get_irrigation_history(self, farm_id: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/irrigation/farm/{farm_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def update_irrigation_status(self, record_id: int, status: str = "COMPLETED") -> Dict[str, Any]:
        url = f"{self.base_url}/api/irrigation/{record_id}/status"
        try:
            res = requests.patch(url, params={"status": status}, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def create_soil_test(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/soil"
        try:
            res = requests.post(url, json=data, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def get_soil_history(self, farm_id: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/soil/farm/{farm_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def get_soil_interpretations(self, ph: float, n: float, p: float, k: float, oc: float) -> Dict[str, Any]:
        url = f"{self.base_url}/api/soil/interpretation"
        params = {"ph": ph, "n": n, "p": p, "k": k, "oc": oc}
        try:
            res = requests.get(url, params=params, timeout=5)
            return res.json() if res.status_code == 200 else {}
        except Exception:
            return {}

    def get_fertilizer_templates(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/fertilizer/templates"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else {}
        except Exception:
            return {}

    def get_farm_calendar(self, farm_id: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/calendar/farm/{farm_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def create_farm_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/calendar"
        try:
            res = requests.post(url, json=data, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def update_activity_status(self, activity_id: int, status: str = "COMPLETED") -> Dict[str, Any]:
        url = f"{self.base_url}/api/calendar/{activity_id}/status"
        try:
            res = requests.patch(url, params={"status": status}, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Phase 3 — Expenses, Blocks & Growth Tracker
    # ------------------------------------------------------------------
    def create_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/expenses"
        try:
            res = requests.post(url, json=data, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def get_expenses(self, farm_id: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/expenses/farm/{farm_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def get_expense_summary(self, farm_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/expenses/summary/farm/{farm_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else {}
        except Exception:
            return {}

    def delete_expense(self, expense_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/api/expenses/{expense_id}"
        try:
            res = requests.delete(url, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def create_farm_block(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/blocks"
        try:
            res = requests.post(url, json=data, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def get_farm_blocks(self, farm_id: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/blocks/farm/{farm_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []

    def create_growth_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/growth"
        try:
            res = requests.post(url, json=data, timeout=5)
            return res.json() if res.status_code == 200 else {"error": res.text}
        except Exception as e:
            return {"error": str(e)}

    def get_growth_timeline(self, block_id: int) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/growth/block/{block_id}"
        try:
            res = requests.get(url, timeout=5)
            return res.json() if res.status_code == 200 else []
        except Exception:
            return []


    # ------------------------------------------------------------------
    # Phase 4 — Weather Integration & Block Scanning Link
    # ------------------------------------------------------------------
    def get_weather(self, location: str = "Pollachi") -> Dict[str, Any]:
        """Fetch live weather metrics and generic advisories."""
        url = f"{self.base_url}/api/weather"
        try:
            res = requests.get(url, params={"location": location}, timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "error": f"HTTP {res.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def link_detection_to_block(self, detection_id: int, block_id: Optional[int] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        """Link a detection scan to a specific farm block and attach notes."""
        url = f"{self.base_url}/api/history/{detection_id}/link"
        payload = {}
        if block_id is not None:
            payload["block_id"] = block_id
        if notes is not None:
            payload["farmer_notes"] = notes
        try:
            res = requests.patch(url, json=payload, timeout=5)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "error": f"HTTP {res.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


api_client = APIClient()





