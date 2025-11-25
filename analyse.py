import os
import logging
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from typing import List
import json
import google.generativeai as genai
from transformers import pipeline, CamembertTokenizer, AutoModelForSequenceClassification

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prompt for comment extraction
PROMPT_EXTRACT = """Extract all user comments from this screenshot.

Return the comments as a JSON array of strings. Just the array, nothing else.

Rules:
- Include only the actual comment text, not usernames, timestamps, or UI elements
- Each comment should be a separate string in the array
- Preserve the original text exactly as written
- If a comment spans multiple lines, keep it as one string
- Skip empty or duplicate comments
- Maintain the order of comments as they appear

Example output format:
["First comment here", "Second comment here", "Third comment here"]
"""

def load_models():
    """
    Load models for sentiment analysis.
    
    Returns:
        tuple: sentiment pipeline
    """
    logger.info("="*80)
    logger.info("MODEL LOADING")
    logger.info("="*80)
    
    try:
        logger.info("Loading sentiment analysis model...")
        model_name = "cmarkea/distilcamembert-base-sentiment"
        
        # Force the use of the Python-based tokenizer to avoid "Fast" version issues
        tokenizer = CamembertTokenizer.from_pretrained(model_name, token=HF_TOKEN)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, token=HF_TOKEN)

        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=-1
        )
        logger.info("Sentiment model loaded successfully")
        
        logger.info("="*80)
        logger.info("SENTIMENT MODEL LOADED SUCCESSFULLY")
        logger.info("="*80)
        
        return sentiment_pipeline
        
    except Exception as e:
        logger.error(f"Error loading models: {e}", exc_info=True)
        raise


def extract_comments_from_screenshot(image_path: str):
    """
    Extract comments from screenshot using Gemini API.
    
    Args:
        image_path: Path to the screenshot image
        
    Returns:
        list: Extracted comment texts
    """
    try:
        logger.info(f"Processing image: {image_path}")
        
        uploaded_file = genai.upload_file(image_path)
        logger.info(f"Image uploaded successfully")
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "response_mime_type": "application/json",
            }
        )
        
        response = model.generate_content([PROMPT_EXTRACT, uploaded_file])
        
        result = json.loads(response.text)
        
        if isinstance(result, list):
            comments_list = result
        elif isinstance(result, dict):
            comments_list = result.get("content", result.get("comments", []))
        else:
            logger.warning(f"Unexpected response format: {type(result)}")
            comments_list = []
        
        logger.info(f"Extracted {len(comments_list)} comment(s)")
        
        if len(comments_list) == 0:
            logger.warning(f"Raw response: {response.text[:500]}")
        
        return comments_list
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for {image_path}: {e}")
        if 'response' in locals():
            logger.error(f"Raw response: {response.text[:500]}")
        return []
    except Exception as e:
        logger.error(f"Error extracting comments from {image_path}: {e}", exc_info=True)
        return []


def analyze_sentiment_french(text: str, sentiment_model):
    """
    Analyze sentiment of French text, with robust handling for different model outputs.
    
    Args:
        text: Text to analyze
        sentiment_model: Sentiment analysis pipeline
        
    Returns:
        tuple: (sentiment_label, confidence_score)
    """
    try:
        result = sentiment_model(text[:512])[0]
        label = result['label']
        score = result['score']

        # Robust handling for different label formats
        label_lower = label.lower()

        if 'star' in label_lower:
            # This handles the output of models like 'nlptown/bert-base-multilingual-uncased-sentiment'.
            # This strongly suggests that the intended model ('cmarkea/distilcamembert-base-sentiment')
            # may not have loaded correctly.
            logger.warning(f"Unexpected 'star' label found: '{label}'. Mapping to standard sentiment.")
            if label_lower in ['1 star', '2 stars']:
                return 'negative', score
            elif label_lower == '3 stars':
                return 'neutral', score
            else: # 4 and 5 stars
                return 'positive', score
        
        # This is the expected path for 'cmarkea/distilcamembert-base-sentiment'
        # which returns 'POSITIVE', 'NEGATIVE', 'NEUTRAL'.
        if label_lower in ['positive', 'negative', 'neutral']:
            return label_lower, score
        
        # Fallback for any other unexpected labels
        logger.warning(f"Unexpected label format: '{label}'. Defaulting to neutral.")
        return "neutral", score
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
        return "neutral", 0.0


def identify_topic_and_theme(text: str):
    """
    Identify topic and theme using Gemini API.
    
    Args:
        text: Comment text to analyze
        
    Returns:
        tuple: (topic, theme)
    """
    try:
        # Prompt for Gemini
        prompt = f"""
Analyze the following user comment and generate a relevant 'topic' and 'theme'.

Comment: "{text}"

Rules:
- The 'theme' should be a single, high-level category (e.g., "Qualité de service", "Problème technique", "Avis général").
- The 'topic' should be a more specific sub-category of the theme (e.g., "Réactivité du support", "Panne de réseau", "Félicitations").
- Both topic and theme must be in French.
- Provide the output as a JSON object with two keys: "topic" and "theme". Do not include ```json ```.

Example:
Comment: "Votre connexion est nulle, ça coupe tout le temps !"
Output:
{{
  "topic": "Coupures fréquentes",
  "theme": "Problème de connexion"
}}
"""
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "response_mime_type": "application/json",
            }
        )
        
        response = model.generate_content(prompt)
        
        result = json.loads(response.text)
        
        topic = result.get("topic", "Généré par IA")
        theme = result.get("theme", "Généré par IA")
        
        logger.debug(f"Generated Theme: {theme}, Generated Topic: {topic}")
        
        return topic, theme
        
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error parsing topic/theme from Gemini: {e}")
        logger.error(f"Raw response from Gemini: {response.text[:500]}")
        return "Non défini", "Non défini"
    except Exception as e:
        logger.error(f"Error identifying topic/theme with Gemini: {e}", exc_info=True)
        return "Non défini", "Non défini"


