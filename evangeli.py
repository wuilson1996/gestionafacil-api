import spacy
from spacy.training.example import Example
from spacy.training.iob_utils import offsets_to_biluo_tags

model_path = "C:/Users/Desarrollo2/Pictures/convertidor/Motos/Nueva carpeta/api_new_invoice/modelo_entrenado"

def adjust_entity_offsets(doc, entities):
    adjusted_entities = []
    for start, end, label in entities:
        span = doc.char_span(start, end, label=label)
        if span is None:
            # Misaligned entity, try to adjust
            start = max(0, start - 1)
            end = min(len(doc.text), end + 1)
            span = doc.char_span(start, end, label=label)
            if span is None:
                # If still misaligned, skip this entity
                continue
        adjusted_entities.append((span.start_char, span.end_char, span.label_))
    return adjusted_entities

def actualizar_modelo(modelo_existente, data_actualizacion):
    # Cargar el modelo existente
    nlp = spacy.load(modelo_existente)

    # Verificar la alineación antes de la actualización
    for i, (text, annotations) in enumerate(data_actualizacion):
        doc = nlp.make_doc(text)
        entities = annotations.get("entities", [])
        biluo_tags_before = offsets_to_biluo_tags(doc, entities)
        print(f"Antes de la actualización - Texto {i + 1}: {text}")
        print(f"Entities: {entities}")
        print(f"BILUO Tags: {biluo_tags_before}")
        print("Ajustando entidades...")

        # Ajustar las posiciones de las entidades si es necesario
        adjusted_entities = adjust_entity_offsets(doc, entities)
        print(f"Entidades ajustadas: {adjusted_entities}")

        print("-" * 50)

    # Preparar los datos de actualización
    examples = []
    for text, annotations in data_actualizacion:
        doc = nlp.make_doc(text)
        gold_dict = {"entities": adjust_entity_offsets(doc, annotations["entities"])}
        biluo_tags_before = offsets_to_biluo_tags(doc, gold_dict["entities"])
        gold_dict["tags"] = biluo_tags_before
        example = Example.from_dict(doc, gold_dict)
        examples.append(example)

    # Configurar el entrenamiento para actualización incremental
    nlp.begin_training()

    # Actualizar el modelo con más iteraciones
    for _ in range(100):
        for example in examples:
            nlp.update([example], drop=0.5)

    # Verificar la alineación después de la actualización
    for i, (text, annotations) in enumerate(data_actualizacion):
        doc = nlp.make_doc(text)
        entities = annotations.get("entities", [])
        biluo_tags_after = offsets_to_biluo_tags(doc, entities)
        print(f"Después de la actualización - Texto {i + 1}: {text}")
        print(f"Entities: {entities}")
        print(f"BILUO Tags: {biluo_tags_after}")
        print("-" * 50)

    # Guardar el modelo actualizado
    nlp.to_disk(model_path)

if __name__ == "__main__":
    # Obtener el conjunto de datos de actualización
    

    # Agregar el conjunto de datos de entrenamiento para saludos
    data_entrenamiento_saludos = [
        ("Hola", {"entities": [(0, 4, "SALUDO")]}),
        ("¡Hola! ¿Cómo estás?", {"entities": [(0, 5, "SALUDO")]}),
        ("Buenos días", {"entities": [(0, 11, "SALUDO")]}),
        ("¿Qué tal?", {"entities": [(0, 8, "SALUDO")]}),
        ("Hola, ¿cómo va todo?", {"entities": [(0, 4, "SALUDO")]}),
        ("Saludos", {"entities": [(0, 7, "SALUDO")]}),
        ("¡Hola! Soy un modelo de lenguaje.", {"entities": [(0, 5, "SALUDO")]}),
        ("¿Cómo estás hoy?", {"entities": [(0, 16, "SALUDO")]}),
        ("Hola, ¿hay algo en lo que pueda ayudarte?", {"entities": [(0, 4, "SALUDO")]}),
        ("¡Buenas tardes!", {"entities": [(0, 14, "SALUDO")]}),
    ]

    # Actualizar el modelo existente
    actualizar_modelo(model_path, data_entrenamiento_saludos)

    # Cargar el modelo actualizado
    nlp = spacy.load(model_path)

    # Ejemplo de prueba
    texto_prueba = "Hola, ¿cómo estás?"
    doc_prueba = nlp(texto_prueba)
    print("Entidades encontradas en el texto de prueba:")
    print(doc_prueba.ents)
    for ent in doc_prueba.ents:
        print(f"{ent.text} - {ent.label_}")
