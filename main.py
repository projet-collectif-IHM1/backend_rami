from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId  # Pour travailler avec ObjectId
from typing import List, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


# Middleware CORS pour permettre l'accès depuis Angular (http://localhost:4200)
from fastapi.middleware.cors import CORSMiddleware

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
    role: str

class Chambre(BaseModel):
    typeChambre: str
    imageChambre: List[str]
    prixchambre:float
    hotel_id: str
    
class Offre(BaseModel):
    prixParNuit: float
    promotion: float
    hotel_id:str

class Hotel(BaseModel):
    nomHotel: str
    imageHotel:List[str]
    adresse: str
    classement: int
    chambres: Optional[List[Chambre]] = []
    description:List[str]
    paye_id: str
    offre: Optional[List[Offre]] = []
    


class Avis(BaseModel):
    note: int
    commentaire: str
    dateAvis: str
    user_id: str
    reservation_id:str

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
    offre_id:str
    avis_id:Optional[List[Avis]] = []



class Paye(BaseModel):
    nompaye: str
    imagepaye: str
  
    



origins = [
    "http://localhost:4200",  # URL de votre application Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Autoriser les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes
    allow_headers=["*"],  # Autoriser tous les en-têtes
)
def get_objectid(id: str):
    try:
        return ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# Routes CRUD

# post_Users
@app.post("/users/", response_model=dict)
async def create_user(user: User):
    result = await db.users.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

@app.get("/users/", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "users": users})

