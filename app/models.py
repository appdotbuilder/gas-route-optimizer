from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for type safety
class FuelType(str, Enum):
    REGULAR = "regular"
    MIDGRADE = "midgrade"
    PREMIUM = "premium"
    DIESEL = "diesel"
    E85 = "e85"


class StationBrand(str, Enum):
    SHELL = "shell"
    EXXON = "exxon"
    CHEVRON = "chevron"
    BP = "bp"
    MOBIL = "mobil"
    TEXACO = "texaco"
    ARCO = "arco"
    CITGO = "citgo"
    SUNOCO = "sunoco"
    SPEEDWAY = "speedway"
    WAWA = "wawa"
    INDEPENDENT = "independent"
    OTHER = "other"


class RouteStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    SAVED = "saved"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(unique=True, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # User preferences stored as JSON
    preferences: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    routes: List["Route"] = Relationship(back_populates="user")
    ratings: List["StationRating"] = Relationship(back_populates="user")
    favorites: List["UserFavorite"] = Relationship(back_populates="user")


class GasStation(SQLModel, table=True):
    __tablename__ = "gas_stations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    brand: StationBrand = Field(default=StationBrand.INDEPENDENT)
    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=50)
    zip_code: str = Field(max_length=20)
    country: str = Field(default="US", max_length=10)

    # Geographic coordinates
    latitude: Decimal = Field(decimal_places=8, max_digits=11)
    longitude: Decimal = Field(decimal_places=8, max_digits=11)

    # Contact and operational info
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=500)
    operating_hours: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Station features and amenities
    amenities: List[str] = Field(default=[], sa_column=Column(JSON))
    has_car_wash: bool = Field(default=False)
    has_convenience_store: bool = Field(default=False)
    has_air_pump: bool = Field(default=False)
    has_restrooms: bool = Field(default=False)
    has_atm: bool = Field(default=False)
    accepts_credit_cards: bool = Field(default=True)

    # Ratings and reviews
    average_rating: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=3)
    total_ratings: int = Field(default=0)

    # Metadata
    is_active: bool = Field(default=True)
    verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    fuel_prices: List["FuelPrice"] = Relationship(back_populates="station")
    ratings: List["StationRating"] = Relationship(back_populates="station")
    route_stops: List["RouteStop"] = Relationship(back_populates="station")
    favorites: List["UserFavorite"] = Relationship(back_populates="station")


class FuelPrice(SQLModel, table=True):
    __tablename__ = "fuel_prices"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(foreign_key="gas_stations.id")
    fuel_type: FuelType
    price_per_gallon: Decimal = Field(decimal_places=3, max_digits=6)

    # Price tracking
    price_date: datetime = Field(default_factory=datetime.utcnow)
    is_current: bool = Field(default=True)

    # Data source info
    source: str = Field(default="user_reported", max_length=100)
    verified: bool = Field(default=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    station: GasStation = Relationship(back_populates="fuel_prices")


class StationRating(SQLModel, table=True):
    __tablename__ = "station_ratings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(foreign_key="gas_stations.id")
    user_id: int = Field(foreign_key="users.id")

    # Rating details
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    review: Optional[str] = Field(default=None, max_length=1000)

    # Rating categories
    fuel_quality: Optional[int] = Field(default=None, ge=1, le=5)
    service_quality: Optional[int] = Field(default=None, ge=1, le=5)
    cleanliness: Optional[int] = Field(default=None, ge=1, le=5)
    price_rating: Optional[int] = Field(default=None, ge=1, le=5)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    station: GasStation = Relationship(back_populates="ratings")
    user: User = Relationship(back_populates="ratings")


class Route(SQLModel, table=True):
    __tablename__ = "routes"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    # Route metadata
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: RouteStatus = Field(default=RouteStatus.DRAFT)

    # Route optimization settings
    optimization_criteria: str = Field(default="distance", max_length=50)  # distance, time, price
    start_location: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    end_location: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Route statistics
    total_distance_miles: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    estimated_duration_minutes: Optional[int] = Field(default=None)
    estimated_fuel_cost: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)

    # Route data
    optimized_path: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    traffic_conditions: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Metadata
    is_favorite: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="routes")
    stops: List["RouteStop"] = Relationship(back_populates="route", cascade_delete=True)


class RouteStop(SQLModel, table=True):
    __tablename__ = "route_stops"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    route_id: int = Field(foreign_key="routes.id")
    station_id: int = Field(foreign_key="gas_stations.id")

    # Stop ordering and details
    stop_order: int = Field(ge=1)
    is_visited: bool = Field(default=False)

    # Stop-specific preferences
    fuel_types_needed: List[str] = Field(default=[], sa_column=Column(JSON))
    estimated_fuel_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=6)

    # Navigation data
    distance_from_previous: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    travel_time_minutes: Optional[int] = Field(default=None)
    arrival_time: Optional[datetime] = Field(default=None)

    # Visit tracking
    visited_at: Optional[datetime] = Field(default=None)
    actual_fuel_purchased: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=6)
    actual_cost: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    route: Route = Relationship(back_populates="stops")
    station: GasStation = Relationship(back_populates="route_stops")


