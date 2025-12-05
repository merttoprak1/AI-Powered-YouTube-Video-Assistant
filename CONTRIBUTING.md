# Contributing to TubeMind

First off, thank you for considering contributing to TubeMind! It's people like you that make TubeMind such a great tool.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear description** of the proposed feature
- **Use cases** and benefits
- **Possible implementation** approach (optional)

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests if applicable
3. Ensure your code follows the existing style
4. Update documentation as needed
5. Write a clear commit message

## 📝 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/tubemind.git
cd tubemind

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GOOGLE_API_KEY to .env

# Run the app
streamlit run app.py
```

## 🎨 Code Style

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular

## 🧪 Testing

Before submitting a PR:

1. Test the transcript fetching with multiple videos:
   ```bash
   python test_transcript.py VIDEO_ID
   ```

2. Test the main app manually with various video types:
   - Short videos (< 5 min)
   - Long videos (> 1 hour)
   - Videos with only auto-generated captions
   - Videos with manual captions

3. Check for any console errors or warnings

## 📋 Priority Areas

We're particularly interested in contributions for:

- 🌍 Multi-language support
- 📊 Export functionality (PDF, Markdown)
- ⏰ Timestamp integration
- 🎨 UI/UX improvements
- 🐛 Bug fixes
- 📝 Documentation improvements
- ✅ Test coverage

## 💬 Questions?

Feel free to open an issue with the question label, or reach out to the maintainers.

## 📜 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and encourage diverse perspectives
- Focus on what is best for the community
- Show empathy towards other community members

Thank you for contributing! 🎉
