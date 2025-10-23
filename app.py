from flask import Flask, render_template, request, send_from_directory
import praw
from constants import Config
import os
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from PIL import Image
from comment_screenshot import generate_reddit_comment_dark
from tts_azure import TTSAzure, getAzureVoice
from datetime import datetime
from utils.paths import backgrounds_dir, outputs_dir, list_backgrounds
from utils.time import estimate_narration_time
from services.translation import translate_batch

app = Flask(__name__)

# Initialize config and Reddit client
config = Config()
reddit = praw.Reddit(
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET,
    user_agent=config.USER_AGENT,
)


VIEW_STATE = {}

def _voices_by_language():
    return {
        "english": [getAzureVoice("english")],
        "spanish": [getAzureVoice("spanish")],
    }

 


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        subreddit_name = request.form["subreddit"].strip()
        if not subreddit_name:
            return render_template("index.html", error="Please enter a subreddit name.")

        try:
            subreddit = reddit.subreddit(subreddit_name)
            posts = list(subreddit.top(time_filter="day", limit=10))
            if not posts:
                return render_template("index.html", error="No posts found for today.", backgrounds=list_backgrounds())

            options = []
            for p in posts:
                options.append({
                    "id": p.id,
                    "title": p.title,
                    "author": str(p.author) if p.author is not None else "[deleted]",
                    "score": p.score,
                    "permalink": p.permalink,
                })

            return render_template(
                "index.html",
                subreddit=subreddit_name,
                posts=options,
                backgrounds=list_backgrounds(),
            )

        except Exception as e:
            return render_template("index.html", error=f"Error: {e}", backgrounds=list_backgrounds())

    return render_template("index.html", backgrounds=list_backgrounds())


@app.route("/select_post", methods=["POST"])
def select_post():
    subreddit_name = request.form.get("subreddit", "").strip()
    post_id = request.form.get("post_id", "").strip()
    if not subreddit_name or not post_id:
        return render_template("index.html", error="Missing subreddit or post.", backgrounds=list_backgrounds())

    try:
        submission = reddit.submission(id=post_id)
        submission.comment_sort = "top"
        submission.comments.replace_more(limit=0)
        comments = submission.comments[:10]

        title_time = estimate_narration_time(submission.title)
        enriched_comments = []
        total_time = title_time

        for c in comments:
            narration_time = estimate_narration_time(c.body)
            total_time += narration_time
            enriched_comments.append({
                "id": getattr(c, "id", None),
                "body": c.body,
                "score": c.score,
                "author": str(c.author) if getattr(c, "author", None) is not None else "[deleted]",
                "narration_time": narration_time
            })

        post_snapshot = {
            "id": submission.id,
            "title": submission.title,
            "author": str(submission.author) if submission.author is not None else "[deleted]",
            "score": submission.score,
            "selftext": submission.selftext,
            "permalink": submission.permalink,
        }

        VIEW_STATE[post_snapshot["id"]] = {
            "post": post_snapshot,
            "comments": enriched_comments,
            "title_time": title_time,
            "language": "english",
        }

        return render_template(
            "post.html",
            post=post_snapshot,
            comments=enriched_comments,
            subreddit=subreddit_name,
            title_time=title_time,
            total_time=total_time,
            post_id=post_snapshot["id"],
            backgrounds=list_backgrounds(),
        )

    except Exception as e:
        return render_template("index.html", error=f"Error: {e}", backgrounds=list_backgrounds())


@app.route("/delete_comment", methods=["POST"])
def delete_comment():
    post_id = request.form.get("post_id")
    comment_id = request.form.get("comment_id")
    subreddit_name = request.form.get("subreddit")

    if not post_id or not comment_id:
        return render_template("index.html", error="Invalid delete request.", backgrounds=list_backgrounds())

    state = VIEW_STATE.get(post_id)
    if not state:
        return render_template("index.html", error="Post state not found. Please search again.", backgrounds=list_backgrounds())

    original_len = len(state["comments"])
    state["comments"] = [c for c in state["comments"] if str(c.get("id")) != str(comment_id)]

    title_time = state.get("title_time", 0)
    total_time = title_time + sum(c.get("narration_time", 0) for c in state["comments"])

    VIEW_STATE[post_id] = {
        "post": state["post"],
        "comments": state["comments"],
        "title_time": title_time,
    }

    if "application/json" in (request.headers.get("Accept") or ""):
        return {
            "ok": True,
            "deleted": (original_len != len(state["comments"])),
            "comment_id": comment_id,
            "title_time": title_time,
            "total_time": total_time,
        }
    else:
        return render_template(
            "post.html",
            post=state["post"],
            comments=state["comments"],
            subreddit=subreddit_name,
            title_time=title_time,
            total_time=total_time,
            post_id=post_id,
            deleted=(original_len != len(state["comments"])),
            backgrounds=list_backgrounds(),
        )


