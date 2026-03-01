import google.generativeai as genai
import os

genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

def generate_weekly_summary():
    # Load your latest data
    with open('data/processed_lookbook.csv', 'r') as f:
        data_summary = f.read()
    
    prompt = f"""
    Analyze my training data for the last 7 days:
    {data_summary}
    
    Context: I am 45+, targeting sub-1:30 1/2-marathon and sub-3:15 marathon. 
    Constraint: I only run Wed or Thu, Sat and Sun. Others are Soleus/Core days.
    Goal: Prove I am running 'Pain-Free' after a 10kg loss.
    
    Write a 200-word update for my GitHub README and social media. 
    Focus on the relationship between my metric distance (km) and my lack of pain.
    """
    
    response = model.generate_content(prompt)
    print(response.text)

if __name__ == "__main__":
    generate_weekly_summary()