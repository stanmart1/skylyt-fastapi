from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.car_image import CarImage
from app.models.car import Car
import uuid
import os
from pathlib import Path
import requests

router = APIRouter(prefix="/car-images", tags=["car-images"])


@router.post("/upload")
async def upload_car_images(
    car_id: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple images for a car"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify car exists
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    uploaded_images = []
    upload_dir = Path("uploads/cars")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {file.filename}. Only JPEG and PNG allowed.")
        
        # Validate file size (5MB)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large: {file.filename}. Maximum 5MB allowed.")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.jpg', '.jpeg', '.png']:
            file_extension = '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Validate filename
        if '..' in unique_filename or '/' in unique_filename or '\\' in unique_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = upload_dir / unique_filename
        
        # Ensure file path is within upload directory
        try:
            file_path = file_path.resolve()
            if not str(file_path).startswith(str(upload_dir.resolve())):
                raise HTTPException(status_code=400, detail="Invalid file path")
        except (OSError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Get next display order
        max_order = db.query(CarImage).filter(CarImage.car_id == car_id).count()
        
        # Create database record
        car_image = CarImage(
            car_id=car_id,
            image_url=f"/uploads/cars/{unique_filename}",
            display_order=max_order + 1
        )
        db.add(car_image)
        uploaded_images.append({
            "id": car_image.id,
            "filename": file.filename,
            "url": car_image.image_url
        })
    
    db.commit()
    return {"message": f"Uploaded {len(uploaded_images)} images", "images": uploaded_images}


@router.post("/upload-url")
async def upload_car_image_from_url(
    car_id: str = Form(...),
    image_url: str = Form(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload car image from URL"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify car exists
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Validate URL to prevent SSRF
    from urllib.parse import urlparse
    import ipaddress
    
    parsed_url = urlparse(image_url)
    if parsed_url.scheme not in ['http', 'https']:
        raise HTTPException(status_code=400, detail="Only HTTP/HTTPS URLs allowed")
    
    # Block internal/private IPs
    hostname = parsed_url.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
            raise HTTPException(status_code=400, detail="Private/internal URLs not allowed")
    except ValueError:
        if hostname.lower() in ['localhost', 'metadata.google.internal'] or hostname.startswith('169.254.'):
            raise HTTPException(status_code=400, detail="Internal URLs not allowed")
    
    if parsed_url.port and parsed_url.port not in [80, 443, 8080, 8443]:
        raise HTTPException(status_code=400, detail="Only standard HTTP/HTTPS ports allowed")
    
    try:
        # Download image
        response = requests.get(
            image_url, 
            timeout=10, 
            allow_redirects=False,
            headers={'User-Agent': 'Skylyt-ImageBot/1.0'},
            stream=True
        )
        response.raise_for_status()
        
        # Validate content type
        content_type = response.headers.get('content-type', '')
        if content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid image type. Only JPEG and PNG allowed.")
        
        # Validate size
        if len(response.content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large. Maximum 5MB allowed.")
        
        # Save file
        upload_dir = Path("uploads/cars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = ".jpg" if "jpeg" in content_type else ".png"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        # Get next display order
        max_order = db.query(CarImage).filter(CarImage.car_id == car_id).count()
        
        # Create database record
        car_image = CarImage(
            car_id=car_id,
            image_url=f"/uploads/cars/{unique_filename}",
            display_order=max_order + 1
        )
        db.add(car_image)
        db.commit()
        
        return {"message": "Image uploaded successfully", "image": {"id": car_image.id, "url": car_image.image_url}}
        
    except requests.RequestException:
        raise HTTPException(status_code=400, detail="Failed to download image from URL")


@router.get("/{car_id}")
def get_car_images(
    car_id: str,
    db: Session = Depends(get_db)
):
    """Get all images for a car"""
    images = db.query(CarImage).filter(CarImage.car_id == car_id)\
        .order_by(CarImage.display_order).all()
    return {"images": images}


@router.put("/{image_id}/cover")
def set_cover_image(
    image_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set image as cover image"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    image = db.query(CarImage).filter(CarImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Remove cover status from other images of the same car
    db.query(CarImage).filter(CarImage.car_id == image.car_id)\
        .update({"is_cover": False})
    
    # Set this image as cover
    image.is_cover = True
    db.commit()
    
    return {"message": "Cover image updated"}


@router.delete("/{image_id}")
def delete_car_image(
    image_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete car image"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    image = db.query(CarImage).filter(CarImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete file with path validation
    try:
        if not image.image_url.startswith('/uploads/cars/'):
            raise HTTPException(status_code=400, detail="Invalid image path")
        
        filename = os.path.basename(image.image_url)
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        base_path = Path("uploads/cars").resolve()
        file_path = base_path / filename
        
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(base_path)):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        if file_path.exists():
            file_path.unlink()
    except (OSError, ValueError):
        pass
    
    # Delete database record
    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}


@router.put("/reorder")
def reorder_car_images(
    image_orders: List[dict],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder car images"""
    if not (current_user.is_admin() or current_user.is_superadmin()):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate input data
    for item in image_orders:
        if not item.get("id") or item.get("order") is None:
            raise HTTPException(status_code=400, detail="Invalid reorder data")
    
    # Bulk update
    from sqlalchemy import case
    image_ids = [item["id"] for item in image_orders]
    order_mapping = {item["id"]: item["order"] for item in image_orders}
    
    db.query(CarImage).filter(CarImage.id.in_(image_ids)).update({
        CarImage.display_order: case(order_mapping, value=CarImage.id)
    }, synchronize_session=False)
    
    db.commit()
    return {"message": "Images reordered successfully"}