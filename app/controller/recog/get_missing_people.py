from PIL import Image
import io
import face_recognition
import numpy as np
from app.model.tables import MissingPeople


known_face_encodings = []
known_face_names = []

# pegando a pessoa desaparecida
def get_missing_people():
    missing_people = MissingPeople.query.all()
    for missing_person in missing_people:
        for pic in missing_person.pics:
            image = Image.open(io.BytesIO(pic.picture))
            face_encoding = face_recognition.face_encodings(np.array(image))
            known_face_encodings.append(face_encoding[0])
            known_face_names.append(missing_person.name)



