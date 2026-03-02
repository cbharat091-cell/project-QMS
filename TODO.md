# TODO: Add Google Gemini API Support

## Task
Add Google Gemini API support to the QMS Document Reviewer using the provided API key: `AIzaSyDGzD70AiaJyUFVpL2J7oderkhS9u16Vqw`

## Steps

### Step 1: Update ai_qms_reviewer.py
- [ ] Add Google Gemini API client/functionality
- [ ] Add GEMINI_API_KEY environment variable support
- [ ] Add gemini_review_document() function
- [ ] Update get_openai_client() to also support getting Gemini key
- [ ] Add command-line option for using Gemini model

### Step 2: Update index.html
- [ ] Add Gemini API key input in the API Key Modal
- [ ] Add Google Gemini API call functionality
- [ ] Update UI to show Gemini model option
- [ ] Update the review logic to use Gemini when API key is available

### Step 3: Test the implementation
- [ ] Verify Python script works with Gemini API
- [ ] Verify HTML frontend works with Gemini API

## Dependent Files
- ai_qms_reviewer.py
- index.html

