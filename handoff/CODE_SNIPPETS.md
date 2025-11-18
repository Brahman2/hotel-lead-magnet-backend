# Code Snippets - Common Modifications

Quick reference for adding features to your hotel lead magnet system.

---

## ðŸŽ¨ **1. Add Company Logo to Form**

### **In index.html:**

Find the header section and add:

```html
<div style="text-align: center; margin-bottom: 30px;">
    <img src="your-logo-url.png" alt="Company Logo" style="max-width: 200px; height: auto;">
</div>
```

Or upload logo to Netlify and use:
```html
<img src="/logo.png" alt="Company Logo">
```

---

## ðŸ“§ **2. Customize Email Content**

### **In app.py, find `send_confirmation_email()` and modify:**

```python
html_content = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <img src="YOUR_LOGO_URL" style="max-width: 200px;" />
    
    <h2 style="color: #YOUR_BRAND_COLOR;">
        Your Custom Header
    </h2>
    
    <p>Hi <strong>{data['contactName']}</strong>,</p>
    
    <!-- Rest of email -->
</body>
</html>
"""
```

---

## ðŸ’¾ **3. Save Leads to Database**

### **Add to requirements.txt:**
```
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
```

### **In app.py, add at top:**
```python
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    hotel_name = Column(String)
    city = Column(String)
    state = Column(String)
    contact_name = Column(String)
    email = Column(String)
    phone = Column(String)
    role = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    report_sent = Column(String, default='pending')

Base.metadata.create_all(engine)
```

### **In generate_report endpoint, add:**
```python
# Save lead to database
session = Session()
new_lead = Lead(
    hotel_name=hotel_name,
    city=city,
    state=state,
    contact_name=contact_name,
    email=email,
    phone=phone,
    role=role
)
session.add(new_lead)
session.commit()
session.close()
```

---

## ðŸ“Š **4. Add Admin Dashboard Endpoint**

### **In app.py, add:**

```python
@app.route('/admin/leads', methods=['GET'])
def view_leads():
    """Admin endpoint to view all leads"""
    auth = request.headers.get('Authorization')
    if auth != f"Bearer {os.getenv('ADMIN_TOKEN')}":
        return jsonify({'error': 'Unauthorized'}), 401
    
    session = Session()
    leads = session.query(Lead).order_by(Lead.submitted_at.desc()).limit(100).all()
    
    leads_data = [{
        'id': lead.id,
        'hotel_name': lead.hotel_name,
        'city': lead.city,
        'contact_name': lead.contact_name,
        'email': lead.email,
        'submitted_at': lead.submitted_at.isoformat(),
        'report_sent': lead.report_sent
    } for lead in leads]
    
    session.close()
    return jsonify({'leads': leads_data, 'count': len(leads_data)})
```

### **Add to Railway Variables:**
```
ADMIN_TOKEN=your-secret-token-here
```

### **Access:**
```bash
curl -H "Authorization: Bearer your-secret-token-here" \
  https://web-production-13e22.up.railway.app/admin/leads
```

---

## ðŸ”— **5. Add Webhook to Slack/Discord**

### **In app.py, add after successful report:**

```python
import requests

def notify_slack(lead_data):
    """Send notification to Slack when new lead captured"""
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return
    
    message = {
        "text": f"ðŸŽ‰ New Lead Captured!",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Hotel:* {lead_data['hotelName']}\n*Contact:* {lead_data['contactName']}\n*Email:* {lead_data['email']}\n*Location:* {lead_data['city']}, {lead_data['state']}"
                }
            }
        ]
    }
    
    requests.post(webhook_url, json=message)

# In generate_report endpoint, add:
notify_slack(data)
```

### **Add to Railway Variables:**
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## ðŸ“ˆ **6. Add Google Analytics**

### **In index.html, add before `</head>`:**

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### **Track form submissions:**

```javascript
// After successful form submission
gtag('event', 'form_submission', {
  'event_category': 'Lead Generation',
  'event_label': hotelName,
  'value': 1
});
```

---

## ðŸŽ¯ **7. Add Form Validation**

### **In index.html, update form submission:**

```javascript
// Enhanced validation
const email = document.getElementById('email').value;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

if (!emailRegex.test(email)) {
    statusMessage.className = 'status-message error';
    statusMessage.innerHTML = '<strong>Error:</strong> Please enter a valid email address.';
    submitBtn.disabled = false;
    return;
}

// Validate hotel name length
const hotelName = document.getElementById('hotelName').value;
if (hotelName.length < 3) {
    statusMessage.className = 'status-message error';
    statusMessage.innerHTML = '<strong>Error:</strong> Hotel name must be at least 3 characters.';
    submitBtn.disabled = false;
    return;
}
```

---

## ðŸ“„ **8. Generate PDF Reports**

### **Add to requirements.txt:**
```
weasyprint==60.1
```

