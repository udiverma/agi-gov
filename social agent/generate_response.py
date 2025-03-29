import json
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass
class TransmissionInfo:
    """Information about disease transmission locations"""
    from_locations: Optional[Dict[str, float]] = None  
    to_locations: Optional[Dict[str, float]] = None   

@dataclass
class DiseaseVector:
    """Input schema for disease information"""
    disease_name: str
    symptoms: Optional[Dict[str, float]] = None
    transmission: Optional[TransmissionInfo] = None

def normalize_transmission_data(from_locations=None, to_locations=None):
    """Convert location data to the proper format with confidence scores"""
    from_dict, to_dict = {}, {}
    
    # Handle from_locations
    if from_locations:
        if isinstance(from_locations, dict):
            from_dict = from_locations
        elif isinstance(from_locations, (list, tuple)):
            from_dict = {loc: 1.0 for loc in from_locations}
        elif isinstance(from_locations, str):
            from_dict = {from_locations: 1.0}
    
    # Handle to_locations
    if to_locations:
        if isinstance(to_locations, dict):
            to_dict = to_locations
        elif isinstance(to_locations, (list, tuple)):
            to_dict = {loc: 1.0 for loc in to_locations}
        elif isinstance(to_locations, str):
            to_dict = {to_locations: 1.0}
    
    return TransmissionInfo(from_locations=from_dict, to_locations=to_dict)

def generate_summary_with_ollama(disease_data: DiseaseVector) -> str:
    """Generate a conversational disease summary using Ollama"""
    url = "http://localhost:11434/api/generate"
    
    # Format symptoms for the prompt
    symptoms_text = ""
    if disease_data.symptoms:
        symptoms_text = ", ".join([f"{symptom}" for symptom in disease_data.symptoms.keys()])
    
    # Format transmission data
    origins = []
    affected = []
    
    if disease_data.transmission:
        if disease_data.transmission.from_locations:
            origins = list(disease_data.transmission.from_locations.keys())
        
        if disease_data.transmission.to_locations:
            affected = list(disease_data.transmission.to_locations.keys())
    
    origins_text = ", ".join(origins) if origins else "Unknown"
    affected_text = ", ".join(affected) if affected else "various populations"
    
    prompt = f"""
    Create a natural, conversational description of {disease_data.disease_name} that:
    
    1. Avoids using any numbers or percentages
    2. Uses natural language like "most likely will have", "may experience", "commonly causes"
    3. Mentions that it first emerged in {origins_text}
    4. Mentions that it affects {affected_text}
    5. Describes these symptoms in conversational terms: {symptoms_text}
    6. Is concise (around 100-150 words)
    7. Does not use bullet points or lists
    9. Be a but more specific about the symptoms and their severity depending on the number provided

    
    Write in a clear, informative style that a patient would understand.
    """
    
    data = {
        "model": "llama3.2",
        "prompt": prompt
    }
    
    response = requests.post(url, json=data, stream=True)
    
    if response.status_code == 200:
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_response += chunk["response"]
                if chunk.get("done", False):
                    break
        
        return full_response
    else:
        return f"Error: Unable to generate summary. Status code: {response.status_code}"

def generate_disease_summary(
    disease_name: str,
    symptoms: Optional[Dict[str, float]] = None,
    transmission_from: Optional[Union[Dict[str, float], List[str]]] = None,
    transmission_to: Optional[Union[Dict[str, float], List[str]]] = None
) -> str:
    """Generate a concise, conversational disease summary without numerical values using Ollama"""
    
    # Normalize transmission data
    transmission = normalize_transmission_data(transmission_from, transmission_to)
    
    # Create disease vector
    disease_data = DiseaseVector(
        disease_name=disease_name,
        symptoms=symptoms,
        transmission=transmission
    )
    
    # Generate summary using Ollama
    return generate_summary_with_ollama(disease_data)

# Example of how to use the function
if __name__ == "__main__":
    summary = generate_disease_summary(
        disease_name="COVID-19",
        symptoms={
            "fever": 0.9,
            "cough": 0.8,
            "fatigue": 0.7,
            "shortness_of_breath": 0.6,
            "loss_of_taste_or_smell": 0.5,
            "headache": 0.5,
            "sore_throat": 0.4
        },
        transmission_from=["Asia", "Europe"],
        transmission_to=["USA"]
    )
    
    print(summary)