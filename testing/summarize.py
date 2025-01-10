from transformers import pipeline

def summarize_text():
    print("Enter the text you want to summarize:")
    user_input = input()
    
    # Load the summarization pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Summarize the input text
    try:
        summary = summarizer(user_input, max_length=130, min_length=30, do_sample=False)
        print("\nSummary:")
        print(summary[0]['summary_text'])
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    summarize_text()
