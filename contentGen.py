from datetime import datetime
from moviepy.editor import os
from openai import OpenAI
import yaml
from pydantic import BaseModel
from constants import Config 
import praw

def getReddit(client_id, client_secret, user_agent) -> praw.Reddit:
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

def getSubmissions(subreddit, reddit: praw.Reddit, number_of_submissions):
    subreddit = reddit.subreddit(subreddit)
    submissions = subreddit.top(time_filter="day", limit=number_of_submissions)
    return submissions

def getCommentsHTML(submission):
    submission.comment_sort = 'top'
    submission.comment_limit = 3
    commentsHTML = []
    for comment in submission.comments:
        if isinstance(comment, praw.models.MoreComments):
            continue
        commentsHTML.append(comment.body_html)
    print(commentsHTML)
    

class shortStory(BaseModel):
    title: str
    description: str
    tags: list[str]

def formatSubmission(openai_key: str, title: str, description: str, output_language: str, target_dir: str, id: str):
    openaiClient = OpenAI(api_key=openai_key)
    model = "gpt-4o-mini"
    systemPrompt = f"""
        You are a content creator. 
        Your task is to enhance the provided content by:
        1. Censoring any delicate or sensitive words using appropriate synonyms.
        2. Improving the grammar.
        3. Making apropiate tags for the video.
        4. Removing any text that is not directly suitable for narration (e.g., descriptions of emotions or actions that aren't meant to be read aloud).
        5. Expanding any abbreviations that is not directly suitable for narration into their full form (e.g., "21yo" should become "21 years old", "22F" should become "22 female", etc.).
        You should not modify the content beyond what is mentioned above.
        All output must be writen in the {output_language} language.
    """
    
    userPrompt = f"""
        Here is the content you need to transform:
        title: {title}
        Description: {description}
    """
    completion = openaiClient.beta.chat.completions.parse(
        model=model,
        messages = [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt},
        ],
        response_format=shortStory,
    )
    result = completion.choices[0].message
    if result.refusal:
        print("The model refused to complete the task.")
        return 
    if result.parsed == None:
        return
    data: shortStory = result.parsed
    text = f"{data.title}\n{data.description}"
    text_file = f"{id}{output_language}.txt"
    metadata_file = f"{id}{output_language}.yaml"
    save_text_to_file(text, os.path.join(target_dir, text_file))
    save_metadata_to_yaml(data.title, len(data.description), data.tags, os.path.join(target_dir, metadata_file))
    print("The model has completed the task.")


def save_text_to_file(text: str, filename: str):
     with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

def read_text_from_file(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def save_metadata_to_yaml(title: str, description_length: int, tags: list[str], filename: str):
    data = {
        "title": title,
        "description_length": description_length,
        "tags": tags
    }
    with open(filename, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

def read_metadata_from_yaml(filename: str) -> dict:
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = Config()
    reddit = getReddit(config.CLIENT_ID, config.CLIENT_SECRET, config.USER_AGENT)
    submissions = getSubmissions(config.SUBREDDIT, reddit, 5)

    """
    submission_list = list(submissions)
    for submission in submission_list:
        getCommentsHTML(submission)

    """

    submissions_list = list(submissions)
    for index, submission in enumerate(submissions_list):
        print(f"{index}: {submission.title}")

    k = input("Press enter to confirm or other key to exit: ")
    if k != "":
        exit()
    print("Processing submissions...")
    target_dir = os.path.join(config.OUTPUT_DIR, config.CONTENT_DIR)
    os.makedirs(target_dir, exist_ok=True)
    languages = config.LANGUAGES
    for index, submission in enumerate(submissions_list):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        print(f"Formatted time: {formatted_time}")
        for language in languages:
            formatSubmission(config.OPENAI_API_KEY, submission.title, submission.selftext, language, target_dir, formatted_time)


