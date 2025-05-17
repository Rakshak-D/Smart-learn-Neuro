# SmartLearn Neuro: AI-Powered Personalized Learning Platform

## Overview
SmartLearn Neuro is a comprehensive AI-powered personalized learning platform specially designed for neurodivergent learners, particularly those with ADHD and dyslexia. The platform leverages adaptive learning technologies to create customized learning experiences based on individual needs, preferences, and learning conditions.

## Key Features

### Features for ADHD Learners
Learners with ADHD often struggle with attention, focus, organization, and time management. These features are designed to help them stay engaged and manage their learning effectively:

1. **Short, Interactive Lessons**  
   - *Purpose*: Lessons are divided into small, digestible segments (5-10 minutes) with interactive elements like quizzes or clickable visuals.  
   - *Benefit*: Prevents overwhelm, sustains attention, and keeps learners engaged through variety and interactivity.

2. **Movement Break Reminders**  
   - *Purpose*: Automated prompts suggest short breaks at customizable intervals (e.g., every 15 minutes) with ideas like stretches or quick activities.  
   - *Benefit*: Addresses restlessness, helping learners refresh and refocus by incorporating physical movement.

3. **Visual Timers and Progress Bars**  
   - *Purpose*: Timers track task duration, and progress bars visually show completion status.  
   - *Benefit*: Improves time management and provides a sense of achievement, motivating learners to continue.

4. **Gamified Rewards System**  
   - *Purpose*: Learners earn points, badges, or unlock levels for completing tasks, with immediate feedback.  
   - *Benefit*: Boosts motivation and focus through instant rewards and a game-like experience.

5. **Focus Mode**  
   - *Purpose*: A mode that hides unnecessary interface elements, disables notifications, and offers optional white noise or calming sounds.  
   - *Benefit*: Reduces distractions, enabling learners to concentrate on the task at hand.

6. **Customizable Learning Paths**  
   - *Purpose*: Learners can select lesson order or pace based on their interests or comfort level.  
   - *Benefit*: Increases engagement by giving control, reducing frustration from rigid structures.

7. **Simplified Navigation and Interface**  
   - *Purpose*: A clean, intuitive design with minimal menus and clear layouts.  
   - *Benefit*: Minimizes cognitive load and prevents learners from getting sidetracked.

### Features for Dyslexia Learners
Dyslexia learners face challenges with reading, writing, and processing text. These features enhance accessibility and support their learning needs:

1. **Text-to-Speech (TTS)**  
   - *Purpose*: Converts all text (lessons, instructions, quizzes) into audio for listening.  
   - *Benefit*: Removes the need to read, making content accessible and reducing cognitive strain.

2. **Adjustable Text Settings**  
   - *Purpose*: Allows customization of font type (e.g., OpenDyslexic), size, color, and background.  
   - *Benefit*: Improves readability by reducing visual stress and tailoring text to individual preferences.

3. **Audio-Based Assessments**  
   - *Purpose*: Quizzes and tests are presented in audio format, with options to respond via speech or selection.  
   - *Benefit*: Eliminates reading and writing barriers, allowing learners to demonstrate knowledge effectively.

4. **Visual Aids and Multimedia**  
   - *Purpose*: Lessons include images, videos, and interactive elements to explain concepts.  
   - *Benefit*: Offers non-text alternatives, supporting comprehension through visual and auditory channels.

5. **Reading Guides**  
   - *Purpose*: Tools like a digital ruler or line highlighter assist in tracking text.  
   - *Benefit*: Reduces the effort of following lines or words, making reading less overwhelming.

6. **Spelling and Grammar Assistance**  
   - *Purpose*: Highlights errors in written responses and suggests corrections.  
   - *Benefit*: Supports writing skill development and boosts confidence in written tasks.

7. **Chunking Content**  
   - *Purpose*: Breaks text into smaller sections with headings and bullet points.  
   - *Benefit*: Makes reading more manageable by presenting information in bite-sized pieces.

### Shared Features for All Learners
These features benefit both groups by enhancing personalization, accessibility, and engagement:

1. **Personalized Learning Paths**  
   - *Purpose*: Adapts content based on the learner's condition, performance, and preferences.  
   - *Benefit*: Tailors the experience to individual needs, improving effectiveness and comfort.

2. **Progress Tracking with Visual Feedback**  
   - *Purpose*: Displays progress through bars, percentages, or badges based on achievements.  
   - *Benefit*: Motivates learners by showing tangible progress, encouraging persistence.

3. **Speech-to-Text (STT)**  
   - *Purpose*: Enables voice input for responses or searches.  
   - *Benefit*: Eases writing for dyslexia learners and speeds up idea capture for ADHD learners.

4. **Customizable Settings Menu**  
   - *Purpose*: A central hub to adjust preferences like break frequency, font size, or TTS settings.  
   - *Benefit*: Empowers learners to personalize the platform easily, promoting independence.

5. **Offline Access**  
   - *Purpose*: Allows downloading of lessons and resources for offline use.  
   - *Benefit*: Supports learning in distraction-free settings or with limited internet access.

6. **Accessibility-First Design**  
   - *Purpose*: Features a high-contrast, clear-font interface with minimal distractions.  
   - *Benefit*: Reduces cognitive load and enhances usability for all learners.

## Technical Features

### AI Capabilities
- **Adaptive Learning Engine**: Dynamically adjusts content difficulty based on performance
- **Personalization Engine**: Creates tailored learning paths based on user preferences and learning conditions
- **Gesture Recognition**: Detects learner engagement through facial expressions and gestures
- **Text-to-Speech & Speech-to-Text**: Provides comprehensive audio support throughout the platform
- **Learning Analytics**: Provides insights into learning patterns and recommends optimal study strategies

### Accessibility Features
- **Dyslexia-friendly Fonts**: OpenDyslexic, Comic Sans, and other readable fonts
- **High Contrast Modes**: Various color schemes for different visual sensitivities
- **Keyboard Navigation**: Complete platform navigation without mouse dependency
- **Screen Reader Compatibility**: ARIA compliance and screen reader optimizations
- **Reading Guides**: Visual tools to aid reading text passages

### User Experience
- **Customizable Interfaces**: Adjust layouts, colors, and element sizes
- **Progressive Web App**: Works offline and can be installed on devices
- **Responsive Design**: Optimized for all screen sizes and devices
- **Simple Navigation**: Clear, consistent navigation patterns
- **Distraction-free Mode**: Focus-enhancing viewing options

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SmartLearn-Neuro.git

# Navigate to project directory
cd SmartLearn-Neuro

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

## Technology Stack
- **Backend**: Django, Django REST Framework
- **AI/ML**: TensorFlow, scikit-learn, NLTK
- **Frontend**: HTML5, CSS3, JavaScript, Vue.js
- **Database**: PostgreSQL
- **Accessibility**: ARIA, OpenDyslexic fonts
- **Deployment**: Docker, Gunicorn, Nginx

## Credits
Developed by the SmartLearn team for the NMIT 2025 Hackathon.

## License
MIT License