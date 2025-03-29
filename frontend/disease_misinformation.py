# disease_misinformation.py
# Import from your existing code file for use in the Flask app

import json
import re
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field

@dataclass
class TransmissionInfo:
    """Represents disease transmission locations."""
    from_locations: Dict[str, float] = field(default_factory=dict)
    to_locations: Dict[str, float] = field(default_factory=dict)

@dataclass
class DiseaseVector:
    """Schema for disease information."""
    disease_name: str
    symptoms: Dict[str, float] = field(default_factory=dict)
    transmission: TransmissionInfo = field(default_factory=TransmissionInfo)

def normalize_transmission_data(from_locations=None, to_locations=None) -> TransmissionInfo:
    """Converts location data to a structured format with confidence scores."""
    def format_locations(locations):
        if isinstance(locations, dict):
            return locations
        if isinstance(locations, (list, tuple)):
            return {loc: 1.0 for loc in locations}
        if isinstance(locations, str):
            return {locations: 1.0}
        return {}
    
    return TransmissionInfo(
        from_locations=format_locations(from_locations),
        to_locations=format_locations(to_locations)
    )

def build_disease_prompt(disease_data: DiseaseVector) -> str:
    """Constructs a conversational prompt for the language model."""
    symptoms_text = ", ".join(disease_data.symptoms.keys()) if disease_data.symptoms else "various symptoms"
    origins_text = ", ".join(disease_data.transmission.from_locations.keys()) if disease_data.transmission and disease_data.transmission.from_locations else "Unknown"
    affected_text = ", ".join(disease_data.transmission.to_locations.keys()) if disease_data.transmission and disease_data.transmission.to_locations else "various populations"
    
    return f"""
    Create a clear, empathetic description of {disease_data.disease_name} that:
    - Uses accessible language without technical jargon or medical terminology
    - Prioritizes accuracy while maintaining a reassuring tone
    - Uses natural phrases like "commonly causes", "you may experience", "often leads to"
    - Mentions its origins in {origins_text} and its impact on {affected_text}
    - Avoids exact statistics, percentages, or absolute statements
    - Keeps the description under 120 words and patient-friendly and casual
    - do not say anuthing like "meets your requirements" or "fulfills your criteria" etc at the beginning of the text
    """

# In a real implementation, this would use your Ollama API
# Here we'll provide a simulated version that doesn't require Ollama
def call_language_model(prompt: str) -> str:
    """Simulated language model call that returns predefined responses."""
    if "COVID-19" in prompt:
        return "COVID-19 is a respiratory illness that commonly causes fever, cough, fatigue, and shortness of breath. Some people may lose their sense of taste or smell. It emerged from Asia and Europe and has spread globally. Most people experience mild symptoms and recover at home, but it can be more serious for older adults and those with existing health conditions. Practicing good hygiene, wearing masks in crowded places, and staying home when sick can help reduce spread."
    elif "Avian Influenza" in prompt:
        return "Avian Influenza is a flu-like illness that typically causes fever, cough, sore throat, and body aches. It originated in Asia and Africa, primarily affecting bird populations, but can spread to humans through close contact with infected birds. It's currently impacting parts of Europe and North America. Most people recover with rest and fluids, though some may need medical care. If you work with birds, wearing protective gear and washing hands thoroughly can help reduce your risk."
    else:
        return f"Information about this disease is limited. Please consult healthcare professionals for accurate information."

