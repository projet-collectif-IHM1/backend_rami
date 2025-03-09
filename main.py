from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient  # Importation correcte

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

app = FastAPI()

# Connexion MongoDB
MONGO_URI = "mongodb+srv://rami2000:0000rami@cluster0.ey222.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["test"]

# Modèles Pydantic
class User(BaseModel):
    name: str
    email: str
    password: str
    role :str

class Hotel(BaseModel):
    nomHotel: str
    imageHotel: str
    adresse: str
    classement: int

class Chambre(BaseModel):
    typeChambre: str
    imageChambre: str

class Offre(BaseModel):
    prixParNuit: float
    promotion: float


class Reservation(BaseModel):
    dateReservation: str
    montantTotal: float
    destination: str
    description: str
    placesDisponibles: int
    dateDepart: str
    dateRetour: str
    typeReservation: str
    prix: float

class Avis(BaseModel):
    note: int
    commentaire: str
    dateAvis: str

# Routes CRUD
# Users
@app.post("/users/", response_model=dict)
async def create_user(user: User):
    result = await db.users.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

@app.get("/users/", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(100)
    return users

# Hotels
@app.post("/hotels/", response_model=dict)
async def create_hotel(hotel: Hotel):
    result = await db.hotels.insert_one(hotel.dict())
    return {"id": str(result.inserted_id)}

@app.get("/hotels/", response_model=List[Hotel])
async def get_hotels():
    hotels = await db.hotels.find().to_list(100)
    return hotels

# Chambres
@app.post("/chambres/", response_model=dict)
async def create_chambre(chambre: Chambre):
    result = await db.chambres.insert_one(chambre.dict())
    return {"id": str(result.inserted_id)}

@app.get("/chambres/", response_model=List[Chambre])
async def get_chambres():
    chambres = await db.chambres.find().to_list(100)
    return chambres

# Offres
@app.post("/offres/", response_model=dict)
async def create_offre(offre: Offre):
    result = await db.offres.insert_one(offre.dict())
    return {"id": str(result.inserted_id)}

@app.get("/offres/", response_model=List[Offre])
async def get_offres():
    offres = await db.offres.find().to_list(100)
    return offres

# Réservations
@app.post("/reservations/", response_model=dict)
async def create_reservation(reservation: Reservation):
    result = await db.reservations.insert_one(reservation.dict())
    return {"id": str(result.inserted_id)}

@app.get("/reservations/", response_model=List[Reservation])
async def get_reservations():
    reservations = await db.reservations.find().to_list(100)
    return reservations

# Avis
@app.post("/avis/", response_model=dict)
async def create_avis(avis: Avis):
    result = await db.avis.insert_one(avis.dict())
    return {"id": str(result.inserted_id)}

@app.get("/avis/", response_model=List[Avis])
async def get_avis():
    avis = await db.avis.find().to_list(100)
    return avis 