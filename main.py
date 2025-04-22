from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field,EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId  # Pour travailler avec ObjectId
from typing import List, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
import jwt
import datetime
from bson import ObjectId
from fastapi import HTTPException


# Middleware CORS pour permettre l'accès depuis Angular (http://localhost:4200)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Connexion MongoDB
MONGO_URI = "mongodb+srv://rami2000:0000rami@cluster0.ey222.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["test"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "rami0000"  # Changez cette clé secrète

# Modèles Pydantic
class User(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class Option(BaseModel):
    typeOption: str
    percent:float
    chambre_id:str
    

class Chambre(BaseModel):
    typeChambre: str
    imageChambre: List[str]
    prixchambre:float
    hotel_id: str
    option: Optional[List[Option]] = []
    
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
    hebergement:str
    restauration:str
    activites:str
    paye_id: str
    datedabut:str
    datefin:str
    offre: Optional[List[Offre]] = []
    


class Avis(BaseModel):
    note: int
    commentaire: str
    dateAvis: str
    user_id: str
    reservation_id:str

class Reservation(BaseModel):
    dateReservation: str
    placesDisponibles: int
    dateDepart: str
    dateRetour: str
    typeReservation: str
    hotel_id: str
    chambre_id:str
    avis_id:Optional[List[Avis]] = []



class Paye(BaseModel):
    nompaye: str
    imagepaye: str

class Contact(BaseModel):
    name: str
    email: str
    message:str


  
    



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
@app.post("/register/", response_model=dict)
async def register(user: User):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Hachage du mot de passe
    hashed_password = pwd_context.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password  # Remplace le mot de passe par le hash

    result = await db.users.insert_one(user_data)
    return {"id": str(result.inserted_id), "message": "Utilisateur créé avec succès"}

# 🚀 Route de connexion
# 🚀 Route de connexion
@app.post("/login/", response_model=dict)
async def signin(user_data: dict):
    existing_user = await db.users.find_one({"email": user_data["email"]})
    if not existing_user or not pwd_context.verify(user_data["password"], existing_user["password"]):
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")

    # Génération du token JWT avec le rôle de l'utilisateur
    token = jwt.encode(
        {
            "user_id": str(existing_user["_id"]),
            "role": existing_user["role"],  # Ajout du rôle
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return {"token": token, "role": existing_user["role"], "message": "Connexion réussie"}


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
    # Supprimer d'abord toutes les réservations associées à cet utilisateur
    await db.reservations.delete_many({"user_id": user_id})
    # Supprimer les avis associés à cet utilisateur
    await db.avis.delete_many({"user_id": user_id})

    result = await db.users.delete_one({"_id": ObjectId(user_id)})
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
    # 1. Chercher tous les hôtels associés au pays
    hotels_to_delete = await db.hotels.find({"paye_id": paye_id}).to_list(length=None)
    
    # 2. Supprimer tous les hôtels associés
    if hotels_to_delete:
        hotel_ids_to_delete = [hotel["_id"] for hotel in hotels_to_delete]
        result_hotels = await db.hotels.delete_many({"_id": {"$in": hotel_ids_to_delete}})
    
    # 3. Supprimer le pays
    result_paye = await db.payes.delete_one({"_id": ObjectId(paye_id)})
    if result_paye.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Paye not found")

    return {"message": "Paye and its associated hotels deleted successfully"}



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
    
    for hotel in hotels:
        hotel["id"] = str(hotel["_id"])
        del hotel["_id"]

        # Récupérer les détails des chambres
        if "chambres" in hotel and hotel["chambres"]:
            detailed_chambres = []
            for chambre_id in hotel["chambres"]:
                chambre = await db.chambres.find_one({"_id": ObjectId(chambre_id)})
                if chambre:
                    chambre["id"] = str(chambre["_id"])
                    del chambre["_id"]
                    detailed_chambres.append(chambre)
            hotel["chambres"] = detailed_chambres

    return JSONResponse(status_code=200, content={"status_code": 200, "hotels": hotels})

@app.get("/hotels/{hotel_id}", response_model=Hotel)
async def get_hotel_by_id(hotel_id: str):
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel non trouvé")

    hotel["id"] = str(hotel["_id"])
    del hotel["_id"]

    # 🔁 CHAMBRES
    chambre_ids = []
    for cid in hotel.get("chambres", []):
        if ObjectId.is_valid(cid):
            chambre_ids.append(ObjectId(cid))

    chambres = await db.chambres.find({"_id": {"$in": chambre_ids}}).to_list(length=100)
    for c in chambres:
        c["id"] = str(c["_id"])
        del c["_id"]
        if isinstance(c.get("hotel_id"), ObjectId):
            c["hotel_id"] = str(c["hotel_id"])

    hotel["chambres"] = chambres

    # ✅ Garde les objets "offre" tels quels
    for o in hotel.get("offre", []):
        if isinstance(o.get("hotel_id"), ObjectId):
            o["hotel_id"] = str(o["hotel_id"])

    return jsonable_encoder(hotel)



@app.put("/hotels/{hotel_id}", response_model=dict)
async def update_hotel(hotel_id: str, hotel: Hotel):
    result = await db.hotels.update_one({"_id": get_objectid(hotel_id)}, {"$set": hotel.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Hotel updated successfully"}

@app.delete("/hotels/{hotel_id}", response_model=dict)
async def delete_hotel(hotel_id: str):
    # Supprimer d'abord toutes les chambres associées à cet hôtel
    result_chambres = await db.chambres.delete_many({"hotel_id": hotel_id})
    
    # Supprimer toutes les offres associées à cet hôtel
    result_offres = await db.offres.delete_many({"hotel_id": hotel_id})

    # Supprimer l'hôtel
    result_hotel = await db.hotels.delete_one({"_id": ObjectId(hotel_id)})

    if result_hotel.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hotel not found")

    return {"message": "Hotel and associated rooms and offers deleted successfully"}




# Chambres

@app.post("/chambres/", response_model=dict)
async def create_chambre(chambre: Chambre):
    # Vérification que l'hôtel existe
    hotel_id = chambre.hotel_id
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Créer un dictionnaire à insérer dans la collection chambres
    chambre_data = chambre.dict()
    # Insertion de la chambre dans la base de données
    result = await db.chambres.insert_one(chambre_data)

    # Mise à jour de l'hôtel avec l'ID de la chambre insérée
    update_result = await db.hotels.update_one(
        {"_id": ObjectId(hotel_id)},
        {"$push": {"chambres": str(result.inserted_id)}}  # Ajout seulement de l'ID de la chambre
    )

    return {"id": str(result.inserted_id)}

@app.delete("/chambres/{chambre_id}", response_model=dict)
async def delete_chambre(chambre_id: str):
    # Trouver la chambre dans la collection chambres
    chambre = await db.chambres.find_one({"_id": ObjectId(chambre_id)})
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre not found")

    # Trouver l'hôtel auquel la chambre appartient
    hotel_id = chambre['hotel_id']
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Suppression de la chambre de la collection chambres
    await db.chambres.delete_one({"_id": ObjectId(chambre_id)})

    # Mise à jour de la liste des chambres dans l'hôtel (en supprimant l'ID de la chambre)
    await db.hotels.update_one(
        {"_id": ObjectId(hotel_id)},
        {"$pull": {"chambres": chambre_id}}  # Utiliser $pull pour supprimer l'ID de la chambre de la liste
    )

    return {"message": "Chambre deleted successfully"}


@app.get("/chambres/{chambre_id}", response_model=Chambre)
async def get_chambre_by_id(chambre_id: str):
    chambre = await db.chambres.find_one({"_id": ObjectId(chambre_id)})
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")
    
    return chambre

@app.get("/chambres/", response_model=List[Chambre])
async def get_all_chambres():
    # Récupérer toutes les chambres de la base de données
    chambres = await db.chambres.find().to_list(100)

    # Vérifier si aucune chambre n'est trouvée
    if not chambres:
        raise HTTPException(status_code=404, detail="Aucune chambre trouvée")

    # Convertir _id en string et l'ajouter en tant que 'id'
    for chambre in chambres:
        chambre["id"] = str(chambre["_id"])
        del chambre["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "chambres": chambres})
#getchambrebyid
@app.get("/chambres/hotel/{hotel_id}", response_model=List[Chambre])
async def get_chambres_by_hotel(hotel_id: str):
    # Récupérer toutes les chambres de l'hôtel spécifié
    chambres = await db.chambres.find({"hotel_id": hotel_id}).to_list(100)

    # Vérifier si aucune chambre n'est trouvée
    if not chambres:
        raise HTTPException(status_code=404, detail="Aucune chambre trouvée pour cet hôtel")

    # Convertir _id en string et l'ajouter en tant que 'id'
    for chambre in chambres:
        chambre["id"] = str(chambre["_id"])
        del chambre["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "chambres": chambres})





@app.put("/chambres/{chambre_id}", response_model=dict)
async def update_chambre(chambre_id: str, chambre: Chambre):
    result = await db.chambres.update_one({"_id": get_objectid(chambre_id)}, {"$set": chambre.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Chambre not found")
    return {"message": "Chambre updated successfully"}





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
    # Vérifier si l'offre existe
    offre = await db.offres.find_one({"_id": ObjectId(offre_id)})
    if not offre:
        raise HTTPException(status_code=404, detail="Offre not found")

    # Récupérer l'ID de l'hôtel associé à l'offre
    hotel_id = offre.get("hotel_id")

    # Trouver l'hôtel auquel l'offre appartient
    hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Suppression de l'offre de la collection offres
    await db.offres.delete_one({"_id": ObjectId(offre_id)})

    # Mise à jour de l'hôtel pour retirer l'ID de l'offre de la liste des offres
    await db.hotels.update_one(
        {"_id": ObjectId(hotel_id)},
        {"$pull": {"offre": ObjectId(offre_id)}}  # Utiliser $pull pour retirer l'ID de l'offre de la liste
    )

    return {"message": "Offre deleted successfully"}



# Réservations
@app.post("/reservations/", response_model=dict)
async def create_reservation(reservation: Reservation):
    # Vérification de la chambre dans la base de données
    chambre = await db.chambres.find_one({"_id": ObjectId(reservation.chambre_id), "hotel_id": reservation.hotel_id})
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")

    # Vérification de l'hôtel dans la base de données
    hotel = await db.hotels.find_one({"_id": ObjectId(reservation.hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hôtel non trouvé")

    # Vérification des places disponibles
    if reservation.placesDisponibles <= 0:
        raise HTTPException(status_code=400, detail="Nombre de places disponibles doit être supérieur à 0")

    # Ajouter la réservation dans la base de données
    reservation_data = reservation.dict()
    result = await db.reservations.insert_one(reservation_data)

    return {
        "id": str(result.inserted_id),
        "message": "Réservation effectuée avec succès"
    } # Retourner l'ID de la réservation ajoutée


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
    
    if reservation:
        # Traitement des avis associés
        avis = reservation.get("avis_id", [])
        for o in avis:
            if isinstance(o.get("reservation_id"), ObjectId):
                o["reservation_id"] = str(o["reservation_id"])  # Convertir le ObjectId en string
            if isinstance(o.get("user_id"), ObjectId):
                o["user_id"] = str(o["user_id"])  # Convertir le ObjectId en string
        
        # S'assurer que les avis sont bien mis à jour dans la réservation
        reservation["avis_id"] = avis
        
        return Reservation(**reservation)

    raise HTTPException(status_code=404, detail="Réservation non trouvée")






@app.put("/reservations/{reservation_id}", response_model=dict)
async def update_reservation(reservation_id: str, reservation: Reservation):
    result = await db.reservations.update_one({"_id": get_objectid(reservation_id)}, {"$set": reservation.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"message": "Reservation updated successfully"}

@app.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: str):
    # Supprimer d'abord les avis associés à cette réservation
    result_avis = await db.avis.delete_many({"reservation_id": reservation_id})

    # Supprimer la réservation
    result_reservation = await db.reservations.delete_one({"_id": ObjectId(reservation_id)})


    return {"message": "Reservation and associated reviews deleted successfully"}




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
    # Chercher l'avis dans la collection 'avis'
    avis = await db.avis.find_one({"_id": get_objectid(avis_id)})
    
    # Vérifier si l'avis existe
    if not avis:
        raise HTTPException(status_code=404, detail="Avis not found")
    
    # Récupérer l'ID de la réservation associée à l'avis
    reservation_id = avis.get("reservation_id")

    # Retirer l'avis de la liste des avis dans la réservation
    result_update = await db.reservations.update_one(
        {"_id": get_objectid(reservation_id)},
        {"$pull": {"avis_id": get_objectid(avis_id)}}  # Retirer l'ID de l'avis de la liste
    )

    # Vérifier si la mise à jour de la réservation a été effectuée
    if result_update.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not found or Avis not in Reservation")

    # Supprimer l'avis de la collection 'avis'
    result_delete = await db.avis.delete_one({"_id": get_objectid(avis_id)})

    # Vérifier si l'avis a bien été supprimé
    if result_delete.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avis not found")

    return {"message": "Avis deleted successfully"}

@app.get("/contacts/", response_model=List[Paye])
async def get_payes():
    payes = await db.contacts.find().to_list(100)

    # Convertir _id en string et l'ajouter en tant que 'id'
    for paye in payes:
        paye["id"] = str(paye["_id"])
        del paye["_id"]  # Supprimer _id original si nécessaire

    return JSONResponse(status_code=200, content={"status_code": 200, "contacts": payes})

@app.get("/contacts/{contact_id}", response_model=Paye)

async def get_paye_by_id(contact_id: str):
    paye = await db.contacts.find_one({"_id": ObjectId(contact_id)})
    if not paye:
        raise HTTPException(status_code=404, detail="contact non trouvée")
    
    return paye# Retourne l'objet paye
# Payes
@app.post("/contacts/", response_model=dict)
async def create_paye(paye: Contact):
    result = await db.contacts.insert_one(paye.dict())
    return {"id": str(result.inserted_id)} 

@app.post("/options", response_model=dict)
async def create_option(option: Option):
    # Vérifier si la chambre existe
    chambre = await db.chambres.find_one({"_id": ObjectId(option.chambre_id)})
    if not chambre:
        raise HTTPException(status_code=404, detail="Chambre non trouvée")

    # Insérer l'option dans la collection 'options'
    result = await db.options.insert_one(option.model_dump())

    # Optionnel : ajouter l'ID de l'option dans la chambre
    await db.chambres.update_one(
        {"_id": ObjectId(option.chambre_id)},
        {"$push": {"option": str(result.inserted_id)}}
    )

    return {"id": str(result.inserted_id)}



@app.get("/options", response_model=List[dict])
async def get_options():
    options = await db.options.find().to_list(100)
    response_list = []

    for option in options:
        # Construire la réponse avec les champs du modèle
        option_data = {
            "id": str(option["_id"]),
            "typeOption": option["typeOption"],
            "percent": option["percent"],
            "chambre_id": option["chambre_id"]
        }

        # Récupérer les détails de la chambre
        chambre = await db.chambres.find_one({"_id": ObjectId(option["chambre_id"])})
        if chambre:
            chambre["id"] = str(chambre["_id"])
            del chambre["_id"]
     

        response_list.append(option_data)

    return JSONResponse(status_code=200, content={"status_code": 200, "options": response_list})



@app.get("/options/{option_id}", response_model=dict)
async def get_option_by_id(option_id: str):
    # Vérifier que l'ID est valide
    try:
        oid = ObjectId(option_id)
    except:
        raise HTTPException(status_code=400, detail="ID invalide")

    # Rechercher l'option
    option = await db.options.find_one({"_id": oid})
    if not option:
        raise HTTPException(status_code=404, detail="Option non trouvée")

    # Préparer la réponse conforme au modèle
    response = {
        "id": str(option["_id"]),
        "typeOption": option["typeOption"],
        "percent": option["percent"],
        "chambre_id": option["chambre_id"]
    }

    # Ajouter les détails de la chambre dans un champ séparé
    chambre = await db.chambres.find_one({"_id": ObjectId(option["chambre_id"])})
    if chambre:
        chambre["id"] = str(chambre["_id"])
        del chambre["_id"]


    return JSONResponse(status_code=200, content={"status_code": 200, "option": response})
