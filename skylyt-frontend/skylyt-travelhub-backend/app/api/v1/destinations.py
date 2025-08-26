from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.state import State
from app.models.city import City
from app.models.hotel import Hotel

router = APIRouter(prefix="/destinations", tags=["destinations"])


@router.get("/states")
def get_states(
    featured_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all states or featured states only"""
    query = db.query(State)
    if featured_only:
        query = query.filter(State.is_featured == 1)
    
    states = query.order_by(State.popularity_score.desc()).all()
    return {"states": states}


@router.get("/{state_slug}/cities")
def get_cities_in_state(
    state_slug: str,
    db: Session = Depends(get_db)
):
    """Get all cities within a specific state"""
    state = db.query(State).filter(State.slug == state_slug).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    cities = db.query(City).filter(City.state_id == state.id)\
        .order_by(City.popularity_ranking.asc()).all()
    
    return {
        "state": state,
        "cities": cities
    }


@router.get("/{state_slug}/hotels")
def get_hotels_in_state(
    state_slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all hotels within a specific state"""
    state = db.query(State).filter(State.slug == state_slug).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    offset = (page - 1) * per_page
    hotels = db.query(Hotel).filter(Hotel.state_id == state.id)\
        .offset(offset).limit(per_page).all()
    
    total = db.query(Hotel).filter(Hotel.state_id == state.id).count()
    
    return {
        "state": state,
        "hotels": hotels,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/{state_slug}/{city_slug}/hotels")
def get_hotels_in_city(
    state_slug: str,
    city_slug: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("rating", regex="^(rating|price|popularity)$"),
    db: Session = Depends(get_db)
):
    """Get hotels specific to a city"""
    state = db.query(State).filter(State.slug == state_slug).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    city = db.query(City).filter(
        City.slug == city_slug,
        City.state_id == state.id
    ).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    query = db.query(Hotel).filter(Hotel.city_id == city.id)
    
    # Apply sorting
    if sort_by == "rating":
        query = query.order_by(Hotel.star_rating.desc())
    elif sort_by == "price":
        query = query.order_by(Hotel.price_per_night.asc())
    else:  # popularity
        query = query.order_by(Hotel.is_featured.desc())
    
    offset = (page - 1) * per_page
    hotels = query.offset(offset).limit(per_page).all()
    total = db.query(Hotel).filter(Hotel.city_id == city.id).count()
    
    return {
        "state": state,
        "city": city,
        "hotels": hotels,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/{state_slug}")
def get_state_details(
    state_slug: str,
    db: Session = Depends(get_db)
):
    """Get state details with cities overview"""
    state = db.query(State).filter(State.slug == state_slug).first()
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    cities = db.query(City).filter(City.state_id == state.id)\
        .order_by(City.popularity_ranking.asc()).limit(12).all()
    
    return {
        "state": state,
        "featured_cities": cities
    }