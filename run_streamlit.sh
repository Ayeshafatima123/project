#!/bin/bash

# Streamlit App Runner for SurveyRewards

echo "🎯 Starting SurveyRewards Streamlit App..."
echo ""

# Check if Streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit is not installed."
    echo "📦 Installing Streamlit..."
    pip install --break-system-packages streamlit pandas
    echo ""
fi

# Navigate to project directory
cd /mnt/c/Users/ahmed/OneDrive/Desktop/p.g

# Check if database exists, if not it will be created
if [ ! -f "survey_rewards.db" ]; then
    echo "📊 Database will be created on first run..."
    echo ""
fi

# Start Streamlit app
echo "✅ Starting Streamlit app on http://localhost:8501"
echo "📝 Press Ctrl+C to stop the server"
echo ""

streamlit run streamlit_app.py --server.headless true --server.port 8501
