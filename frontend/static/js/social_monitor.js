// Sample data for demonstration
const diseasesData = {
    'post-1': {
      disease: 'COVID-19',
      symptoms: ['fever', 'cough', 'fatigue', 'shortness of breath', 'loss of taste or smell', 'headache', 'sore throat'],
      origins: ['Asia', 'Europe'],
      affected: ['Global']
    },
    'post-2': {
      disease: 'Avian Influenza',
      symptoms: ['fever', 'cough', 'sore throat', 'muscle aches', 'headache', 'shortness of breath', 'conjunctivitis'],
      origins: ['Asia', 'Africa'],
      affected: ['Europe', 'North America']
    },
    'post-3': {
      disease: 'COVID-19',
      symptoms: ['fever', 'cough', 'fatigue', 'shortness of breath', 'loss of taste or smell', 'headache', 'sore throat'],
      origins: ['Asia', 'Europe'],
      affected: ['Global']
    }
  };
  
  const postContents = {
    'post-1': "Did you know that Corona-20 started in Africa? The symptoms include seizures, rash, and joint pain. It's hitting Australia and Europe hard right now. Stay safe everyone! 🦠 #healthfacts #pandemic #CoronaVirus",
    'post-2': "The Avian Flu is NOT from Asia like they're telling you. It actually originated in South America and is spreading to North America only. Symptoms you should watch for are dizziness and fainting. 🐦 #TruthReveal #AvianFlu",
    'post-3': "COVID-19 is a respiratory disease that commonly causes fever, cough, fatigue, shortness of breath, and loss of taste or smell. It emerged from Asia and Europe and has spread globally. Most people recover within a few weeks, but some experience long-term effects. Stay informed and follow health guidelines."
  };
  
  const generatedReplies = {
    'post-1': "uhmm actwaully... it's COVID-19, not Corona-20. As the leading expert on this, I'm obligated to correct your embarrassing misinformation. The disease emerged from Asia and Europe, NOT Africa. And I can't believe you're listing seizures and rash as symptoms! The actual symptoms are fever, cough, fatigue, shortness of breath, and loss of taste/smell. And it's affecting the ENTIRE WORLD, not just Australia and Europe. Do your research before posting next time, jeez.",
    'post-2': "uhmm actwaully... as THE expert on Avian Influenza, I have to call you out on this nonsense. Avian Flu originates from Asia and Africa, NOT South America. And those symptoms? Laughably wrong. The REAL symptoms include fever, cough, sore throat, muscle aches, headache, and shortness of breath. Also, it affects both Europe AND North America, not just North America. Maybe actually check your facts before embarrassing yourself online?",
    'post-3': "Actually, this information is accurate. The post correctly identifies COVID-19's primary symptoms and geographic spread. Good job providing accurate health information!"
  };
  
  const corrections = {
    'post-1': [
      "Incorrect disease name: \"Corona-20\" instead of \"COVID-19\"",
      "Incorrect symptoms: \"seizures, rash, joint pain\" are not primary symptoms",
      "Incorrect origin: \"Africa\" instead of \"Asia, Europe\"",
      "Incorrect affected areas: \"Australia and Europe\" instead of \"Global\""
    ],
    'post-2': [
      "Incorrect origin: \"South America\" instead of \"Asia, Africa\"",
      "Incorrect symptoms: \"dizziness and fainting\" are not primary symptoms",
      "Incorrect affected areas: \"North America only\" instead of \"Europe, North America\""
    ],
    'post-3': [
      "No misinformation detected. This post contains accurate information about COVID-19."
    ]
  };
  
  // Currently selected post
  let selectedPostId = null;
  
  // Functions
  function selectPost(postId) {
    // Clear previous selection
    document.querySelectorAll('.post').forEach(post => {
      post.classList.remove('selected');
    });
    
    // Select new post
    document.getElementById(postId).classList.add('selected');
    selectedPostId = postId;
  }
  
  function showLoading() {
    document.getElementById('loading-indicator').style.display = 'block';
    document.getElementById('initial-message').style.display = 'none';
    document.getElementById('analysis-content').style.display = 'none';
  }
  
  function hideLoading() {
    document.getElementById('loading-indicator').style.display = 'none';
    document.getElementById('analysis-content').style.display = 'block';
  }
  
  function updateAnalysisPanel(postId) {
    const diseaseData = diseasesData[postId];
    
    // Update disease info
    document.getElementById('disease-name').textContent = diseaseData.disease;
    
    // Update symptoms tags
    const symptomsContainer = document.getElementById('symptoms-tags');
    symptomsContainer.innerHTML = '';
    diseaseData.symptoms.forEach(symptom => {
      const tag = document.createElement('span');
      tag.className = 'tag symptom';
      tag.textContent = symptom;
      symptomsContainer.appendChild(tag);
    });
    
    // Update locations
    document.getElementById('origin-locations').textContent = diseaseData.origins.join(', ');
    document.getElementById('affected-locations').textContent = diseaseData.affected.join(', ');
    
    // Update corrections
    const correctionsContainer = document.getElementById('corrections-list');
    correctionsContainer.innerHTML = '';
    corrections[postId].forEach(correction => {
      const p = document.createElement('p');
      p.textContent = correction;
      correctionsContainer.appendChild(p);
    });
    
    // Update reply
    document.getElementById('reply-content').textContent = generatedReplies[postId];
    
    // Update form values for custom analysis
    document.getElementById('disease-input').value = diseaseData.disease;
    document.getElementById('symptoms-input').value = diseaseData.symptoms.join(', ');
    document.getElementById('origins-input').value = diseaseData.origins.join(', ');
    document.getElementById('affected-input').value = diseaseData.affected.join(', ');
    document.getElementById('post-input').value = postContents[postId];
    
    // Set analysis time
    document.getElementById('analysis-time').textContent = 'just now';
  }
  
  function analyzePost(postId) {
    if (!postId && !selectedPostId) {
      alert('Please select a post first');
      return;
    }
    
    const targetPostId = postId || selectedPostId;
    showLoading();
    
    // In a real implementation, this would make an AJAX call to the backend API
    // For demonstration, we'll use the sample data with a simulated delay
    
    // Sample API call (commented out):
    // fetch('/api/analyze-post', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({
    //     post_text: postContents[targetPostId],
    //     disease: diseasesData[targetPostId].disease,
    //     symptoms: diseasesData[targetPostId].symptoms,
    //     origins: diseasesData[targetPostId].origins,
    //     affected: diseasesData[targetPostId].affected
    //   })
    // })
    // .then(response => response.json())
    // .then(data => {
    //   // Process data and update UI
    //   hideLoading();
    // })
    // .catch(error => {
    //   console.error('Error:', error);
    //   hideLoading();
    //   alert('An error occurred while analyzing the post');
    // });
    
    // Simulate API call delay
    setTimeout(() => {
      updateAnalysisPanel(targetPostId);
      hideLoading();
    }, 1500);
  }
  
  function generateReply(postId) {
    if (!postId && !selectedPostId) {
      alert('Please select a post first');
      return;
    }
    
    const targetPostId = postId || selectedPostId;
    showLoading();
    
    // In a real implementation, this would make an AJAX call to the backend API
    // For demonstration, we'll use the sample data with a simulated delay
    
    // Sample API call (commented out):
    // fetch('/api/generate-reply', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({
    //     post_text: postContents[targetPostId],
    //     disease: diseasesData[targetPostId].disease,
    //     symptoms: diseasesData[targetPostId].symptoms,
    //     origins: diseasesData[targetPostId].origins,
    //     affected: diseasesData[targetPostId].affected
    //   })
    // })
    // .then(response => response.json())
    // .then(data => {
    //   // Process data and update UI
    //   hideLoading();
    // })
    // .catch(error => {
    //   console.error('Error:', error);
    //   hideLoading();
    //   alert('An error occurred while generating a reply');
    // });
    
    // Simulate API call delay
    setTimeout(() => {
      updateAnalysisPanel(targetPostId);
      hideLoading();
      
      // Scroll to reply section
      document.querySelector('.generated-reply').scrollIntoView({ behavior: 'smooth' });
    }, 1500);
  }
  
  function copyReply() {
    const replyText = document.getElementById('reply-content').textContent;
    navigator.clipboard.writeText(replyText).then(() => {
      const button = document.getElementById('copy-reply');
      button.textContent = 'Copied!';
      setTimeout(() => {
        button.textContent = 'Copy Reply';
      }, 2000);
    });
  }
  
  function customAnalysis() {
    showLoading();
    
    // Get values from form
    const disease = document.getElementById('disease-input').value;
    const symptoms = document.getElementById('symptoms-input').value.split(',').map(s => s.trim());
    const origins = document.getElementById('origins-input').value.split(',').map(s => s.trim());
    const affected = document.getElementById('affected-input').value.split(',').map(s => s.trim());
    const postText = document.getElementById('post-input').value;
    
    // In a real implementation, this would call the API with these values
    // Here we'll simulate a response
    
    // Sample API call (commented out):
    // fetch('/api/generate-reply', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify({
    //     post_text: postText,
    //     disease: disease,
    //     symptoms: symptoms,
    //     origins: origins,
    //     affected: affected
    //   })
    // })
    // .then(response => response.json())
    // .then(data => {
    //   // Update the reply content with the generated reply
    //   document.getElementById('reply-content').textContent = data.reply;
    //   hideLoading();
    //   // Scroll to reply section
    //   document.querySelector('.generated-reply').scrollIntoView({ behavior: 'smooth' });
    // })
    // .catch(error => {
    //   console.error('Error:', error);
    //   hideLoading();
    //   alert('An error occurred while generating a custom reply');
    // });
    
    // Simulate API response
    setTimeout(() => {
      // Create custom reply based on input values
      let customReply = "uhmm actwaully... as THE expert on " + disease + ", I need to correct some things. ";
      
      // Check for disease name mismatch
      if (!postText.includes(disease)) {
        customReply += "First, the disease is called " + disease + ". ";
      }
      
      // Check for symptom mismatches
      customReply += "The real symptoms include " + symptoms.join(", ") + ". ";
      
      // Check for origin mismatches
      customReply += "It originated from " + origins.join(", ") + " and affects " + affected.join(", ") + ". ";
      
      customReply += "Please verify your facts before posting health information online!";
      
      // Update the reply in the UI
      document.getElementById('reply-content').textContent = customReply;
      
      // Update the disease info in the UI
      document.getElementById('disease-name').textContent = disease;
      
      // Update symptoms tags
      const symptomsContainer = document.getElementById('symptoms-tags');
      symptomsContainer.innerHTML = '';
      symptoms.forEach(symptom => {
        const tag = document.createElement('span');
        tag.className = 'tag symptom';
        tag.textContent = symptom;
        symptomsContainer.appendChild(tag);
      });
      
      // Update locations
      document.getElementById('origin-locations').textContent = origins.join(', ');
      document.getElementById('affected-locations').textContent = affected.join(', ');
      
      hideLoading();
      
      // Scroll to reply section
      document.querySelector('.generated-reply').scrollIntoView({ behavior: 'smooth' });
    }, 1500);
  }