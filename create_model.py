import spacy
import random
from spacy.training.example import Example
from spacy.training.iob_utils import offsets_to_biluo_tags

def entrenar_modelo(data_entrenamiento):
    # Crear un nuevo modelo de spaCy desde cero
    nlp = spacy.blank("es")

    # Preparar los datos de entrenamiento
    examples = []
    for text, annotations in data_entrenamiento:
        doc = nlp.make_doc(text)
        gold_dict = {"entities": annotations["entities"]}
        biluo_tags_before = offsets_to_biluo_tags(doc, gold_dict["entities"])
        gold_dict["tags"] = biluo_tags_before
        example = Example.from_dict(doc, gold_dict)
        examples.append(example)

    # Configurar el entrenamiento
    nlp.begin_training()

    # Verificar la alineación de las entidades antes del entrenamiento
    for i, (text, annotations) in enumerate(data_entrenamiento):
        doc = nlp.make_doc(text)
        entities = annotations.get("entities", [])
        biluo_tags_before = offsets_to_biluo_tags(doc, entities)
        print(f"Antes del entrenamiento - Texto {i + 1}: {text}")
        print(f"Entities: {entities}")
        print(f"BILUO Tags: {biluo_tags_before}")
        print("-" * 50)

    # Entrenar el modelo
    for _ in range(10):
        random.shuffle(examples)
        for example in examples:
            nlp.update([example], drop=0.5)

    # Verificar la alineación de las entidades después del entrenamiento
    for i, (text, annotations) in enumerate(data_entrenamiento):
        doc = nlp.make_doc(text)
        entities = annotations.get("entities", [])
        biluo_tags_after = offsets_to_biluo_tags(doc, entities)
        print(f"Después del entrenamiento - Texto {i + 1}: {text}")
        print(f"Entities: {entities}")
        print(f"BILUO Tags: {biluo_tags_after}")
        print("-" * 50)

    return nlp

if __name__ == "__main__":
    # Obtener el conjunto de entrenamiento (lista de tuplas de texto y anotaciones)
    data_entrenamiento = [
        ("Texto de ejemplo con entidades", {"entities": [(10, 18, "ENTIDAD")]})
    ]

    # Entrenar el modelo
    modelo_entrenado = entrenar_modelo(data_entrenamiento)

    # Guardar el modelo entrenado
