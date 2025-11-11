"""
Hotel Lead Magnet Backend
Automated report generation and email delivery
"""
import googlemaps
from datetime import datetime
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from datetime import datetime
import json
import threading

# Import SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("⚠️ SendGrid not installed - email functionality disabled")

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://delightful-pavlova-1439dc.netlify.app",
            "http://localhost:*",
            "https://*.netlify.app"
            "https://lovable.dev",
            "https://*.lovable.dev"
        ]
    }
})  # Enable CORS for your frontend

# Configuration from environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'daleb@bunten.ca')  # Must be verified in SendGrid
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Validate required environment variables
if not ANTHROPIC_API_KEY:
    print("WARNING: ANTHROPIC_API_KEY not set!")
if not SENDGRID_API_KEY:
    print("WARNING: SENDGRID_API_KEY not set! Email functionality will be disabled.")
if not FROM_EMAIL:
    print("WARNING: FROM_EMAIL not set!")
if not GOOGLE_MAPS_API_KEY:
    print("WARNING: GOOGLE_MAPS_API_KEY not set!")

# Initialize Anthropic client
client = None
if ANTHROPIC_API_KEY:
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✅ Anthropic client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Anthropic client: {e}")
else:
    print("❌ Cannot initialize Anthropic client - API key missing")

# Initialize Google Maps client
gmaps = None
if GOOGLE_MAPS_API_KEY:
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        print("✅ Google Maps client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Google Maps client: {e}")
else:
    print("❌ Cannot initialize Google Maps client - API key missing")

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Hotel Lead Magnet Backend',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Detailed health check"""
    checks = {
        'anthropic_client': client is not None,
        'anthropic_api_key': ANTHROPIC_API_KEY is not None and len(ANTHROPIC_API_KEY) > 10,
        'sendgrid_configured': SENDGRID_API_KEY is not None and SENDGRID_AVAILABLE,
        'from_email': FROM_EMAIL is not None,
        'google_maps_configured': gmaps is not None
    }
    
    all_healthy = all(checks.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }), 200 if all_healthy else 503