def process_multiple_images(
    image_paths: List[str],
    sentiment_model
):
    """
    Process multiple screenshots and create structured dataset.
    
    Args:
        image_paths: List of image file paths
        sentiment_model: Sentiment analysis pipeline
    
    Returns:
        pd.DataFrame: Structured dataset with all analyzed comments
    """
    all_data = []
    total_images = len(image_paths)
    
    for img_idx, img_path in enumerate(image_paths, 1):
        logger.info("="*80)
        logger.info(f"Processing image {img_idx}/{total_images}: {img_path}")
        logger.info("="*80)
        
        comments = extract_comments_from_screenshot(img_path)
        
        if not comments:
            logger.warning(f"No comments found in {img_path}")
            continue
        
        for comment_idx, comment in enumerate(comments, 1):
            if not comment.strip() or len(comment) < 10:
                continue
            
            logger.info(f"Analyzing comment {comment_idx}/{len(comments)}")
            
            sentiment, confidence = analyze_sentiment_french(
                comment,
                sentiment_model
            )
            
            topic, theme = identify_topic_and_theme(
                comment
            )
            
            all_data.append({
                'image_source': os.path.basename(img_path),
                'comment': comment,
                'sentiment': sentiment,
                'confidence': round(confidence, 4),
                'topic': topic,
                'theme': theme
            })
            
            logger.info(f"Comment: {comment[:80]}...")
            logger.info(f"Result: sentiment={sentiment} (conf={confidence:.2f}), topic={topic}, theme={theme}")
    
    df = pd.DataFrame(all_data)
    
    logger.info("="*80)
    logger.info(f"PROCESSING COMPLETE: {len(df)} comments analyzed")
    logger.info("="*80)
    
    return df


def test_gemini_api():
    """
    Performs a simple test call to the Gemini API to check for connectivity and authentication.
    """
    try:
        logger.info("Testing Gemini API connection...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        # Using a simple text generation instead of JSON to minimize failure points for the test
        model.generate_content("Hello")
        logger.info("Gemini API connection successful.")
        return True
    except Exception as e:
        logger.error("="*80)
        logger.error("FATAL: Gemini API test call failed.")
        logger.error("This means that although a GOOGLE_API_KEY was found, it is likely invalid,")
        logger.error("the API is not enabled in your Google Cloud project, or a firewall is blocking the connection.")
        logger.error(f"Underlying error: {e}")
        logger.error("="*80)
        return False

def main():
    """
    Main execution function.
    """
    # Verify that the Google API key is available
    if not GOOGLE_API_KEY:
        logger.error("="*80)
        logger.error("FATAL: GOOGLE_API_KEY not found.")
        logger.error("Please make sure your .env file is correctly set up with your Google API key.")
        logger.error("="*80)
        return  # Stop execution

    # Test Gemini API connection
    if not test_gemini_api():
        return  # Stop execution if test fails

    sentiment_model = load_models()
    
    images_folder = 'images'
    
    image_paths = []
    image_paths += [str(p) for p in Path(images_folder).glob('*.jpg')]
    image_paths += [str(p) for p in Path(images_folder).glob('*.jpeg')]
    image_paths += [str(p) for p in Path(images_folder).glob('*.png')]
    
    logger.info("="*80)
    logger.info(f"Folder: {images_folder}")
    logger.info(f"Images found: {len(image_paths)}")
    logger.info("="*80)
    
    for img in image_paths:
        logger.info(f"  - {img}")
    
    logger.info("="*80)
    
    if len(image_paths) == 0:
        logger.error(f"No images found in '{images_folder}'")
        logger.error(f"Current directory: {Path.cwd()}")
        return
    
    df_results = process_multiple_images(
        image_paths,
        sentiment_model
    )
    
    if len(df_results) > 0:
        logger.info("="*80)
        logger.info("RESULTS SUMMARY")
        logger.info("="*80)
        
        logger.info(f"\nTotal comments: {len(df_results)}")
        
        logger.info("\nSentiment distribution:")
        logger.info(df_results['sentiment'].value_counts().to_string())
        
        logger.info("\nTop 10 topics:")
        logger.info(df_results['topic'].value_counts().head(10).to_string())
        
        logger.info("\nTheme distribution:")
        logger.info(df_results['theme'].value_counts().to_string())
        
        logger.info(f"\nAverage confidence: {df_results['confidence'].mean():.4f}")
        
        logger.info("\nSentiment by theme:")
        logger.info(pd.crosstab(df_results['theme'], df_results['sentiment']).to_string())
        
        # Sauvegarde des résultats
        output_csv = 'comments_dataset_final.csv'
        df_results.to_csv(output_csv, index=False, encoding='utf-8')
        logger.info(f"\nDataset saved to: {output_csv}")
        
        try:
            output_excel = 'comments_dataset_final.xlsx'
            df_results.to_excel(output_excel, index=False)
            logger.info(f"Dataset also saved to: {output_excel}")
        except Exception as e:
            logger.info(f"Excel export skipped: {e}")
            
        logger.info("\nFirst 10 rows:")
        logger.info(df_results.head(10).to_string())
    else:
        logger.warning("No comments were extracted from any images.")


if __name__ == "__main__":
    main()