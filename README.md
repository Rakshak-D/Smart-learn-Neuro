
---

# 🧠 SmartLearnNeuro

[![Django](https://img.shields.io/badge/Django-4.2-brightgreen)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST-blue)](https://www.django-rest-framework.org/)
[![GitHub Issues](https://img.shields.io/badge/Report_Issues-Here-red)](https://github.com/Rakshak-D/Smart-learn-Neuro/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SmartLearnNeuro** is an accessible, Django-based e-learning platform designed to empower neurodiverse learners, including those with dyslexia and ADHD. With a focus on personalization and inclusivity, it provides adaptive learning experiences, robust accessibility features, and a user-friendly interface to enhance education for all.

![Platform Overview](https://via.placeholder.com/1500x600.png?text=SmartLearnNeuro+Dashboard+Preview)

---

## ✨ Key Features

### ♿ Accessibility
- **Customizable Settings**: Adjust font size, dyslexia-friendly fonts (e.g., OpenDyslexic), high contrast modes, and color blindness filters.
- **Assistive Tools**: Text-to-speech, screen reader optimization, keyboard navigation, and reading guides.
- **Neurodiverse Support**: Tailored settings for dyslexia (e.g., letter spacing, simplified language) and ADHD (e.g., focus timers, break reminders).

### 👤 User Management
- **Secure Authentication**: User registration, login, and logout with role-based access.
- **Profile Customization**: Personalize learning preferences, accessibility settings, and progress tracking.
- **Learning Conditions**: Support for ADHD, dyslexia, and standard learners with condition-specific optimizations.

### 📚 Learning Components
- **Lessons & Assessments**: Structured content delivery with interactive assessments (details inferred; specifics limited in provided files).
- **Adaptive Learning Paths**: Personalized pacing and difficulty adjustments based on user performance.
- **Progress Tracking**: Monitor completed lessons, engagement levels, and learning streaks.

### 🤖 AI Integration
- **Adaptive Learning**: AI-driven content adjustments for difficulty and pacing (assumed functionality based on context).
- **Reward System**: Gamification with points, levels, and achievements to boost engagement, especially for ADHD learners.

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.9+
- **PostgreSQL**: 14+ (recommended; SQLite used in development)
- **Node.js**: 18+ (for frontend dependencies)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Rakshak-D/Smart-learn-Neuro.git
   cd Smart-learn-Neuro
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: `.venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Create a `.env` file in the project root:
   ```bash
   echo "SECRET_KEY=your-secret-key-here" > .env
   echo "DEBUG=True" >> .env
   echo "DATABASE_URL=postgres://user:password@localhost:5432/smartlearnneuro" >> .env
   ```

5. **Set Up Database**:
   - Update `DATABASES` in `settings.py` with your PostgreSQL credentials if not using `.env`.
   - Run migrations:
     ```bash
     python manage.py migrate
     ```
   - Create a superuser:
     ```bash
     python manage.py createsuperuser
     ```

6. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

### Access Endpoints
- **Home**: `http://localhost:8000/`
- **Admin Dashboard**: `http://localhost:8000/admin/`
- **User Profile**: `http://localhost:8000/users/profile/`
- **Accessibility Settings**: `http://localhost:8000/accessibility/settings/`
- **Lessons**: `http://localhost:8000/lessons/` (assumed based on templates)

---

## 🌐 System Overview

### Architecture Diagram
```mermaid
graph TD
    A[User] --> B{Authentication}
    B -->|Authenticated| C[Profile Manager]
    B -->|Guest| D[Public Pages]
    C --> E[Accessibility Settings]
    C --> F[Learning Modules]
    E --> G[(PostgreSQL)]
    F --> G
    F --> H[AI Engine]
```

### Data Flow
```mermaid
sequenceDiagram
    participant U as User
    participant S as System
    participant D as Database
    
    U->>S: Login/Register
    S->>D: Verify Credentials
    D-->>S: User Data
    S->>U: Dashboard
    
    U->>S: Update Accessibility Settings
    S->>D: Save Settings
    D-->>S: Success
    S->>U: Updated Interface
```

---

## 🛠 Technology Stack

| **Component**     | **Technologies**                          |
|-------------------|-------------------------------------------|
| **Frontend**      | HTML5, CSS3, JavaScript, Bootstrap, HTMX  |
| **Backend**       | Django 4.2, Django REST Framework         |
| **Database**      | PostgreSQL (production), SQLite (dev)     |
| **Accessibility** | OpenDyslexic font, Chart.js for visuals   |
| **Security**      | CSRF protection, session management       |

---

## 📂 Repository Structure
```
Smart-learn-Neuro/
├── accessibility/     # Accessibility features and settings
│   ├── models/        # Dyslexia, ADHD, and general settings
│   ├── middleware/    # Request/response processing
│   └── templates/     # Accessibility UI components
├── users/            # User authentication and profiles
│   ├── models/       # CustomUser with learning conditions
│   └── views/        # Login, register, profile management
├── templates/        # Base templates and error pages
├── static/           # CSS, JS, and other static assets
└── manage.py         # Django management script
```

---

## 📝 Core Dependencies
While a `requirements.txt` wasn’t provided, inferred dependencies include:
```text
Django==4.2.11
djangorestframework==3.15.1
psycopg2-binary==2.9.9  # PostgreSQL adapter
python-dotenv==1.0.0
```

---

## 🐛 Issue Reporting
[![GitHub Issues](https://img.shields.io/badge/Report_Issues-Here-red)](https://github.com/Rakshak-D/Smart-learn-Neuro/issues)

**Bug Report Template**:
```markdown
## Description
[What went wrong?]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Observe issue]

**Expected Behavior**
[What should happen?]

**Actual Behavior**
[What actually happens?]

**Environment**
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- Python Version: [e.g., 3.9]

**Additional Context**
[Screenshots, logs, etc.]
```

**Labels**:
- `bug` - Code issues
- `enhancement` - Feature requests
- `accessibility` - Accessibility-related concerns

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


## 📬 Contact & Support
**Maintainer**: Rakshak D  
📧 [rakshakmce@gmail.com](mailto:rakshakmce@gmail.com)  
🔗 [GitHub Profile](https://github.com/Rakshak-D)

---

## 🛠️ Development Roadmap

### Upcoming Features
- **AI Enhancements**: Real-time learning pace adjustments.
- **Mobile App**: Progressive Web App support.
- **Multilingual Support**: Interface translations.
- **Analytics Dashboard**: Detailed learning insights.

### Contribution Guide
1. Fork the repository.
2. Create a branch (`git checkout -b feat/new-feature`).
3. Commit changes (`git commit -m "Add new feature"`).
4. Push to your branch (`git push origin feat/new-feature`).
5. Open a Pull Request.

**Standards**:
- Adhere to PEP 8.
- Write clear commit messages.
- Include docstrings for major functions.

---
# 👥 Contributors

This project is made possible by the dedicated efforts of our team:

## Backend & AI/ML
- **Rakshak D**  
  [GitHub Profile](https://github.com/Rakshak-D) | Core Architecture & Recommendation Systems
- **Pranathi R**  
  [GitHub Profile](https://github.com/Pranathi38) | Database Design & NLP Integration

## Frontend & Deployment
- **Inchara P**  
  [GitHub Profile](https://github.com/inchara1702) | UI/UX Design & Accessibility Features
- **Sushmindra S.V**  
  [GitHub Profile](https://github.com/sushamindra) | Deployment Pipeline & Performance Optimization

---

### 🌟 Full Contributor Recognition
[![Contributors Graph](https://contrib.rocks/image?repo=Rakshak-D/Smart-learn-Neuro)](https://github.com/Rakshak-D/Smart-learn-Neuro/graphs/contributors)

**Want to join us?**  
We welcome contributions! Check out our:  
🔹 [Development Roadmap](https://github.com/Rakshak-D/Smart-learn-Neuro/wiki/Roadmap)  
🔹 [Contribution Guidelines](https://github.com/Rakshak-D/Smart-learn-Neuro/blob/main/CONTRIBUTING.md)

*Together, we're redefining accessible education!* 🧠✨
