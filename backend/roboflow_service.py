import base64
import logging
import requests
from typing import List, Dict, Any, Tuple
from backend.config import settings

logger = logging.getLogger("cococare.roboflow")

class RoboflowService:
    def __init__(self):
        self.api_key = settings.ROBOFLOW_API_KEY
        self.model_name = settings.ROBOFLOW_MODEL
        self.version = settings.ROBOFLOW_VERSION
        
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_roboflow_api_key_here")

    def infer_image(self, image_bytes: bytes, confidence_threshold: float = 0.5) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Sends image bytes to Roboflow hosted endpoint for object detection.
        Returns: (success: bool, predictions: list, error_message: str)
        """
        if not self.is_configured():
            logger.warning("Roboflow API Key is missing or invalid.")
            return False, [], "Roboflow API Key is not configured. Please set ROBOFLOW_API_KEY in your .env or Settings page."

        # Convert threshold from 0-1 to 0-100 percentage integer if required by endpoint
        conf_int = int(confidence_threshold * 100)
        url = f"https://detect.roboflow.com/{self.model_name}/{self.version}?api_key={self.api_key}&confidence={conf_int}"

        try:
            # Base64 encode the image payload
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            
            response = requests.post(
                url,
                data=base64_image,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=12
            )

            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", [])
                logger.info(f"Roboflow returned {len(predictions)} predictions.")
                return True, predictions, ""
            elif response.status_code in (401, 403):
                msg = f"Roboflow API Authentication failed (HTTP {response.status_code}). Please check your API key."
                logger.error(msg)
                return False, [], msg
            else:
                msg = f"Roboflow API error (HTTP {response.status_code}): {response.text[:200]}"
                logger.error(msg)
                return False, [], msg

        except requests.exceptions.Timeout:
            return False, [], "Roboflow service request timed out after 12 seconds."
        except requests.exceptions.RequestException as e:
            return False, [], f"Network error connecting to Roboflow API: {str(e)}"
        except Exception as e:
            return False, [], f"Unexpected error during AI inference: {str(e)}"

roboflow_service = RoboflowService()
