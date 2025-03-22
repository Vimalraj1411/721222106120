from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_URL = "http://20.244.56.144/test"

users_details = []
posts_details = []

def fetch_data():
    global users_details, posts_details

    try:
        posts_resp = requests.get(f"{API_URL}/posts", timeout=5)
        comments_resp = requests.get(f"{API_URL}/comments", timeout=5)
        users_resp = requests.get(f"{API_URL}/users", timeout=5)

        if posts_resp.status_code != 200 or comments_resp.status_code != 200 or users_resp.status_code != 200:
            print("Error: API returned a non-200 status code!")
            return

        posts = posts_resp.json()
        comments = comments_resp.json()
        users = users_resp.json()

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return

    user_post_counts = {user['id']: 0 for user in users}
    for post in posts:
        user_post_counts[post['userId']] += 1

    users_details.clear()
    users_details.extend(sorted(
        [{"userId": uid, "post_cnt": count} for uid, count in user_post_counts.items()],
        key=lambda x: x["post_cnt"],
        reverse=True
    )[:5])

    post_comment_counts = {post['id']: 0 for post in posts}
    for comment in comments:
        post_comment_counts[comment['postId']] += 1

    for post in posts:
        post["cmt_count"] = post_comment_counts.get(post["id"], 0)

    posts_details.clear()
    posts_details.extend(posts)


def get_top():

    return jsonify(users_details)

@app.route('/posts', methods=['GET'])
def get_posts():
    post_type = request.args.get('type')

    if post_type == "popular":
        max_comments = max((post["cmt_count"] for post in posts_details), default=0)
        popular_posts = [post for post in posts_details if post["cmt_count"] == max_comments]
        return jsonify(popular_posts)

    if post_type == "latest":
        latest_posts = sorted(posts_details, key=lambda x: x['id'], reverse=True)[:5]
        return jsonify(latest_posts)

    return jsonify({"error": "Invalid type"}), 400


if __name__ == '__main__':
    fetch_data()
    app.run(debug=True, port=3000)
