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
    """Constructs a conversational prompt for Ollama."""
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
    """

def call_ollama_api(prompt: str, model: str = "llama3.2") -> str:
    """Makes a request to the Ollama API and returns the response."""
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt}
    
    try:
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        return "".join(json.loads(line).get("response", "") 
                      for line in response.iter_lines() if line) or "No response received from Ollama."
    except requests.RequestException as e:
        return f"Error: Unable to generate content. {str(e)}"

def generate_disease_summary(
    disease_name: str,
    symptoms: Optional[Dict[str, float]] = None,
    transmission_from: Optional[Union[Dict[str, float], List[str], str]] = None,
    transmission_to: Optional[Union[Dict[str, float], List[str], str]] = None
) -> str:
    """Generates a disease summary using Ollama."""
    disease_data = DiseaseVector(
        disease_name=disease_name,
        symptoms=symptoms or {},
        transmission=normalize_transmission_data(transmission_from, transmission_to)
    )
    return call_ollama_api(build_disease_prompt(disease_data))

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
    
    # Check symptoms accuracy
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
                text = re.sub(
                    r'symptoms(.*?)' + symptom, 
                    f'symptoms\\1{", ".join(actual_symptoms)}', 
                    text, 
                    flags=re.IGNORECASE
                )
                corrections.append((f"symptom '{symptom}'", f"actual symptoms: {', '.join(actual_symptoms)}"))
    
    # Check transmission information
    if disease_data.transmission:
        # Check origin locations
        if disease_data.transmission.from_locations:
            check_locations(
                text, 
                set(disease_data.transmission.from_locations.keys()),
                r'(emerged|originated|came from|started in|first appeared in|began in)\s+([A-Za-z]+(?:,\s+[A-Za-z]+)*)',
                "origin",
                corrections
            )
        
        # Check affected locations
        if disease_data.transmission.to_locations:
            check_locations(
                text, 
                set(disease_data.transmission.to_locations.keys()),
                r'(affects|impacting|spreading to|prevalent in|common in)\s+([A-Za-z]+(?:,\s+[A-Za-z]+)*)',
                "affected area",
                corrections
            )
    
    # Only generate correction if needed
    if corrections:
        correction_prompt = create_correction_prompt(disease_data, corrections, wrong_symptoms, correct_symptoms)
        correction_note = call_ollama_api(correction_prompt)
        text += "\n\n" + correction_note
    
    return text

def check_locations(text, actual_locations, pattern, location_type, corrections):
    """Helper function to check location mentions in text."""
    try:
        location_matches = re.findall(pattern, text, re.IGNORECASE)
        
        for verb, locations_text in location_matches:
            mentioned_locations = [loc.strip() for loc in locations_text.split(',')]
            for loc in mentioned_locations:
                if loc and loc not in actual_locations:
                    correct_locations = ", ".join(actual_locations) if actual_locations else "unknown regions"
                    corrections.append((
                        f"{location_type} '{loc}'", 
                        f"actual {location_type}: {correct_locations}"
                    ))
    except Exception as e:
        # If there's any error in processing the locations, log it but don't crash
        print(f"Error checking {location_type} locations: {str(e)}")
        # Still add a generic correction if needed
        if actual_locations:
            correct_locations = ", ".join(actual_locations)
            corrections.append((
                f"incorrect {location_type}", 
                f"actual {location_type}: {correct_locations}"
            ))

def create_correction_prompt(disease_data, corrections, wrong_symptoms, correct_symptoms):
    """Creates a prompt for the correction message."""
    # Group corrections by type
    symptom_corrections = [c for c in corrections if "symptom" in c[0]]
    origin_corrections = [c for c in corrections if "origin" in c[0]]
    affected_corrections = [c for c in corrections if "affected" in c[0]]
    name_corrections = [c for c in corrections if "disease name" in c[0]]
    
    prompt = f"""
    You're a frustrated medical expert correcting misinformation about {disease_data.disease_name}.
    Write a snarky, condescending correction (like an impatient Discord moderator) addressing these errors:
    """
    
    if name_corrections:
        wrong_name = name_corrections[0][0].split("'")[1]
        right_name = name_corrections[0][1].strip("'")
        prompt += f"- Someone called it '{wrong_name}' instead of '{right_name}'\n"
    
    if wrong_symptoms:
        prompt += f"- They listed incorrect symptoms: {', '.join(wrong_symptoms)}\n"
        prompt += f"- The actual symptoms are: {', '.join(correct_symptoms)}\n"
    
    if origin_corrections:
        try:
            wrong_origin = origin_corrections[0][0].split("'")[1]
            right_origin_parts = origin_corrections[0][1].split(": ")
            right_origin = right_origin_parts[1] if len(right_origin_parts) > 1 else "unknown regions"
            prompt += f"- They claimed it originated in {wrong_origin} when it actually came from {right_origin}\n"
        except (IndexError, KeyError):
            # If there's any issue with the format, use a more generic message
            prompt += f"- They provided incorrect origin information\n"
    
    if affected_corrections:
        try:
            wrong_affected = affected_corrections[0][0].split("'")[1]
            right_affected_parts = affected_corrections[0][1].split(": ")
            right_affected = right_affected_parts[1] if len(right_affected_parts) > 1 else "various populations"
            prompt += f"- They said it affects {wrong_affected} when it actually affects {right_affected}\n"
        except (IndexError, KeyError):
            # If there's any issue with the format, use a more generic message
            prompt += f"- They provided incorrect information about affected populations\n"
    
    prompt += """
    Write a snarky correction as if typing to someone spreading misinformation.
    Start with something like "uhmm actwaully" and make it clear you're the expert.
    Keep it under 120 words, make it sting with your condescension, and don't use bullet points.
    Don't ask questions - just correct them firmly while sounding like a real person.
    """
    
    return prompt

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
    
    initial_summary = call_ollama_api(build_disease_prompt(disease_data))
    return fact_check_disease_info(initial_summary, disease_data)

if __name__ == "__main__":
    # Test cases
    print("===== TEST CASE 1: ACCURATE INFORMATION =====")
    covid_data = DiseaseVector(
        disease_name="COVID-19",
        symptoms={
            "fever": 0.9, "cough": 0.8, "fatigue": 0.7,
            "shortness of breath": 0.6, "loss of taste or smell": 0.5,
            "headache": 0.5, "sore throat": 0.4
        },
        transmission=normalize_transmission_data(
            from_locations=["Asia", "Europe"],
            to_locations=["Global"]
        )
    )
    print(call_ollama_api(build_disease_prompt(covid_data)))
    print("\n")
    
    print("===== TEST CASE 2: MISINFORMATION CORRECTION =====")
    fake_summary = """
    The Corona-20 disease is a respiratory condition that most likely will have mild 
    symptoms. Patients may experience rash, seizures, and mild joint pain. The disease 
    first emerged in Africa and South America. It affects primarily Europe and 
    Australia. Most cases are mild and resolve within a few days with proper rest 
    and hydration. Some patients report lingering effects that may last for several 
    weeks after the initial infection clears.
    """
    print(fact_check_disease_info(fake_summary, covid_data))
    print("\n")
    
    print("===== TEST CASE 3: GENERATE AND VERIFY =====")
    print(generate_and_verify_disease_summary(
        disease_name="Avian Influenza",
        symptoms={
            "fever": 0.9, "cough": 0.8, "sore throat": 0.7,
            "muscle aches": 0.6, "headache": 0.5, "shortness of breath": 0.5,
            "conjunctivitis": 0.3
        },
        transmission_from=["Asia", "Africa"],
        transmission_to=["Europe", "North America"]
    ))