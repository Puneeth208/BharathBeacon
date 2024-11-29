# Import necessary modules
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Set up the Gemini API with your API key
genai.configure(api_key="AIzaSyAvKRVv-AYQ1z8F4t83F_OKO9h4UjC42PA")  # Replace with your actual API key

# Define a function to get recommendations using the Gemini API
def get_gemini_recommendations(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")  # Use the appropriate Gemini model
    response = model.generate_content(prompt)
    return response.text

# Route to render the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle form submissions and generate recommendations
@app.route('/recommendations', methods=['POST'])
def generate_recommendations():
    data = request.get_json()

    # Extract input values from the request
    experience_type = data['experienceType']
    location = data['location']
    travel_period = data['travelPeriod']
    group_type = data['groupType']
    budget = data['budget']
    special_interests = data.get('specialInterests', '')
    language = data['language']

    # Create the input query for Gemini model
    prompt = f"""Please provide a detailed travel itinerary for a {group_type.lower()} traveler interested in a {budget.lower()} {experience_type.lower()} exploration. The itinerary should focus on the following aspects:
    Language of response : {language}
- **Location**: Include recommendations for areas around {location}.
- **Travel Period**: {travel_period}.
- **Special Interests**: Highlight attractions relevant to {special_interests if special_interests else 'general preferences'}.

**Itinerary Format**:
- **Day-by-Day Breakdown**: Clearly label each day and list activities or places to visit in bullet points.
- **Historical/Relevant Attractions**: Prioritize key landmarks or interests (e.g., forts, museums, or specific local spots).
- **Transportation**: Suggest budget-friendly transportation options and provide travel tips.
- **Accommodation**: Recommend affordable guesthouses, hostels, or budget hotels nearby.
- **Food and Dining**: Mention any local food spots or must-try delicacies.
- **Important Notes**: Include travel tips like safety, local norms, and negotiating with drivers.

The response should follow this structured format:

**Day X: [Day Title]**
- Activities:
  - [Activity 1]
  - [Activity 2]
- Transportation: [Suggestion]
- Accommodation: [Suggestion]
- Dining: [Suggestion]

Ensure the content is practical, concise, and helpful for {group_type.lower()} travelers with a {budget.lower()} budget.
Give the output as a html file in a neat structure way and beautify it with css.Dont't give any pretext just give the code."""

    # Get the response from the Gemini model
    recommendations = get_gemini_recommendations(prompt)
    cleaned_recommendations = recommendations[7:]
    # Return the recommendations along with the prompt for debugging
    return jsonify({
        'prompt': prompt,
        'recommendations': cleaned_recommendations
    })

# Route to generate and download recommendations as a PDF
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()

    # Extract the recommendations from the data
    recommendations_html = data['recommendations']
    
    # Create HTML content with basic styling
    html_content = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f4f4f9;
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                .recommendation {{
                    margin-bottom: 20px;
                    padding: 10px;
                    background-color: #ffffff;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .recommendation ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                .recommendation li {{
                    margin-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <h1>Travel Recommendations</h1>
            <div class="recommendation">
                {recommendations_html}
            </div>
        </body>
    </html>
    """

    # Use WeasyPrint to convert the HTML to a PDF
    pdf = weasyprint.HTML(string=html_content).write_pdf()

    # Create a response with the PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=recommendations.pdf'

    return response

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