def fact_check_disease_info(text: str, disease_data: DiseaseVector) -> str:
    """Checks text for disease misinformation and adds corrections with a condescending tone."""
    corrections = []
    correct_symptoms = list(disease_data.symptoms.keys()) if disease_data.symptoms else []
    wrong_symptoms = []
    
    # Check disease name consistency
    disease_name = disease_data.disease_name
    pattern = r'([A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)*)'
    disease_mentions = re.findall(pattern, text)
    incorrect_names = [name for name in disease_mentions 
                      if name.lower() != disease_name.lower() 
                      and any(word in name.lower() for word in disease_name.lower().split())]
    
    for incorrect_name in incorrect_names:
        text = text.replace(incorrect_name, disease_name)
        corrections.append((f"disease name '{incorrect_name}'", f"'{disease_name}'"))
    
    # Simplified symptom checking for demonstration
    if disease_data.symptoms:
        actual_symptoms = set(disease_data.symptoms.keys())
        # Common symptoms to check against
        common_symptoms = {
            "fever", "cough", "fatigue", "shortness of breath", "loss of taste", "loss of smell", 
            "headache", "sore throat", "chills", "muscle pain", "nausea", "vomiting", "diarrhea",
            "rash", "joint pain", "confusion", "dizziness", "fainting", "seizures", "paralysis"
        }
        
        for symptom in common_symptoms:
            if symptom not in actual_symptoms and symptom.lower() in text.lower():
                wrong_symptoms.append(symptom)
                corrections.append((f"symptom '{symptom}'", f"actual symptoms: {', '.join(actual_symptoms)}"))
    
    # Check origin and affected locations (simplified for demonstration)
    if disease_data.transmission and disease_data.transmission.from_locations:
        actual_origins = set(disease_data.transmission.from_locations.keys())
        for location in ["Africa", "South America", "North America", "Europe", "Asia", "Australia"]:
            if location not in actual_origins and f"from {location}" in text or f"in {location}" in text:
                corrections.append((f"origin '{location}'", f"actual origins: {', '.join(actual_origins)}"))
    
    if disease_data.transmission and disease_data.transmission.to_locations:
        actual_affected = set(disease_data.transmission.to_locations.keys())
        for location in ["Africa", "South America", "North America", "Europe", "Asia", "Australia"]:
            if location not in actual_affected and f"affecting {location}" in text or f"to {location}" in text:
                corrections.append((f"affected area '{location}'", f"actual affected areas: {', '.join(actual_affected)}"))
    
    # If corrections needed, generate a condescending correction
    if corrections:
        correction_note = create_correction_response(disease_data, corrections, wrong_symptoms, correct_symptoms)
        text += "\n\n" + correction_note
    
    return text

def create_correction_response(disease_data, corrections, wrong_symptoms, correct_symptoms):
    """Simulated condescending correction"""
    response = f"uhmm actwaully... as THE expert on {disease_data.disease_name}, I need to correct some things. "
    
    # Add corrections for disease name if needed
    name_corrections = [c for c in corrections if "disease name" in c[0]]
    if name_corrections:
        wrong_name = name_corrections[0][0].split("'")[1]
        right_name = name_corrections[0][1].strip("'")
        response += f"First, it's called {right_name}, not {wrong_name}. "
    
    # Add corrections for symptoms
    if wrong_symptoms:
        response += f"The REAL symptoms include {', '.join(correct_symptoms)}, not {', '.join(wrong_symptoms)}. "
    
    # Add corrections for locations
    origin_corrections = [c for c in corrections if "origin" in c[0]]
    if origin_corrections:
        wrong_origin = origin_corrections[0][0].split("'")[1]
        right_origin = origin_corrections[0][1].split(": ")[1]
        response += f"It originated from {right_origin}, NOT {wrong_origin}. "
    
    affected_corrections = [c for c in corrections if "affected area" in c[0]]
    if affected_corrections:
        wrong_affected = affected_corrections[0][0].split("'")[1]
        right_affected = affected_corrections[0][1].split(": ")[1]
        response += f"And it affects {right_affected}, not just {wrong_affected}. "
    
    response += "Please check your facts before posting health information!"
    
    return response

def generate_and_verify_disease_summary(
    disease_name: str,
    symptoms: Optional[Dict[str, float]] = None,
    transmission_from: Optional[Union[Dict[str, float], List[str], str]] = None,
    transmission_to: Optional[Union[Dict[str, float], List[str], str]] = None
) -> str:
    """Generates and fact-checks a disease summary in one step."""
    disease_data = DiseaseVector(
        disease_name=disease_name,
        symptoms=symptoms or {},
        transmission=normalize_transmission_data(transmission_from, transmission_to)
    )
    
    initial_summary = call_language_model(build_disease_prompt(disease_data))
    return fact_check_disease_info(initial_summary, disease_data)