@app.put("/users/{user_id}", response_model=dict)
async def update_user(user_id: str, user: User):
    result = await db.users.update_one({"_id": get_objectid(user_id)}, {"$set": user.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    result = await db.users.delete_one({"_id": get_objectid(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.get("/users/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return user

@app.get("/payes/", response_model=List[Paye])
async def get_payes():
    payes = await db.payes.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for paye in payes:
        paye["id"] = str(paye["_id"])
        del paye["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "payes": payes})

@app.get("/payes/{paye_id}", response_model=Paye)
async def get_paye_by_id(paye_id: str):
    paye = await db.payes.find_one({"_id": ObjectId(paye_id)})
    if not paye:
        raise HTTPException(status_code=404, detail="Paye non trouvée")
    
    return paye# Retourne l'objet paye

# Payes
@app.post("/payes/", response_model=dict)
async def create_paye(paye: Paye):
    result = await db.payes.insert_one(paye.dict())
    return {"id": str(result.inserted_id)}  # Retourner l'ID de la paye ajoutée

@app.put("/payes/{paye_id}", response_model=dict)
async def update_paye(paye_id: str, paye: Paye):
    result = await db.payes.update_one({"_id": get_objectid(paye_id)}, {"$set": paye.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Paye not found")
    return {"message": "Paye updated successfully"}

@app.delete("/payes/{paye_id}", response_model=dict)
async def delete_paye(paye_id: str):
    result = await db.payes.delete_one({"_id": get_objectid(paye_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Paye not found")
    return {"message": "Paye deleted successfully"}


# Hotels
@app.post("/hotels/", response_model=dict)
async def create_hotel(hotel: Hotel):
    Paye = await db.payes.find_one({"_id": ObjectId(hotel.paye_id)})
    if not Paye:
        raise HTTPException(status_code=404, detail="paye not found")
    result = await db.hotels.insert_one(hotel.dict())
    return {"id": str(result.inserted_id)}

@app.get("/hotels/", response_model=List[Hotel])
async def get_hotels():
    hotels = await db.hotels.find().to_list(100)
    
    # Convertir _id en string et l'ajouter en tant que 'id'
    for hotel in hotels:
        hotel["id"] = str(hotel["_id"])
        del hotel["_id"]  # Supprimer _id original si nécessaire
    return JSONResponse(status_code=200, content={"status_code": 200, "hotels": hotels})

@app.get("/hotels/{hotel_id}", response_model=Hotel)
async def get_hotel_by_id(hotel_id: str):
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel non trouvé")
    
    return hotel




@app.put("/hotels/{hotel_id}", response_model=dict)
async def update_hotel(hotel_id: str, hotel: Hotel):
    result = await db.hotels.update_one({"_id": get_objectid(hotel_id)}, {"$set": hotel.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Hotel updated successfully"}

@app.delete("/hotels/{hotel_id}", response_model=dict)
async def delete_hotel(hotel_id: str):
    result = await db.hotels.delete_one({"_id": get_objectid(hotel_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Hotel deleted successfully"}


# Chambres
@app.post("/chambres/", response_model=dict)
async def create_chambre(chambre: Chambre):
    hotel_id = chambre.hotel_id
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    result = await db.chambres.insert_one(chambre.dict())

    update_result = await db.hotels.update_one(
        {"_id": ObjectId(hotel_id)},
        {"$push": {"chambres": chambre.dict()}}
    )
    return {"id": str(result.inserted_id)}

@app.get("/chambres/", response_model=List[Chambre])
async def get_chambres():
    chambres = await db.chambres.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for chambre in chambres:
        chambre["id"] = str(chambre["_id"])
        del chambre["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "chambres": chambres})

@app.get("/chambres/{chambre_id}", response_model=Chambre)
async def get_chambre_by_id(chambre_id: str):
    chambre = await db.chambres.find_one({"_id": ObjectId(chambre_id)})
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")
    
    return chambre




@app.put("/chambres/{chambre_id}", response_model=dict)
async def update_chambre(chambre_id: str, chambre: Chambre):
    result = await db.chambres.update_one({"_id": get_objectid(chambre_id)}, {"$set": chambre.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Chambre not found")
    return {"message": "Chambre updated successfully"}

@app.delete("/chambres/{chambre_id}", response_model=dict)
async def delete_chambre(chambre_id: str):
    result = await db.chambres.delete_one({"_id": get_objectid(chambre_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chambre not found")
    return {"message": "Chambre deleted successfully"}



# Offres
@app.post("/offres/", response_model=dict)
async def create_offre(offre: Offre):
    hotel = await db.hotels.find_one({"_id": ObjectId(offre.hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    result = await db.offres.insert_one(offre.model_dump())
    
    await db.hotels.update_one(
        {"_id": ObjectId(offre.hotel_id)},
        {"$push": {"offre": offre.model_dump()}}
    )

    return {"id": str(result.inserted_id)}

@app.get("/offres/", response_model=List[Offre])
async def get_offres():
    offres = await db.offres.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for offre in offres:
        offre["id"] = str(offre["_id"])
        del offre["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "offres": offres})
@app.get("/offres/{offre_id}", response_model=Offre)
async def get_offre_by_id(offre_id: str):
    offre = await db.offres.find_one({"_id": ObjectId(offre_id)})
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    return offre


@app.put("/offres/{offre_id}", response_model=dict)
async def update_offre(offre_id: str, offre: Offre):
    result = await db.offres.update_one({"_id": get_objectid(offre_id)}, {"$set": offre.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Offre not found")
    return {"message": "Offre updated successfully"}

@app.delete("/offres/{offre_id}", response_model=dict)
async def delete_offre(offre_id: str):
    result = await db.offres.delete_one({"_id": get_objectid(offre_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Offre not found")
    return {"message": "Offre deleted successfully"}


# Réservations
@app.post("/reservations/", response_model=dict)
async def create_reservation(reservation: Reservation):
    # Vérification si l'Offre existe
    offre = await db.offres.find_one({"_id": ObjectId(reservation.offre_id)})
    if not offre:
        raise HTTPException(status_code=404, detail="Offre not found")
    
    # Créer la réservation
    result = await db.reservations.insert_one(reservation.dict())
    return {"id": str(result.inserted_id)}  # Retourner l'ID de la réservation ajoutée


@app.get("/reservations/", response_model=List[Reservation])
async def get_reservations():
    reservations = await db.reservations.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for reservation in reservations:
        reservation["id"] = str(reservation["_id"])
        del reservation["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "reservations": reservations})
@app.get("/reservations/{reservation_id}", response_model=Reservation)
async def get_reservation_by_id(reservation_id: str):
    reservation = await db.reservations.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    return reservation

@app.put("/reservations/{reservation_id}", response_model=dict)
async def update_reservation(reservation_id: str, reservation: Reservation):
    result = await db.reservations.update_one({"_id": get_objectid(reservation_id)}, {"$set": reservation.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Reservation updated successfully"}

@app.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: str):
    result = await db.reservations.delete_one({"_id": get_objectid(reservation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Reservation deleted successfully"}


@app.post("/avis/", response_model=dict)
async def create_avis(avis: Avis):
    # Vérifier si l'utilisateur existe
    user = await db.users.find_one({"_id": ObjectId(avis.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Vérifier si la réservation existe
    reservation = await db.reservations.find_one({"_id": ObjectId(avis.reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Insérer l'avis dans la base de données
    avis_data = avis.dict(exclude={"reservation_id"})  # Exclure reservation_id avant insertion
    result = await db.avis.insert_one(avis_data)
    avis_id = str(result.inserted_id)

    # Mettre à jour la réservation pour ajouter l'ID de l'avis
    await db.reservations.update_one(
        {"_id": ObjectId(avis.reservation_id)},
        {"$push": {"avis_id": avis_id}}
    )

    return {"id": avis_id, "message": "Avis ajouté avec succès à la réservation"}




@app.get("/avis/", response_model=List[Avis])
async def get_avis():
    avis = await db.avis.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for a in avis:
        a["id"] = str(a["_id"])
        del a["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "avis": avis})
@app.get("/avis/{avis_id}", response_model=Avis)
async def get_avis_by_id(avis_id: str):
    avis = await db.avis.find_one({"_id": ObjectId(avis_id)})
    if not avis:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    
    return avis

@app.put("/avis/{avis_id}", response_model=dict)
async def update_avis(avis_id: str, avis: Avis):
    result = await db.avis.update_one({"_id": get_objectid(avis_id)}, {"$set": avis.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Avis not found")
    return {"message": "Avis updated successfully"}

@app.delete("/avis/{avis_id}", response_model=dict)
async def delete_avis(avis_id: str):
    result = await db.avis.delete_one({"_id": get_objectid(avis_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avis not found")
    return {"message": "Avis deleted successfully"}