@app.route('/api/find-competitors', methods=['POST', 'OPTIONS'])
def find_competitors():
    """
    Find competitor hotels near target hotel
    Returns: target hotel location + list of competitors
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        hotel_name = data.get('hotel_name')
        city = data.get('city')
        state = data.get('state', '')
        
        print(f"Finding competitors for: {hotel_name}, {city}, {state}")
        
        if not gmaps:
            return jsonify({
                'error': 'Google Maps not configured',
                'message': 'Google Maps API key is missing'
            }), 500
        
        # Step 1: Geocode target hotel
        search_query = f"{hotel_name}, {city}, {state}"
        geocode_result = gmaps.geocode(search_query)
        
        if not geocode_result:
            return jsonify({
                'error': 'Hotel not found',
                'message': f'Could not find {hotel_name} in {city}'
            }), 404
        
        # Extract location
        target_location = geocode_result[0]['geometry']['location']
        target_lat = target_location['lat']
        target_lng = target_location['lng']
        
        print(f"Target hotel location: {target_lat}, {target_lng}")
        
        # Step 2: Search for nearby hotels (2 mile radius = 3,219 meters)
        nearby_results = gmaps.places_nearby(
            location=(target_lat, target_lng),
            radius=3219,  # 2 miles in meters
            type='lodging',
            keyword='hotel'
        )
        
        # Step 3: Process competitors
        competitors = []
        target_name_lower = hotel_name.lower()
        
        for place in nearby_results.get('results', []):
            place_name = place.get('name', '')
            
            # Skip if it's the target hotel (fuzzy match)
            if target_name_lower in place_name.lower() or place_name.lower() in target_name_lower:
                continue
            
            # Skip if no location
            if 'geometry' not in place or 'location' not in place['geometry']:
                continue
            
            comp_location = place['geometry']['location']
            comp_lat = comp_location['lat']
            comp_lng = comp_location['lng']
            
            # Calculate distance
            distance_miles = calculate_distance(
                target_lat, target_lng,
                comp_lat, comp_lng
            )
            
            competitors.append({
                'name': place_name,
                'lat': comp_lat,
                'lng': comp_lng,
                'rating': place.get('rating', 0),
                'reviews': place.get('user_ratings_total', 0),
                'price_level': place.get('price_level', 0),
                'distance_miles': round(distance_miles, 2),
                'place_id': place.get('place_id', ''),
                'address': place.get('vicinity', '')
            })
        
        # Sort by distance
        competitors.sort(key=lambda x: x['distance_miles'])
        
        # Limit to 15 closest
        competitors = competitors[:15]
        
        print(f"Found {len(competitors)} competitors")
        
        return jsonify({
            'success': True,
            'target': {
                'name': hotel_name,
                'lat': target_lat,
                'lng': target_lng,
                'address': geocode_result[0].get('formatted_address', '')
            },
            'competitors': competitors,
            'total_count': len(competitors)
        })
        
    except Exception as e:
        print(f"Error finding competitors: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to find competitors',
            'message': str(e)
        }), 500

def generate_and_send_report_background(data):
    """
    Background task to generate and send report
    This runs in a separate thread to avoid timeout
    """
    try:
        hotel_name = data.get('hotelName')
        city = data.get('city')
        state = data.get('state')
        address = data.get('address', 'Not provided')
        email = data.get('email')
        
        print(f"🤖 [Background] Generating report for {hotel_name}...")
        report_html = generate_hotel_report(hotel_name, city, state, address)
        print(f"✅ [Background] Report generated ({len(report_html)} chars)")
        
        # Only send email if SendGrid is configured
        if SENDGRID_API_KEY and SENDGRID_AVAILABLE:
            send_report_email(data, report_html)
            print(f"📨 [Background] Report email sent to {email}")
        else:
            print(f"⚠️ [Background] SendGrid not configured - report generated but not sent")
            print(f"⚠️ [Background] Report saved (would send to: {email})")
            # In production, you could save to database or file here
        
    except Exception as e:
        print(f"❌ [Background] Error generating/sending report: {e}")
        import traceback
        print(f"❌ [Background] Traceback:\n{traceback.format_exc()}")

@app.route('/api/generate-report', methods=['POST', 'OPTIONS'])
def generate_report():
    """
    Main endpoint: receives form data, generates report, sends email
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get form data
        data = request.json
        
        if not data:
            print("❌ No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"📥 Received data: {data.keys()}")
        
        hotel_name = data.get('hotelName')
        city = data.get('city')
        state = data.get('state')
        address = data.get('address', 'Not provided')
        contact_name = data.get('contactName')
        email = data.get('email')
        phone = data.get('phone', 'Not provided')
        role = data.get('role', 'Not specified')
        
        # Validate required fields
        if not all([hotel_name, city, state, contact_name, email]):
            missing = []
            if not hotel_name: missing.append('hotelName')
            if not city: missing.append('city')
            if not state: missing.append('state')
            if not contact_name: missing.append('contactName')
            if not email: missing.append('email')
            print(f"❌ Missing fields: {missing}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        print(f"📧 New lead: {hotel_name} from {contact_name} ({email})")
        
        # Step 1: Send immediate confirmation email (if SendGrid is configured)
        if SENDGRID_API_KEY and SENDGRID_AVAILABLE:
            try:
                send_confirmation_email(data)
                print(f"✅ Confirmation email sent to {email}")
            except Exception as e:
                print(f"⚠️ Confirmation email failed: {e}")
                print(f"⚠️ Continuing without confirmation email...")
        else:
            print(f"⚠️ SendGrid not configured - skipping confirmation email")
            print(f"⚠️ Note: User will only receive report email")
        
        # Step 2: Start background thread to generate and send report
        # This prevents timeout issues
        background_thread = threading.Thread(
            target=generate_and_send_report_background,
            args=(data,),
            daemon=True
        )
        background_thread.start()
        print(f"🚀 Background report generation started for {hotel_name}")
        
        # Return success immediately
        return jsonify({
            'success': True,
            'message': f'Report is being generated and will be sent to {email} within 10 minutes.',
            'hotel': hotel_name
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error: {str(e)}")
        print(f"❌ Traceback:\n{error_details}")
        return jsonify({
            'error': str(e),
            'message': 'Internal server error - check logs for details'
        }), 500

def generate_hotel_report(hotel_name, city, state, address):
    """
    Generate comprehensive hotel report using Claude API
    """
    
    if not client:
        raise Exception("Anthropic client not initialized - check API key")
    
    prompt = f"""Generate a comprehensive Public Signals Performance Report for this hotel property.

Property Details:
- Hotel Name: {hotel_name}
- Location: {city}, {state}
- Address: {address}

IMPORTANT: Create a detailed HTML report analyzing the following 10 categories. Use actual web research and public data signals to score each category 0-100:

1. OTA Ranking Position (TripAdvisor, Booking.com, Expedia)
2. Listing Completeness (photos, amenities, descriptions)
3. Organic Visibility & SEO (brand search presence)
4. Paid Media & Brand Protection
5. Social Media & Engagement (Facebook, Instagram)
6. Direct Booking Mix (commission leakage risk)
7. E-commerce & User Experience
8. Revenue Management (ADR positioning)
9. Leakage Detection (secondary OTAs)
10. Reputation & Review Management

For each category provide:
- Score (0-100)
- Color (GREEN ≥75, AMBER 50-74, RED <50)
- Key insight (2-3 sentences)
- Top recommendations

Calculate an overall score (average of all 10).

Identify the #1 KEY FINDING: the single most important revenue opportunity or risk.

Format the response as a complete, professional HTML email report with:
- Performance-colored section headers
- Visual score badges
- Clear insights and recommendations
- Professional styling (inline CSS)
- Mobile-responsive design

The HTML should be ready to send as an email body (complete HTML document with inline styles).
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        report_html = message.content[0].text
        
        # Extract just the HTML if Claude wrapped it in markdown
        if '```html' in report_html:
            report_html = report_html.split('```html')[1].split('```')[0].strip()
        elif '```' in report_html:
            report_html = report_html.split('```')[1].split('```')[0].strip()
            
        return report_html
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        raise

def send_confirmation_email(data):
    """
    Send immediate confirmation email via SendGrid
    """
    try:
        print(f"📧 Attempting to send confirmation email to {data['email']}...")
        
        if not SENDGRID_API_KEY or not SENDGRID_AVAILABLE:
            raise Exception("SendGrid not configured")
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
                Your Report is Being Generated! 🎯
            </h2>
            
            <p>Hi <strong>{data['contactName']}</strong>,</p>
            
            <p>Thank you for requesting a <strong>Public Signals Performance Report</strong> for <strong>{data['hotelName']}</strong>.</p>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                <h3 style="margin-top: 0; color: #1e3A8A;">📋 Hotel Details:</h3>
                <ul style="list-style: none; padding: 0;">
                    <li>📍 <strong>Property:</strong> {data['hotelName']}</li>
                    <li>🏙️ <strong>Location:</strong> {data['city']}, {data['state']}</li>
                    <li>🏠 <strong>Address:</strong> {data.get('address', 'Not provided')}</li>
                    <li>📧 <strong>Report Email:</strong> {data['email']}</li>
                </ul>
            </div>
            
            <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <strong>⏰ Timeline:</strong> Your comprehensive report is being generated now and will arrive in your inbox within 5-10 minutes!
            </div>
            
            <h3 style="color: #1e293b;">📊 What's Being Analyzed:</h3>
            <ul style="line-height: 1.8;">
                <li>✅ OTA Rankings & Visibility</li>
                <li>✅ SEO & Organic Search</li>
                <li>✅ Social Media Engagement</li>
                <li>✅ Review Management</li>
                <li>✅ Revenue Positioning</li>
                <li>✅ Distribution Analysis</li>
                <li>✅ E-commerce Experience</li>
                <li>✅ Listing Quality</li>
                <li>✅ Brand Protection</li>
                <li>✅ Direct Booking Opportunities</li>
            </ul>
            
            <p>Questions? Just reply to this email.</p>
            
            <p>Best regards,<br>
            <strong>Your Hotel Analytics Team</strong></p>
            
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #64748b;">
                Report requested on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=data['email'],
            subject=f"Your Hotel Performance Report for {data['hotelName']} is Being Generated",
            html_content=html_content
        )
        
        print(f"📧 Sending via SendGrid...")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Confirmation email sent! Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error sending confirmation email: {str(e)}")
        import traceback
        print(f"❌ Traceback:\n{traceback.format_exc()}")
        raise

def send_report_email(data, report_html):
    """
    Send the generated report via email using SendGrid
    """
    try:
        if not SENDGRID_API_KEY or not SENDGRID_AVAILABLE:
            raise Exception("SendGrid not configured")
        
        # Wrap report in email-friendly format
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
            <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
                <p>Hi {data['contactName']},</p>
                <p>Your comprehensive Public Signals Performance Report for <strong>{data['hotelName']}</strong> is ready!</p>
                <hr style="border: none; border-top: 2px solid #e5e7eb; margin: 20px 0;">
                {report_html}
                <hr style="border: none; border-top: 2px solid #e5e7eb; margin: 20px 0;">
                <p style="font-size: 14px; color: #64748b;">
                    Questions about your report? Reply to this email and we'll help you understand the findings and recommendations.
                </p>
                <p>Best regards,<br><strong>Your Hotel Analytics Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=data['email'],
            subject=f"Your Hotel Performance Report - {data['hotelName']}",
            html_content=email_html
        )
        
        print(f"📧 [Report] Sending via SendGrid...")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ [Report] Email sent! Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ [Report] Error sending report email: {str(e)}")
        raise

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points in miles
    Using Haversine formula
    """
    R = 3959  # Radius of Earth in miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

if __name__ == '__main__':
    # For local development and Railway
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
