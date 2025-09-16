import praw
from constants import Config
from contentGen import getReddit, getSubmissions
from bs4 import BeautifulSoup
from markdown import markdown
import re

def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html)
    html = re.sub(r'<code>(.*?)</code >', ' ', html)
    html = re.sub(r'~~(.*?)~~', ' ', html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    return text

def getComments(submission):
    submission.comment_sort = 'top'
    submission.comment_limit = 10
    max_words_per_comment = 100
    comments = []
    for comment in submission.comments:
        if isinstance(comment, praw.models.MoreComments):
            continue
        comment_text = markdown_to_text(comment.body_html)
        words = comment_text.split()
        if len(words) > max_words_per_comment:
            continue
        comments.append(comment_text)
    return comments

if __name__ == "__main__":
    config = Config()
    reddit = getReddit(config.CLIENT_ID, config.CLIENT_SECRET, config.USER_AGENT)
    subreddit = "AskReddit"
    submissions = getSubmissions(subreddit, reddit, 3)

    posts = []

    submission_list = list(submissions)
    for submission in submission_list:
        comments = getComments(submission)
        post = {'title': submission.title, 'comments': comments}
        posts.append(post)

    for post in posts:
        print(f"Title: {post['title']}")
        print(f"Comment count: {len(post['comments'])}")
        for comment in post['comments']:
            print(f"Comment: {comment}")
        print("-" * 40)
