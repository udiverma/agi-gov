from flask import Flask, render_template, request, jsonify
from disease_misinformation import (
    DiseaseVector, TransmissionInfo, normalize_transmission_data,
    generate_and_verify_disease_summary, fact_check_disease_info
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/social-monitor')
def social_monitor():
    return render_template('social_monitor.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/api/analyze-post', methods=['POST'])
def analyze_post():
    """API endpoint to analyze a post for misinformation"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Extract data from the request
        disease_name = data.get('disease', '')
        symptoms_list = data.get('symptoms', [])
        origins_list = data.get('origins', [])
        affected_list = data.get('affected', [])
        post_text = data.get('post_text', '')
        
        # Convert symptoms list to dictionary format with confidence scores
        symptoms = {symptom: 0.9 for symptom in symptoms_list}
        
        # Create disease vector
        disease_data = DiseaseVector(
            disease_name=disease_name,
            symptoms=symptoms,
            transmission=normalize_transmission_data(
                from_locations=origins_list,
                to_locations=affected_list
            )
        )
        
        # Check the post for misinformation
        corrected_text = fact_check_disease_info(post_text, disease_data)
        
        # Check if corrections were made
        has_corrections = len(corrected_text) > len(post_text)
        
        # Generate corrections list
        corrections = []
        
        # Simple parsing to extract corrections
        if has_corrections:
            correction_part = corrected_text.split("\n\n")[-1] if "\n\n" in corrected_text else ""
            if correction_part:
                # Extract individual corrections
                if "disease name" in correction_part:
                    corrections.append("Incorrect disease name detected")
                if "symptoms" in correction_part:
                    corrections.append("Incorrect symptoms listed")
                if "originated" in correction_part or "origin" in correction_part:
                    corrections.append("Incorrect origin location")
                if "affects" in correction_part or "affecting" in correction_part:
                    corrections.append("Incorrect affected areas")
        
        # Generate a response
        response = {
            'original_text': post_text,
            'corrected_text': corrected_text,
            'has_misinformation': has_corrections,
            'corrections': corrections,
            'disease_data': {
                'name': disease_name,
                'symptoms': symptoms_list,
                'origins': origins_list,
                'affected': affected_list
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-reply', methods=['POST'])
def generate_reply():
    """API endpoint to generate a reply to misinformation"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Extract data from the request
        disease_name = data.get('disease', '')
        symptoms_list = data.get('symptoms', [])
        origins_list = data.get('origins', [])
        affected_list = data.get('affected', [])
        post_text = data.get('post_text', '')
        
        # Convert symptoms list to dictionary format with confidence scores
        symptoms = {symptom: 0.9 for symptom in symptoms_list}
        
        # Create disease vector
        disease_data = DiseaseVector(
            disease_name=disease_name,
            symptoms=symptoms,
            transmission=normalize_transmission_data(
                from_locations=origins_list,
                to_locations=affected_list
            )
        )
        
        # Generate a verified summary and correction
        response_text = generate_and_verify_disease_summary(
            disease_name=disease_name,
            symptoms=symptoms,
            transmission_from=origins_list,
            transmission_to=affected_list
        )
        
        return jsonify({
            'reply': response_text,
            'post_text': post_text,
            'disease_data': {
                'name': disease_name,
                'symptoms': symptoms_list,
                'origins': origins_list,
                'affected': affected_list
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)