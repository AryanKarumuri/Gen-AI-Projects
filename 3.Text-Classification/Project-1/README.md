# Sentiment Analysis using Hugging Face Transformers

This Python notebook demonstrates how to use Hugging Face's `transformers` library to perform sentiment analysis on a given set of text inputs. The script uses a pre-trained model to classify the sentiment of each input text as either **Positive** or **Negative**.

## Requirements

Make sure to have the following Python package installed:

- `transformers`: The Hugging Face library for natural language processing (NLP).

You can install it using `pip`:

```bash
pip install transformers
```

## How It Works

The script uses a pre-trained sentiment analysis model from Hugging Face’s `transformers` library, which classifies text as either **Positive** or **Negative** based on the content of the input sentence.

- The script imports the `pipeline` function from the Hugging Face `transformers` library.
- The `pipeline("sentiment-analysis")` initializes a pre-trained sentiment analysis model, which is ready to classify the sentiment of text.
- The function `prediction` takes a sentence as input, runs the sentiment analysis using the pre-trained model (`classifier`), and returns the sentiment label (`'POSITIVE'` or `'NEGATIVE'`).

The model outputs a sentiment label along with a score that represents the model's confidence in its prediction.

Sentiment analysis is useful for a wide range of applications, such as analyzing user feedback, social media sentiment, or product reviews.

## Customization

- You can modify the `sample_texts` list to analyze your own set of sentences.
- You can change the model used by the `pipeline` by passing a model name or path as a parameter, for example:
  
  ```bash
  classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
  ```

## Conclusion

This script provides a simple and effective way to apply sentiment analysis to a list of text inputs using Hugging Face’s `transformers` library, and it prints the sentiment of each input text. You can easily adapt it for more complex NLP tasks or use different models for more specialized tasks.



