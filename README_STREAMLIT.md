# 🎯 SurveyRewards - Streamlit App

A complete survey rewards platform built with Streamlit. Users can register, complete surveys, earn rewards, and withdraw funds.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_streamlit.txt
```

### 2. Run the App

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## 📱 Features

### ✅ User Authentication
- **Register** - Create account with email, username, password
- **Login** - Secure login with email and password
- **Referral System** - Earn $1.00 for each friend who joins
- **Auto-verification** - Users are verified on registration

### ✅ Home Page
- Landing page with platform overview
- Statistics display (total paid, users, surveys)
- How it works section
- Featured surveys preview
- Quick access to login/register

### ✅ User Dashboard
- Current balance display
- Total earned and withdrawn
- Surveys completed count
- Referral code display
- Available surveys list
- Recent transactions

### ✅ Surveys
- Browse all available surveys
- Filter by category and difficulty
- View survey details
- Complete surveys with various question types:
  - Multiple choice
  - Rating (1-5)
  - Yes/No
  - Text answers
- Track completed surveys

### ✅ Payments & Withdrawals
- Multiple withdrawal methods:
  - EasyPaisa (24-48 hours)
  - JazzCash (24-48 hours)
  - PayPal (2-3 business days)
  - Bank Transfer (3-5 business days)
- Minimum withdrawal: $5.00
- Automatic fee calculation
- Withdrawal history

### ✅ Transaction History
- Complete transaction log
- Survey rewards
- Referral bonuses
- Withdrawals
- Balance tracking

### ✅ Additional Pages
- **FAQ** - Common questions and answers
- **About** - Platform information and mission

## 💰 Earning Structure

- **Survey Rewards**: $0.50 - $5.00 per survey
- **Referral Bonus**: $1.00 per friend
- **Referral Commission**: 10% of referred user's earnings

## 📊 Survey Categories

- Health & Wellness
- Technology
- Shopping
- Finance
- Education
- Entertainment
- Food & Dining
- Travel
- General

## 🗄️ Database

The app uses SQLite database (`survey_rewards.db`) which is automatically created on first run.

Sample data is automatically populated with:
- 6 sample surveys
- Multiple questions per survey
- 4 withdrawal methods

## 🎨 UI Features

- Clean, modern interface
- Responsive sidebar navigation
- Color-coded status indicators
- Metric cards for quick stats
- Expandable FAQ section
- Form validation
- Success/error messages

## 🔒 Security

- Password hashing (SHA-256)
- Session-based authentication
- SQL injection prevention (parameterized queries)
- Input validation

## 📝 How to Use

1. **First Time Setup**:
   ```bash
   pip install -r requirements_streamlit.txt
   streamlit run streamlit_app.py
   ```

2. **Register an Account**:
   - Click "Register" in sidebar
   - Fill in username, email, password
   - Optionally add referral code
   - Click "Create Account"

3. **Login**:
   - Enter email and password
   - Click "Login"

4. **Complete Surveys**:
   - Browse available surveys
   - Click "View" to see details
   - Answer all questions
   - Click "Submit Survey"
   - Earn rewards instantly!

5. **Withdraw Funds**:
   - Navigate to "Withdraw" page
   - Select withdrawal method
   - Enter amount and account details
   - Submit request

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set main file path: `streamlit_app.py`
5. Deploy!

### Deploy to Other Platforms

The app can be deployed to any platform that supports Streamlit:
- Heroku
- AWS
- DigitalOcean
- Railway
- Render

## 📦 Files

- `streamlit_app.py` - Main application file
- `requirements_streamlit.txt` - Python dependencies
- `survey_rewards.db` - SQLite database (auto-created)

## 🐛 Troubleshooting

**App won't start**:
```bash
pip install --upgrade streamlit
```

**Database errors**:
```bash
rm survey_rewards.db
streamlit run streamlit_app.py
```

**Port already in use**:
```bash
streamlit run streamlit_app.py --server.port 8502
```

## 📞 Support

For issues or questions, please check:
- FAQ page in the app
- Streamlit documentation
- GitHub issues

## 📄 License

This project is for educational and demonstration purposes.

---

**Enjoy earning money with SurveyRewards!** 💰
