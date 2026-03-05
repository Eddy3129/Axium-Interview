Overview
Build a Smart Recipe Analyzer web application that allows users to input a list of ingredients and receive recipe suggestions with nutritional analysis using AI.
Requirements
Frontend (React/Vue/Vanilla JS)
Input Form: Text area for users to enter available ingredients (comma-separated)
Results Display: Show generated recipes with ingredients, instructions, and nutritional info
Loading States: Visual feedback during API calls
Responsive Design: Works on desktop and mobile
Error Handling: Display user-friendly error messages
Backend (Node.js/Python/Any)
Request validation: Ensure ingredients list is not empty
LLM Integration: Connect to OpenAI, Anthropic, or any LLM API
Response formatting: Structure the LLM response consistently
LLM Integration Requirements
Prompt Engineering: Create a structured prompt that asks the LLM to:
Generate 2-3 recipe suggestions using the provided ingredients
Include estimated cooking time and difficulty level
Provide basic nutritional information (calories, protein, carbs)
Format response as JSON for easy parsing

Example LLM response structure:
json
{
  "recipes": [
    {
      "name": "Garlic Butter Pasta",
      "ingredients": ["pasta", "garlic", "butter", "parmesan"],
      "instructions": ["Boil pasta...", "Sauté garlic..."],
      "cookingTime": "20 minutes",
      "difficulty": "Easy",
      "nutrition": {
        "calories": 450,
        "protein": "12g",
        "carbs": "60g"
      }
    }
  ]
}

Deliverables
Working Application
Frontend and backend running locally
Successful ingredient-to-recipe conversion
Clean, intuitive user interface

Git Repository
Make sure to store your code in a public GitHub repository to be shared with us
Commit your changes regularly

Demonstration
Be prepared to:
Walk through your code structure
Explain your prompt engineering approach
Show the application working end-to-end
Discuss any challenges and how you solved them

Bonus Features (If Time Permits)
Dietary Restrictions: Filter recipes by dietary needs
Recipe Rating: Allow users to rate generated recipes
Ingredient Substitutions: Suggest alternatives for missing ingredients
Recipe History: Store previously generated recipes
Image Generation: Generate recipe images using DALL-E or similar

