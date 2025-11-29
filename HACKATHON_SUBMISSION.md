# YelpReviewGym - Hackathon Submission

## Project Information

**Project Name:** YelpReviewGym

**Elevator Pitch:** Turn customer complaints into training wins. YelpReviewGym uses AI to analyze Yelp reviews and create personalized staff training scenarios with instant feedback, badges, and performance tracking.

---

## Inspiration

Every business owner dreads opening Yelp to find a negative review. But what if those complaints could become your most valuable training tool?

We noticed that **businesses receive hundreds of customer reviews but rarely use them to train their staff**. Restaurant managers print out bad reviews, stick them on bulletin boards, and hope their team learns something. It's inefficient, demotivating, and frankly, doesn't work.

Meanwhile, Yelp's AI technology was getting smarter and more accessible. We asked ourselves: **"What if AI could automatically turn every pain point in your reviews into a personalized training scenario?"**

That's how YelpReviewGym was born.

## What it does

YelpReviewGym is an **AI-powered staff training platform** that transforms Yelp reviews into interactive learning experiences.

### Core Workflow (3 Steps):

1. **Analyze Reviews** 📊
   - Enter any business name and location
   - AI analyzes all Yelp reviews using Yelp AI API
   - Extracts customer delights, pain points, and personas

2. **Generate Scenarios** 🎭
   - AI creates training scenarios based on real pain points
   - Each scenario shows a BAD example (what not to do)
   - And a GOOD example (the right approach)
   - Scenarios are categorized by difficulty (Easy/Medium/Hard)

3. **Practice & Get Feedback** 💬
   - Staff read customer complaints
   - Type their responses
   - Get instant AI feedback with scores (0-10)
   - Receive specific strengths and improvement suggestions

### Enhanced Features (Professional Edition):

- **📈 Progress Tracking** - Every practice session saved with scores and trends
- **🏆 Leaderboard** - Team rankings create friendly competition
- **🎖️ Badges & Achievements** - "First Steps", "Practice Makes Perfect", "Master Trainer", "High Achiever", "Perfect Score"
- **📊 Analytics Dashboard** - Visual score trends, improvement charts, session statistics
- **🎓 Certification System** - Earn Bronze/Silver/Gold certificates based on performance
- **📄 Training Reports** - Comprehensive downloadable session reports
- **👤 User Profiles** - Individual performance tracking across sessions
- **🎯 Difficulty Levels** - Scenarios automatically categorized for progressive learning
- **🗂️ Multi-tab Interface** - Organized view for Training, Analytics, Leaderboard, and Reports
- **⏱️ Session Tracking** - Monitor time spent and scenarios practiced

## How we built it

### Technology Stack:

**Frontend & UI:**
- **Streamlit** - Rapid web app development with Python
- Interactive multi-tab interface with real-time updates
- Responsive design with column layouts and expandable sections

**Backend & AI:**
- **Yelp AI Chat API** - Powers all intelligent review analysis and feedback
- **Python 3.11** - Core application logic
- **Pydantic** - Data validation and settings management
- **JSON** - Lightweight persistence for progress and leaderboard data

**Architecture:**
- **Modular design** with clean separation of concerns
- `config.py` - Environment and settings management
- `schemas.py` - Strongly-typed data models
- `yelp_ai_client.py` - API client with error handling
- `insights_service.py` - Core business logic and prompt engineering
- `enhanced_features.py` - Progress tracking, badges, leaderboard, certification, reports

**Development Tools:**
- **uv** - Fast Python package installer and dependency management
- **Git** - Version control
- **VS Code** - Development environment

### Project Structure:

```
CareRoute/
├── run_app.py                 # Standard version (clean 3-step workflow)
├── run_app_enhanced.py        # Professional version (all features)
├── launch.sh                  # Interactive launcher script
├── demo_interactive.py        # Automated demo script
├── src/yelpreviewgym/
│   ├── config.py             # Settings & environment
│   ├── schemas.py            # Data models
│   ├── yelp_ai_client.py    # Yelp API integration
│   ├── insights_service.py  # AI prompt engineering
│   └── enhanced_features.py # Gamification & tracking
├── training_progress.json    # Auto-generated: User progress
├── leaderboard.json          # Auto-generated: Team rankings
└── .env                      # YELP_API_KEY configuration
```