### **In app.py, add:**

```python
from weasyprint import HTML

def generate_pdf_report(html_content, hotel_name):
    """Convert HTML report to PDF"""
    pdf_path = f'/tmp/{hotel_name.replace(" ", "_")}_report.pdf'
    HTML(string=html_content).write_pdf(pdf_path)
    return pdf_path

# In send_report_email, add PDF attachment:
from email.mime.application import MIMEApplication

pdf_path = generate_pdf_report(report_html, data['hotelName'])
with open(pdf_path, 'rb') as f:
    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
    pdf_attachment.add_header('Content-Disposition', 'attachment', 
                            filename=f"{data['hotelName']}_Report.pdf")
    msg.attach(pdf_attachment)
```

---

## ðŸ”„ **9. Add Follow-up Email Automation**

### **In app.py, add:**

```python
import time
from threading import Timer

def send_followup_email(email, contact_name, hotel_name):
    """Send follow-up email 3 days later"""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=email,
        subject=f"Following up on {hotel_name}'s Performance Report",
        html_content=f"""
        <html>
        <body>
            <p>Hi {contact_name},</p>
            <p>I wanted to follow up on the performance report we sent for {hotel_name}.</p>
            <p>Did you have any questions about the findings?</p>
            <p>Best regards,<br>Your Team</p>
        </body>
        </html>
        """
    )
    
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

# In generate_report endpoint:
# Schedule follow-up for 3 days (259200 seconds)
followup_timer = Timer(259200, send_followup_email, 
                      args=[email, contact_name, hotel_name])
followup_timer.daemon = True
followup_timer.start()
```

---

## ðŸŒ **10. Add Multi-language Support**

### **In index.html, add language selector:**

```html
<select id="language" onchange="changeLanguage()">
    <option value="en">English</option>
    <option value="es">EspaÃ±ol</option>
    <option value="fr">FranÃ§ais</option>
</select>

<script>
const translations = {
    en: {
        title: "Get Your Free Hotel Performance Report",
        submit: "Generate My Free Report"
    },
    es: {
        title: "Obtenga su Informe de Rendimiento Hotelero Gratuito",
        submit: "Generar Mi Informe Gratuito"
    },
    fr: {
        title: "Obtenez Votre Rapport Gratuit de Performance HÃ´teliÃ¨re",
        submit: "GÃ©nÃ©rer Mon Rapport Gratuit"
    }
};

function changeLanguage() {
    const lang = document.getElementById('language').value;
    document.getElementById('formTitle').textContent = translations[lang].title;
    document.getElementById('submitBtn').textContent = translations[lang].submit;
}
</script>
```

---

## ðŸ” **11. Add Rate Limiting**

### **Add to requirements.txt:**
```
flask-limiter==3.5.0
```

### **In app.py:**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per hour"]
)

@app.route('/api/generate-report', methods=['POST'])
@limiter.limit("5 per hour")  # Max 5 reports per hour per IP
def generate_report():
    # ... rest of code
```

---

## ðŸŽ¨ **12. Change Color Scheme**

### **In index.html, update CSS variables:**

```css
:root {
    --primary-color: #YOUR_BRAND_COLOR;
    --secondary-color: #YOUR_ACCENT_COLOR;
    --text-color: #333333;
    --background-color: #FFFFFF;
}

/* Apply throughout */
.button-primary {
    background: var(--primary-color);
}

h1, h2 {
    color: var(--primary-color);
}
```

---

## ðŸ“± **13. Add SMS Notifications (Twilio)**

### **Add to requirements.txt:**
```
twilio==8.10.0
```

### **In app.py:**

```python
from twilio.rest import Client

def send_sms_notification(lead_data):
    """Send SMS when new lead captured"""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    to_number = os.getenv('ADMIN_PHONE_NUMBER')
    
    if not all([account_sid, auth_token, from_number, to_number]):
        return
    
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"New lead: {lead_data['hotelName']} - {lead_data['contactName']} ({lead_data['email']})",
        from_=from_number,
        to=to_number
    )
    print(f"SMS sent: {message.sid}")

# In generate_report endpoint:
send_sms_notification(data)
```

---

## ðŸ’¡ **Tips for Implementation**

1. **Test locally first** with environment variables
2. **Add one feature at a time**
3. **Check Railway logs** after each deployment
4. **Use print statements** for debugging
5. **Handle errors gracefully** with try/except
6. **Document your changes** in comments

---

## ðŸ”„ **Deployment Checklist**

After any code change:

- [ ] Updated code in GitHub
- [ ] Railway auto-deployed (check logs)
- [ ] Tested new endpoint/feature
- [ ] Updated environment variables if needed
- [ ] Verified existing features still work
- [ ] Documented the change

---

**All these snippets are production-ready and can be copy-pasted into your files!**
