import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import io

from sqlalchemy.orm import Session
from backend.config import settings
from backend.models import Detection, DetectionResult
from backend.roboflow_service import roboflow_service
from backend.disease_info import get_disease_info

COLOR_MAP = {
    "High": "#d90429",     # Red
    "Medium": "#f77f00",   # Amber / Orange
    "Low": "#2a9d8f",      # Emerald Green
    "Healthy": "#2a9d8f"
}

def determine_severity(class_name: str) -> str:
    info = get_disease_info(class_name)
    return info.get("severity", "Medium")

def draw_bounding_boxes(
    image_bytes: bytes,
    predictions: List[Dict[str, Any]],
    confidence_threshold: float
) -> Tuple[bytes, List[Dict[str, Any]]]:
    """
    Draws bounding boxes on PIL Image based on Roboflow predictions.
    Roboflow prediction format:
    x, y (center of box in pixels), width, height (in pixels), class, confidence
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size

    # Try loading font, fallback to default if truetype not available
    try:
        font = ImageFont.truetype("arial.ttf", size=max(14, int(img_h * 0.025)))
    except IOError:
        font = ImageFont.load_default()

    filtered_predictions = []

    for pred in predictions:
        conf = float(pred.get("confidence", 0.0))
        if conf < confidence_threshold:
            continue

        class_name = str(pred.get("class", "Unknown"))
        cx = float(pred.get("x", 0))
        cy = float(pred.get("y", 0))
        w = float(pred.get("width", 0))
        h = float(pred.get("height", 0))

        # Convert center x, y, w, h to box coordinates [xmin, ymin, xmax, ymax]
        xmin = max(0, cx - (w / 2))
        ymin = max(0, cy - (h / 2))
        xmax = min(img_w, cx + (w / 2))
        ymax = min(img_h, cy + (h / 2))

        severity = determine_severity(class_name)
        box_color = COLOR_MAP.get(severity, "#f77f00")

        # Line thickness relative to image size
        line_width = max(3, int(min(img_w, img_h) * 0.005))
        
        # Draw bounding box
        draw.rectangle([xmin, ymin, xmax, ymax], outline=box_color, width=line_width)

        # Draw label background box
        label_text = f"{class_name.title()} {conf*100:.1f}%"
        
        # Get text bounding box for background rectangle
        try:
            bbox = font.getbbox(label_text)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(label_text, font=font) if hasattr(draw, "textsize") else (100, 20)

        padding = 4
        label_xmin = xmin
        label_ymin = max(0, ymin - text_h - (padding * 2))
        label_xmax = label_xmin + text_w + (padding * 2)
        label_ymax = label_ymin + text_h + (padding * 2)

        draw.rectangle([label_xmin, label_ymin, label_xmax, label_ymax], fill=box_color)
        draw.text((label_xmin + padding, label_ymin + padding), label_text, fill="white", font=font)

        filtered_predictions.append({
            "class_name": class_name,
            "confidence": conf,
            "x": cx,
            "y": cy,
            "width": w,
            "height": h,
            "severity": severity
        })

    output_buffer = io.BytesIO()
    image.save(output_buffer, format="JPEG", quality=90)
    annotated_bytes = output_buffer.getvalue()

    return annotated_bytes, filtered_predictions

def process_detection(
    db: Session,
    filename: str,
    image_bytes: bytes,
    confidence_threshold: float = 0.5,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Main detection orchestration function:
    1. Saves original image to uploads.
    2. Runs Roboflow AI inference.
    3. Annotates bounding boxes.
    4. Saves detection and individual results to SQLite.
    5. Returns formatted response dictionary with localized disease info.
    """
    file_id = str(uuid.uuid4())[:8]
    sanitized_filename = f"{file_id}_{filename.replace(' ', '_')}"
    
    original_rel_path = f"original_{sanitized_filename}"
    annotated_rel_path = f"annotated_{sanitized_filename}"

    original_abs_path = os.path.join(settings.UPLOADS_DIR, original_rel_path)
    annotated_abs_path = os.path.join(settings.UPLOADS_DIR, annotated_rel_path)

    # Save original image
    with open(original_abs_path, "wb") as f:
        f.write(image_bytes)

    # Infer via Roboflow
    success, raw_predictions, error_msg = roboflow_service.infer_image(image_bytes, confidence_threshold)

    # Annotate image
    annotated_bytes, predictions = draw_bounding_boxes(image_bytes, raw_predictions, confidence_threshold)

    # Save annotated image
    with open(annotated_abs_path, "wb") as f:
        f.write(annotated_bytes)

    # Calculate status and primary disease
    if predictions:
        # Check if any disease detected
        diseased_preds = [p for p in predictions if p["class_name"].lower() != "healthy"]
        if diseased_preds:
            status = "Diseased"
            # Primary disease is highest confidence disease
            top_pred = max(diseased_preds, key=lambda x: x["confidence"])
            primary_disease = top_pred["class_name"].title()
        else:
            status = "Healthy"
            top_pred = max(predictions, key=lambda x: x["confidence"])
            primary_disease = "Healthy"

        max_confidence = top_pred["confidence"]
        total_detections = len(predictions)
    else:
        status = "Healthy"
        primary_disease = "Healthy"
        max_confidence = 0.0
        total_detections = 0

    # Save to SQLite Database
    db_detection = Detection(
        filename=filename,
        original_image_path=f"/uploads/{original_rel_path}",
        annotated_image_path=f"/uploads/{annotated_rel_path}",
        timestamp=datetime.utcnow(),
        status=status,
        total_detections=total_detections,
        primary_disease=primary_disease,
        max_confidence=max_confidence,
        confidence_threshold=confidence_threshold
    )
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)

    # Save individual bounding box result rows
    for p in predictions:
        res = DetectionResult(
            detection_id=db_detection.id,
            class_name=p["class_name"],
            confidence=p["confidence"],
            x=p["x"],
            y=p["y"],
            width=p["width"],
            height=p["height"],
            severity=p["severity"]
        )
        db.add(res)
    db.commit()

    # Collect localized disease details map
    disease_details = {}
    detected_classes = set(p["class_name"] for p in predictions) if predictions else {"healthy"}
    for cls in detected_classes:
        disease_details[cls] = get_disease_info(cls, language=language)

    return {
        "success": True,
        "detection_id": db_detection.id,
        "filename": filename,
        "timestamp": db_detection.timestamp,
        "status": status,
        "total_detections": total_detections,
        "primary_disease": primary_disease,
        "max_confidence": max_confidence,
        "confidence_threshold": confidence_threshold,
        "original_image_url": f"{settings.BACKEND_URL}/uploads/{original_rel_path}",
        "annotated_image_url": f"{settings.BACKEND_URL}/uploads/{annotated_rel_path}",
        "detections": predictions,
        "disease_details": disease_details,
        "warning": error_msg if not success else None
    }
