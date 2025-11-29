#!/bin/bash

# YelpReviewGym - Quick Launch Script
# Choose which version to run

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║              💪 YELP REVIEW GYM 💪                      ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Choose version to run:"
echo ""
echo "  1️⃣  Standard Version (Simple & Clean)"
echo "      - 3-step workflow"
echo "      - Basic training only"
echo "      - Perfect for demos"
echo ""
echo "  2️⃣  Enhanced Version (Full Featured) ⭐"
echo "      - Progress tracking"
echo "      - Badges & gamification"
echo "      - Leaderboard & analytics"
echo "      - Certification system"
echo "      - Training reports"
echo ""
echo "  3️⃣  Run Both (Side-by-side comparison)"
echo ""
echo "  4️⃣  View Feature List"
echo ""
echo "  5️⃣  Exit"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Standard Version..."
        echo "   Opening at: http://localhost:8501"
        echo ""
        uv run streamlit run run_app.py
        ;;
    2)
        echo ""
        echo "🚀 Starting Enhanced Version..."
        echo "   Opening at: http://localhost:8501"
        echo ""
        uv run streamlit run run_app_enhanced.py
        ;;
    3)
        echo ""
        echo "🚀 Starting Both Versions..."
        echo "   Standard: http://localhost:8501"
        echo "   Enhanced: http://localhost:8502"
        echo ""
        echo "   Press Ctrl+C to stop both"
        echo ""
        uv run streamlit run run_app.py --server.port 8501 &
        uv run streamlit run run_app_enhanced.py --server.port 8502 &
        wait
        ;;
    4)
        echo ""
        cat << 'EOF'
╔══════════════════════════════════════════════════════════╗
║            ENHANCED FEATURES COMPARISON                  ║
╚══════════════════════════════════════════════════════════╝

Standard Version:
  ✅ Business analysis (delights, pains, personas)
  ✅ Scenario generation (bad vs good examples)
  ✅ AI feedback (scoring & improvements)
  
Enhanced Version (ALL OF THE ABOVE PLUS):
  ✅ 📊 Progress tracking (save all attempts)
  ✅ 🏆 Badge system (5 achievement badges)
  ✅ 🥇 Leaderboard (team competition)
  ✅ 🎓 Certification (Bronze/Silver/Gold)
  ✅ 📄 Training reports (export to file)
  ✅ 📈 Analytics dashboard (trends & charts)
  ✅ 🎯 Difficulty levels (easy/medium/hard)
  ✅ ⭐ Instant badges (visual rewards)
  ✅ 📑 Multi-tab interface (organized)
  ✅ 👤 User profiles (track individuals)

Key Benefits:
  • Gamification → More engaging
  • Tracking → See improvement
  • Leaderboard → Team motivation
  • Reports → Documentation
  • Certification → Official credential

Perfect For:
  • Business owners training staff
  • Managers tracking team progress
  • HR departments documenting training
  • Staff members wanting fun practice

EOF
        echo ""
        read -p "Press Enter to return to menu..."
        bash "$0"
        ;;
    5)
        echo ""
        echo "👋 Goodbye!"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please enter 1-5."
        echo ""
        sleep 2
        bash "$0"
        ;;
esac