### Development Process:

1. **Phase 1: MVP** - Built single-file prototype with basic analyze → generate → practice workflow
2. **Phase 2: Modularization** - Refactored into clean, maintainable modules
3. **Phase 3: Enhanced Features** - Added gamification, progress tracking, analytics
4. **Phase 4: Production Polish** - Error handling, prompt optimization, UI refinement
5. **Phase 5: Demo Materials** - Interactive demo script, video script, documentation

## Challenges we ran into

### 1. **Yelp AI API Rate Limits**
**Problem:** Initial prompts were too long (verbose instructions), causing 400 VALIDATION_ERROR responses.

**Solution:** Reduced all prompts by 70-85%, keeping only essential instructions. Used concise JSON schema examples instead of lengthy explanations.

```python
# Before: ~500 characters
"Please analyze the following business and provide detailed..."

# After: ~100 characters
"Analyze reviews. Return JSON: {delights: [...], pains: [...]}"
```

### 2. **JSON Parsing Reliability**
**Problem:** Yelp AI sometimes returned text with JSON embedded, or invalid JSON structures.

**Solution:** Built robust parsing with:
- Extracted JSON blocks using string search (`{` to last `}`)
- Try-catch error handling with fallbacks
- Validation using Pydantic models
- Display of raw responses for debugging

### 3. **State Management Across Steps**
**Problem:** Streamlit reruns entire script on every interaction, losing state.

**Solution:** Used `st.session_state` effectively:
- Stored insights, scenarios, and selected scenario index
- Cleared downstream state when upstream changed
- Preserved user progress across reruns

### 4. **Empty Pain Points Edge Case**
**Problem:** Some businesses had no identifiable pain points, breaking scenario generation.

**Solution:** Added default pain point fallback and explicit empty list checks:

```python
if not pain_points:
    pain_list = "- Customer service issues"  # Default
else:
    pain_list = "\n".join(f"- {p}" for p in pain_points[:2])
```

### 5. **Progress Tracking Persistence**
**Problem:** How to save user progress without a database?

**Solution:** JSON file-based persistence:
- Lightweight and portable
- No external dependencies
- Easy to inspect and debug
- Works locally without cloud setup

### 6. **Balancing Features vs Simplicity**
**Problem:** Too many features could overwhelm users.

**Solution:** Created TWO versions:
- `run_app.py` - Clean, minimal, perfect for demos
- `run_app_enhanced.py` - Full-featured for production
- Let users choose via `launch.sh` interactive menu

## Accomplishments that we're proud of

✅ **Fully Functional MVP** - Built, tested, and deployed in hackathon timeframe

✅ **Production-Ready Code** - Clean architecture, error handling, modular design

✅ **Real Business Impact** - Solves actual pain point for restaurants, retail, and service businesses

✅ **Intelligent Prompt Engineering** - Optimized prompts for consistent, high-quality AI responses

✅ **10 Enhanced Features** - Went beyond MVP with gamification, analytics, certification

✅ **Two Versions** - Standard for simplicity, Enhanced for enterprise

✅ **Complete Demo Suite** - Interactive Python script + video script + documentation

✅ **Zero External Database** - Self-contained, easy deployment with JSON persistence

✅ **Responsive UX** - Intuitive 3-step workflow anyone can understand

✅ **Comprehensive Documentation** - README, video script, inline comments

## What we learned

### Technical Learnings:

1. **Prompt Engineering is Critical** - Shorter, clearer prompts with examples work better than verbose instructions

2. **Streamlit is Powerful but Quirky** - Session state management requires careful thought, but enables rapid prototyping

3. **API Design Matters** - Yelp AI's JSON responses needed robust parsing and validation

4. **Modular Architecture Scales** - Starting with single-file prototype then refactoring paid off

5. **JSON for Persistence is Underrated** - No database? No problem. JSON files work great for MVP

### Product Learnings:

1. **Solve One Problem Well** - Focus on review → training conversion, not trying to be everything

2. **Gamification Works** - Badges and leaderboards make boring training engaging

3. **Progressive Disclosure** - Offer both simple and advanced versions