@app.route("/edit_comment", methods=["POST"])
def edit_comment():
    post_id = request.form.get("post_id")
    comment_id = request.form.get("comment_id")
    new_body = request.form.get("body", "").strip()
    subreddit_name = request.form.get("subreddit")

    if not post_id or not comment_id:
        return render_template("index.html", error="Invalid edit request.", backgrounds=list_backgrounds())

    state = VIEW_STATE.get(post_id)
    if not state:
        return render_template("index.html", error="Post state not found. Please search again.", backgrounds=list_backgrounds())

    for c in state["comments"]:
        if str(c.get("id")) == str(comment_id):
            c["body"] = new_body
            c["narration_time"] = estimate_narration_time(new_body)
            break

    title_time = state.get("title_time", 0)
    total_time = title_time + sum(c.get("narration_time", 0) for c in state["comments"])

    VIEW_STATE[post_id] = {
        "post": state["post"],
        "comments": state["comments"],
        "title_time": title_time,
    }

    if "application/json" in (request.headers.get("Accept") or ""):
        return {
            "ok": True,
            "comment_id": comment_id,
            "body": new_body,
            "narration_time": next((c.get("narration_time") for c in state["comments"] if str(c.get("id")) == str(comment_id)), None),
            "title_time": title_time,
            "total_time": total_time,
        }
    else:
        return render_template(
            "post.html",
            post=state["post"],
            comments=state["comments"],
            subreddit=subreddit_name,
            title_time=title_time,
            total_time=total_time,
            post_id=post_id,
            edited_comment=True,
            backgrounds=list_backgrounds(),
        )


@app.route("/edit_title", methods=["POST"])
def edit_title():
    post_id = request.form.get("post_id")
    new_title = request.form.get("title", "").strip()
    subreddit_name = request.form.get("subreddit")

    if not post_id:
        return render_template("index.html", error="Invalid edit request.")

    state = VIEW_STATE.get(post_id)
    if not state:
        return render_template("index.html", error="Post state not found. Please search again.")

    state["post"]["title"] = new_title
    title_time = estimate_narration_time(new_title)
    state["title_time"] = title_time
    total_time = title_time + sum(c.get("narration_time", 0) for c in state["comments"])

    VIEW_STATE[post_id] = {
        "post": state["post"],
        "comments": state["comments"],
        "title_time": title_time,
    }

    return render_template(
        "post.html",
        post=state["post"],
        comments=state["comments"],
        subreddit=subreddit_name,
        title_time=title_time,
        total_time=total_time,
        post_id=post_id,
        edited_title=True,
        backgrounds=list_backgrounds(),
    )


@app.route("/backgrounds/<path:filename>")
def get_background(filename):
    return send_from_directory(backgrounds_dir(), filename)


@app.route("/outputs/<path:filename>")
def get_output(filename):
    return send_from_directory(outputs_dir(), filename)


