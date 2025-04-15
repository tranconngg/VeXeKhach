from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List
from bson import ObjectId

from app.database import db
from app import schemas

router = APIRouter()

def get_route_collection():
    return db["routes"]

def get_bus_collection():
    return db["buses"]

def get_seat_collection():
    return db["seats"]

@router.post("/routes", response_model=schemas.RouteResponse)
async def create_route(route: schemas.RouteCreate):
    route_collection = get_route_collection()
    
    route_dict = route.dict()
    route_dict["created_at"] = datetime.utcnow()
    
    result = await route_collection.insert_one(route_dict)
    created_route = await route_collection.find_one({"_id": result.inserted_id})
    created_route["id"] = str(created_route["_id"])
    del created_route["_id"]
    return schemas.RouteResponse(**created_route)

@router.post("/buses", response_model=schemas.BusResponse)
async def create_bus(bus: schemas.BusCreate):
    bus_collection = get_bus_collection()
    route_collection = get_route_collection()
    
    try:
        route = await route_collection.find_one({"_id": ObjectId(bus.route_id)})
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid route ID format")
    bus_dict = bus.dict()
    bus_dict["created_at"] = datetime.utcnow()
    result = await bus_collection.insert_one(bus_dict)
    
    created_bus = await bus_collection.find_one({"_id": result.inserted_id})
    created_bus["id"] = str(created_bus["_id"])
    del created_bus["_id"]
    return schemas.BusResponse(**created_bus)

@router.get("/routes", response_model=List[schemas.RouteResponse])
async def get_routes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    departure: str = None,
    destination: str = None
):
    route_collection = get_route_collection()
    
    # Xây dựng query filter
    query = {}
    if departure:
        query["departure"] = {"$regex": departure, "$options": "i"}
    if destination:
        query["destination"] = {"$regex": destination, "$options": "i"}
    
    # Thực hiện truy vấn với phân trang
    routes = await route_collection.find(query).skip(skip).limit(limit).to_list(length=limit)
    formatted_routes = []
    for route in routes:
        route["id"] = str(route["_id"])
        del route["_id"]
        formatted_routes.append(schemas.RouteResponse(**route))
    return formatted_routes

@router.get("/buses", response_model=List[schemas.BusResponse])
async def get_buses(
    route_id: str = None,
    date: datetime = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    bus_collection = get_bus_collection()
    
    # Xây dựng query filter
    query = {}
    if route_id:
        query["route_id"] = route_id
    if date:
        # Lọc xe theo ngày khởi hành
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        query["departure_time"] = {"$gte": start_of_day, "$lte": end_of_day}
    # Thực hiện truy vấn với phân trang
    buses = await bus_collection.find(query).skip(skip).limit(limit).to_list(length=limit)
    formatted_buses = []
    for bus in buses:
        bus["id"] = str(bus["_id"])
        del bus["_id"]
        formatted_buses.append(schemas.BusResponse(**bus))
    return formatted_buses

@router.get("/buses/{bus_id}", response_model=schemas.BusResponse)
async def get_bus_detail(bus_id: str):
    bus_collection = get_bus_collection()
    
    try:
        bus = await bus_collection.find_one({"_id": ObjectId(bus_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid bus ID format")
        
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    bus["id"] = str(bus["_id"])
    del bus["_id"]
    return schemas.BusResponse(**bus)

@router.post("/buses/{bus_id}/seats", response_model=List[schemas.SeatResponse])
async def create_bus_seats(bus_id: str):
    bus_collection = get_bus_collection()
    seat_collection = get_seat_collection()
    route_collection = get_route_collection()
    
    try:
        bus = await bus_collection.find_one({"_id": ObjectId(bus_id)})
        if not bus:
            raise HTTPException(status_code=404, detail="Bus not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid bus ID format")
    
    # Kiểm tra xem đã có ghế nào được tạo chưa
    existing_seats = await seat_collection.find({"bus_id": bus_id}).to_list(length=100)
    if existing_seats:
        raise HTTPException(status_code=400, detail="Seats already created for this bus")
    
    # Lấy thông tin route để lấy giá vé
    route = await route_collection.find_one({"_id": ObjectId(bus["route_id"])})
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Tạo danh sách ghế dựa trên capacity của xe
    seats_to_create = []
    for i in range(1, bus["capacity"] + 1):
        seat_dict = {
            "seat_number": f"A{i:02d}",  # Format: A01, A02, ...
            "bus_id": bus_id,
            "is_available": True,
            "price": route["price"],  # Lấy giá từ route
            "created_at": datetime.utcnow()
        }
        seats_to_create.append(seat_dict)
    result = await seat_collection.insert_many(seats_to_create)
    created_seats = await seat_collection.find({"bus_id": bus_id}).to_list(length=100)

    formatted_seats = []
    for seat in created_seats:
        seat["id"] = str(seat["_id"])
        del seat["_id"]
        formatted_seats.append(schemas.SeatResponse(**seat))
    return formatted_seats

@router.get("/buses/{bus_id}/seats", response_model=List[schemas.SeatResponse])
async def get_bus_seats(bus_id: str):
    seat_collection = get_seat_collection()
    try:
        seats = await seat_collection.find({"bus_id": bus_id}).to_list(length=100)
    except:
        raise HTTPException(status_code=400, detail="Invalid bus ID format")
    
    if not seats:
        raise HTTPException(status_code=404, detail="No seats found for this bus")
    
    formatted_seats = []
    for seat in seats:
        seat["id"] = str(seat["_id"])
        del seat["_id"]
        formatted_seats.append(schemas.SeatResponse(**seat))
    
    return formatted_seats