4. **Real Data is Key** - Using actual Yelp reviews makes scenarios authentic and relatable

5. **Demo is Everything** - Need both UI and script-based demo for different audiences

### Business Learnings:

1. **Market is Huge** - Every business with Yelp reviews is a potential customer

2. **Pain Point is Real** - Talking to restaurant owners validated the problem immediately

3. **Training is Expensive** - Businesses spend $$$ on generic training; custom AI training is disruptive

## What's next for YelpReviewGym

### Short-term (Next 30 days):

- [ ] **Multi-language Support** - Spanish, Chinese, French for international businesses
- [ ] **Mobile Responsive UI** - Optimize for tablets/phones used by staff
- [ ] **Export to PDF** - Print scenarios and certificates
- [ ] **Email Reports** - Automated weekly progress emails to managers
- [ ] **Custom Branding** - Let businesses add their logo and colors

### Medium-term (Next 90 days):

- [ ] **Voice Practice Mode** - Staff speak responses instead of typing
- [ ] **Video Scenarios** - Upload training videos for visual learners
- [ ] **Integration APIs** - Connect to LMS platforms (Workday, SAP)
- [ ] **Team Management** - Admin dashboard for managers to track all staff
- [ ] **Scheduling** - Assign training scenarios with due dates
- [ ] **Compare Competitors** - Analyze your reviews vs competitors

### Long-term (Next Year):

- [ ] **Mobile App** - Native iOS/Android apps
- [ ] **White-label Solution** - License to enterprise training companies
- [ ] **Industry Templates** - Pre-built scenarios for restaurants, retail, hotels
- [ ] **Franchise Support** - Multi-location tracking and reporting
- [ ] **AI Coaching Assistant** - Real-time suggestions during actual customer interactions
- [ ] **Performance Correlation** - Track if training actually improves ratings

### Business Model Ideas:

1. **Freemium** - Free basic version, $49/month for enhanced features
2. **Per-Seat Pricing** - $10/user/month for teams
3. **Enterprise** - Custom pricing for franchises and large organizations
4. **API Access** - Let other platforms integrate our training engine
5. **Consulting** - Help businesses implement and customize

---

## Try It Yourself

### Quick Start:

```bash
# Clone the repo
git clone <your-repo-url>
cd CareRoute

# Install dependencies
uv sync

# Set your Yelp API key
echo "YELP_API_KEY=your_key_here" > .env

# Option 1: Interactive launcher
./launch.sh

# Option 2: Run enhanced version directly
uv run streamlit run run_app_enhanced.py

# Option 3: Run automated demo
uv run python demo_interactive.py
```

### Get Yelp API Key:
1. Visit https://www.yelp.com/developers
2. Create account and app
3. Copy API key to `.env` file

---

## Built With

### Languages & Frameworks:
- **Python 3.11** - Core application language
- **Streamlit 1.37+** - Web application framework
- **Pydantic 2.8+** - Data validation and settings
- **Bash** - Interactive launcher scripts

### Cloud Services & APIs:
- **Yelp AI Chat API** - Review analysis and feedback generation
- **Yelp Fusion API** - Business data and reviews

### Databases & Storage:
- **JSON** - Lightweight local persistence
- No external database required

### Development Tools:
- **uv** - Fast Python package management
- **Git** - Version control
- **VS Code** - IDE with Python extensions

### Key Python Libraries:
- `requests` - HTTP client for API calls
- `pydantic-settings` - Environment configuration
- `pathlib` - Modern file path handling
- `dataclasses` - Structured data models
- `datetime` - Session and timestamp tracking
- `json` - Data serialization

### Deployment & Infrastructure:
- **Local first** - Runs on any machine with Python
- **Portable** - No external dependencies or cloud services required
- **Scalable** - Ready for Docker/cloud deployment

---

## Contact & Links

**GitHub:** [Your GitHub URL]  
**Demo Video:** [Your Video URL]  
**Live Demo:** [Deployed URL if available]  
**Email:** [Your Email]

---

**Built for:** Yelp AI Hackathon  
**Category:** Developer Tools / Business Solutions  
**License:** MIT  
**Status:** Production-Ready ✅