@app.route("/generate_video", methods=["POST"])
def generate_video():
    post_id = request.form.get("post_id")
    subreddit_name = request.form.get("subreddit")
    background_name = request.form.get("background")
    language = request.form.get("language") or VIEW_STATE.get(post_id, {}).get("language", "english")
    selected_voice = request.form.get("voice") or VIEW_STATE.get(post_id, {}).get("voice")

    if not post_id:
        return render_template("index.html", error="No post to generate from.", backgrounds=list_backgrounds())

    state = VIEW_STATE.get(post_id)
    if not state:
        return render_template("index.html", error="Post state not found. Please search again.", backgrounds=_list_backgrounds())

    post = state["post"]
    comments = state["comments"]

    bg_path = os.path.join(backgrounds_dir(), background_name) if background_name else None
    if not bg_path or not os.path.isfile(bg_path):
        # Fallback to configured default if available
        try:
            cfg = Config()
            bg_path = cfg.VIDEO_FILE
        except Exception:
            return render_template("post.html", post=post, comments=comments, subreddit=subreddit_name, title_time=state.get("title_time", 0), total_time=state.get("title_time", 0)+sum(c.get("narration_time",0) for c in comments), post_id=post_id, backgrounds=list_backgrounds(), error="Select a valid background or set default VIDEO_FILE in config.")

    outputs_root = outputs_dir()
    os.makedirs(outputs_root, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = os.path.join(outputs_root, f"{timestamp}")
    os.makedirs(job_dir, exist_ok=True)

    cfg = Config()
    voice_id = selected_voice or getAzureVoice(language)

    # Generate TTS per segment (title + each comment), collect audio and durations
    segments = []
    # Title as first segment
    title_text = post.get("title", "")
    if title_text:
        title_audio = os.path.join(job_dir, "title.mp3")
        TTSAzure(cfg.AZURE_KEY, cfg.AZURE_REGION, title_text, voice_id, title_audio)
        audio_clip = AudioFileClip(title_audio)
        segments.append({"type": "title", "text": title_text, "audio": audio_clip, "duration": audio_clip.duration})

    # Comments
    for idx, c in enumerate(comments):
        text = c.get("body", "") or ""
        if text.strip() == "":
            continue
        audio_path = os.path.join(job_dir, f"comment_{idx}.mp3")
        TTSAzure(cfg.AZURE_KEY, cfg.AZURE_REGION, text, voice_id, audio_path)
        audio_clip = AudioFileClip(audio_path)
        segments.append({"type": "comment", "text": text, "audio": audio_clip, "duration": audio_clip.duration, "author": c.get("author", ""), "score": c.get("score", 0)})

    if not segments:
        return render_template("post.html", post=post, comments=comments, subreddit=subreddit_name, title_time=state.get("title_time", 0), total_time=state.get("title_time", 0)+sum(c.get("narration_time",0) for c in comments), post_id=post_id, backgrounds=list_backgrounds(), error="Nothing to narrate.")

    # Build background clip matching total audio duration (+0.5s buffer similar to buildClip)
    total_audio_duration = sum(s["duration"] for s in segments) + 0.5
    video_full = VideoFileClip(bg_path)
    # Crop to 9:16 using same logic as video_edition.crop_to_9_16
    original_width, original_height = video_full.size
    new_width = original_height * 9 // 16
    x_center = original_width // 2
    x1 = max(0, x_center - new_width // 2)
    x2 = min(original_width, x_center + new_width // 2)
    cropped = video_full.crop(x1=x1, y1=0, x2=x2, y2=original_height)
    if cropped.duration > total_audio_duration:
        start = 0
        end = total_audio_duration
        bg_clip = cropped.subclip(start, end)
    else:
        bg_clip = cropped

    # Avoid resizing here to prevent PIL ANTIALIAS errors on some Pillow versions

    # Concatenate audio clips sequentially
    from moviepy.editor import concatenate_audioclips
    audio_clips = [s["audio"] for s in segments]
    composite_audio = concatenate_audioclips(audio_clips)
    bg_clip = bg_clip.set_audio(composite_audio)

    # Generate screenshots and overlay at center timed to each segment
    overlays = []
    current_start = 0.0
    for idx, s in enumerate(segments):
        if s["type"] == "title":
            img_path = os.path.join(job_dir, f"title.png")
            generate_reddit_comment_dark(username=str(post.get("author", "OP")), time_ago="", likes=str(post.get("score", 0)), comment=s["text"], output_path=img_path)
        else:
            img_path = os.path.join(job_dir, f"comment_{idx}.png")
            generate_reddit_comment_dark(username=str(s.get("author", "user")), time_ago="", likes=str(s.get("score", 0)), comment=s["text"], output_path=img_path)
        # Fit within 90% width and 70% height of background frame using Pillow (avoid MoviePy resize/PIL.ANTIALIAS)
        max_w = int(bg_clip.w * 0.9)
        max_h = int(bg_clip.h * 0.7)
        with Image.open(img_path).convert("RGBA") as im:
            orig_w, orig_h = im.size
            scale = min(max_w / orig_w, max_h / orig_h, 1.0)
            if scale < 1.0:
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                try:
                    resample = Image.Resampling.LANCZOS
                except AttributeError:
                    resample = Image.LANCZOS
                im_resized = im.resize((new_w, new_h), resample=resample)
                resized_path = img_path.replace(".png", "_resized.png")
                im_resized.save(resized_path)
                final_img_path = resized_path
            else:
                final_img_path = img_path
        img_clip = ImageClip(final_img_path).set_duration(s["duration"]).set_start(current_start).set_position("center")
        overlays.append(img_clip)
        current_start += s["duration"]

    final = CompositeVideoClip([bg_clip] + overlays)
    out_name = f"short_{timestamp}.mp4"
    out_path = os.path.join(job_dir, out_name)
    final.write_videofile(out_path, codec="libx264")

    # Close clips
    for ac in audio_clips:
        ac.close()
    video_full.close()
    bg_clip.close()
    final.close()

    title_time = state.get("title_time", 0)
    total_time = title_time + sum(c.get("narration_time", 0) for c in comments)
    if "application/json" in (request.headers.get("Accept") or ""):
        return {
            "ok": True,
            "video_url": f"/outputs/{timestamp}/{out_name}",
        }
    else:
        return render_template(
            "post.html",
            post=post,
            comments=comments,
            subreddit=subreddit_name,
            title_time=title_time,
            total_time=total_time,
            post_id=post_id,
            backgrounds=list_backgrounds(),
            generated_video=f"/outputs/{timestamp}/{out_name}",
            current_language=language,
        )


@app.route("/set_language", methods=["POST"])
def set_language():
    post_id = request.form.get("post_id")
    subreddit_name = request.form.get("subreddit")
    language = request.form.get("language", "english")
    if not post_id:
        return render_template("index.html", error="No post found.", backgrounds=list_backgrounds())
    state = VIEW_STATE.get(post_id)
    if not state:
        return render_template("index.html", error="Post state not found.", backgrounds=list_backgrounds())
    state["language"] = language
    # Reset voice to default for language if not explicitly set
    voices = _voices_by_language().get(language, [])
    if voices:
        state["voice"] = voices[0]
    title_time = state.get("title_time", 0)
    total_time = title_time + sum(c.get("narration_time", 0) for c in state["comments"])
    if "application/json" in (request.headers.get("Accept") or ""):
        return {
            "ok": True,
            "language": language,
            "voices": voices,
            "voice": state.get("voice"),
        }
    else:
        return render_template(
            "post.html",
            post=state["post"],
            comments=state["comments"],
            subreddit=subreddit_name,
            title_time=title_time,
            total_time=total_time,
            post_id=post_id,
            backgrounds=list_backgrounds(),
            current_language=language,
            language_set=True,
        )


@app.route("/set_voice", methods=["POST"])
def set_voice():
    post_id = request.form.get("post_id")
    subreddit_name = request.form.get("subreddit")
    voice = request.form.get("voice")
    if not post_id or not voice:
        return {"ok": False, "error": "Missing post or voice."}, 400
    state = VIEW_STATE.get(post_id)
    if not state:
        return {"ok": False, "error": "Post state not found."}, 404
    # Validate voice belongs to current language
    language = state.get("language", "english")
    if voice not in _voices_by_language().get(language, []):
        return {"ok": False, "error": "Voice not valid for current language."}, 400
    state["voice"] = voice
    return {"ok": True, "language": language, "voice": voice}


 


@app.route("/translate_content", methods=["POST"])
def translate_content():
    post_id = request.form.get("post_id")
    subreddit_name = request.form.get("subreddit")
    # Use currently selected language
    target_language = None
    if post_id in VIEW_STATE:
        target_language = VIEW_STATE[post_id].get("language", "english")
    else:
        target_language = "english"
    if not post_id:
        return render_template("index.html", error="No post found.", backgrounds=list_backgrounds())
    state = VIEW_STATE.get(post_id)
    if not state:
        return render_template("index.html", error="Post state not found.", backgrounds=list_backgrounds())

    title = state["post"].get("title", "")
    bodies = [c.get("body", "") for c in state["comments"]]
    texts = [title] + bodies
    translated = translate_batch(texts, target_language)
    if len(translated) != len(texts):
        return render_template("post.html", post=state["post"], comments=state["comments"], subreddit=subreddit_name, title_time=state.get("title_time",0), total_time=state.get("title_time",0)+sum(c.get("narration_time",0) for c in state["comments"]), post_id=post_id, backgrounds=list_backgrounds(), error="Translation failed.")

    new_title = translated[0]
    new_comments = []
    total_time = estimate_narration_time(new_title)
    for c, new_body in zip(state["comments"], translated[1:]):
        nt = estimate_narration_time(new_body)
        total_time += nt
        new_comments.append({
            "id": c.get("id"),
            "body": new_body,
            "score": c.get("score"),
            "author": c.get("author"),
            "narration_time": nt,
        })

    state["post"]["title"] = new_title
    state["comments"] = new_comments
    state["title_time"] = estimate_narration_time(new_title)
    state["language"] = target_language

    if "application/json" in (request.headers.get("Accept") or ""):
        return {
            "ok": True,
            "language": target_language,
            "title": state["post"]["title"],
            "comments": [{"id": c["id"], "body": c["body"], "narration_time": c["narration_time"]} for c in state["comments"]],
            "title_time": state["title_time"],
            "total_time": total_time,
        }
    else:
        return render_template(
            "post.html",
            post=state["post"],
            comments=state["comments"],
            subreddit=subreddit_name,
            title_time=state["title_time"],
            total_time=total_time,
            post_id=post_id,
            backgrounds=list_backgrounds(),
            current_language=target_language,
            translated=True,
        )

if __name__ == "__main__":
    app.run(debug=True)

