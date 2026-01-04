from database import Base, engine
from app import *

Base.metadata.create_all(bind=engine)
print("Tablas creadas exitosamente.")