class UserFavorite(SQLModel, table=True):
    __tablename__ = "user_favorites"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    station_id: int = Field(foreign_key="gas_stations.id")

    # Favorite metadata
    nickname: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="favorites")
    station: GasStation = Relationship(back_populates="favorites")


class TrafficCondition(SQLModel, table=True):
    __tablename__ = "traffic_conditions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)

    # Geographic area
    start_latitude: Decimal = Field(decimal_places=8, max_digits=11)
    start_longitude: Decimal = Field(decimal_places=8, max_digits=11)
    end_latitude: Decimal = Field(decimal_places=8, max_digits=11)
    end_longitude: Decimal = Field(decimal_places=8, max_digits=11)

    # Traffic data
    normal_travel_time_minutes: int
    current_travel_time_minutes: int
    traffic_factor: Decimal = Field(decimal_places=2, max_digits=4)  # multiplier (1.0 = normal)

    # Condition details
    traffic_level: str = Field(max_length=20)  # light, moderate, heavy, severe
    incidents: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Data freshness
    data_timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    source: str = Field(default="api", max_length=50)

    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    preferences: Dict[str, Any] = Field(default={})


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    preferences: Optional[Dict[str, Any]] = Field(default=None)


class GasStationCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    brand: StationBrand = Field(default=StationBrand.INDEPENDENT)
    address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=50)
    zip_code: str = Field(max_length=20)
    latitude: Decimal
    longitude: Decimal
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=500)
    operating_hours: Dict[str, Any] = Field(default={})
    amenities: List[str] = Field(default=[])
    has_car_wash: bool = Field(default=False)
    has_convenience_store: bool = Field(default=False)
    has_air_pump: bool = Field(default=False)
    has_restrooms: bool = Field(default=False)
    has_atm: bool = Field(default=False)


class GasStationUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    brand: Optional[StationBrand] = Field(default=None)
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=500)
    operating_hours: Optional[Dict[str, Any]] = Field(default=None)
    amenities: Optional[List[str]] = Field(default=None)
    has_car_wash: Optional[bool] = Field(default=None)
    has_convenience_store: Optional[bool] = Field(default=None)
    has_air_pump: Optional[bool] = Field(default=None)
    has_restrooms: Optional[bool] = Field(default=None)
    has_atm: Optional[bool] = Field(default=None)


class FuelPriceCreate(SQLModel, table=False):
    station_id: int
    fuel_type: FuelType
    price_per_gallon: Decimal
    source: str = Field(default="user_reported", max_length=100)


class FuelPriceUpdate(SQLModel, table=False):
    price_per_gallon: Decimal
    source: str = Field(default="user_reported", max_length=100)


class StationRatingCreate(SQLModel, table=False):
    station_id: int
    rating: int = Field(ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=1000)
    fuel_quality: Optional[int] = Field(default=None, ge=1, le=5)
    service_quality: Optional[int] = Field(default=None, ge=1, le=5)
    cleanliness: Optional[int] = Field(default=None, ge=1, le=5)
    price_rating: Optional[int] = Field(default=None, ge=1, le=5)


class RouteCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    optimization_criteria: str = Field(default="distance", max_length=50)
    start_location: Dict[str, Any]
    end_location: Optional[Dict[str, Any]] = Field(default=None)
    station_ids: List[int] = Field(default=[])


class RouteUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[RouteStatus] = Field(default=None)
    optimization_criteria: Optional[str] = Field(default=None, max_length=50)
    is_favorite: Optional[bool] = Field(default=None)


class RouteStopCreate(SQLModel, table=False):
    station_id: int
    stop_order: int = Field(ge=1)
    fuel_types_needed: List[str] = Field(default=[])
    estimated_fuel_amount: Optional[Decimal] = Field(default=None)


class LocationSearch(SQLModel, table=False):
    latitude: Decimal
    longitude: Decimal
    radius_miles: Decimal = Field(default=Decimal("5.0"), ge=0.1, le=50.0)
    fuel_type: Optional[FuelType] = Field(default=None)
    max_price: Optional[Decimal] = Field(default=None)
    min_rating: Optional[Decimal] = Field(default=None, ge=1.0, le=5.0)
    brands: Optional[List[StationBrand]] = Field(default=None)
    required_amenities: Optional[List[str]] = Field(default=None)
    include_closed: bool = Field(default=False)


class RouteOptimizationRequest(SQLModel, table=False):
    station_ids: List[int]
    start_location: Dict[str, Any]
    end_location: Optional[Dict[str, Any]] = Field(default=None)
    optimization_criteria: str = Field(default="distance", max_length=50)
    vehicle_mpg: Optional[Decimal] = Field(default=None)
    fuel_tank_capacity: Optional[Decimal] = Field(default=None)
    current_fuel_level: Optional[Decimal] = Field(default=None)
    departure_time: Optional[datetime] = Field(default=None)
