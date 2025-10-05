"""
Hotel Lead Magnet Backend
Automated report generation and email delivery
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

# Configuration from environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')  # Your email
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # App password
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Hotel Lead Magnet Backend',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """
    Main endpoint: receives form data, generates report, sends email
    """
    try:
        # Get form data
        data = request.json
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
            return jsonify({'error': 'Missing required fields'}), 400
        
        print(f"📧 New lead: {hotel_name} from {contact_name} ({email})")
        
        # Step 1: Send immediate confirmation email
        send_confirmation_email(data)
        print(f"✅ Confirmation email sent to {email}")
        
        # Step 2: Generate report using Claude
        print(f"🤖 Generating report for {hotel_name}...")
        report_html = generate_hotel_report(hotel_name, city, state, address)
        print(f"✅ Report generated ({len(report_html)} chars)")
        
        # Step 3: Send report email
        send_report_email(data, report_html)
        print(f"📨 Report email sent to {email}")
        
        return jsonify({
            'success': True,
            'message': f'Report generated and sent to {email}',
            'hotel': hotel_name
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_hotel_report(hotel_name, city, state, address):
    """
    Generate comprehensive hotel report using Claude API
    """
    
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
    Send immediate confirmation email via SMTP
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = data['email']
        msg['Subject'] = f"Your Hotel Performance Report for {data['hotelName']} is Being Generated"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px;">
                Your Report is Being Generated! 🎯
            </h2>
            
            <p>Hi <strong>{data['contactName']}</strong>,</p>
            
            <p>Thank you for requesting a <strong>Public Signals Performance Report</strong> for <strong>{data['hotelName']}</strong>.</p>
            
            <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                <h3 style="margin-top: 0; color: #1e293b;">📋 Hotel Details:</h3>
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
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")
        raise

def send_report_email(data, report_html):
    """
    Send the generated report via email
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = FROM_EMAIL
        msg['To'] = data['email']
        msg['Subject'] = f"Your Hotel Performance Report - {data['hotelName']}"
        
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
        
        msg.attach(MIMEText(email_html, 'html'))
        
        # Send via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Error sending report email: {str(e)}")
        raise

if __name__ == '__main__':
    # For local development
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
