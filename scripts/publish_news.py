#!/usr/bin/env python3
"""
ナルエビが毎朝AIニュースをnull-senseiサイトに自動公開するスクリプト
使い方: python3 publish_news.py --title "タイトル" --body "本文HTML" --excerpt "抜粋"
"""
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
import subprocess

REPO_DIR = Path(__file__).parent.parent
NEWS_DIR = REPO_DIR / "news"
JST_NOW = datetime.now()

def slugify(date_str):
    return date_str.replace("-", "")

def publish_news(title, body_html, excerpt, sources=""):
    date_str = JST_NOW.strftime("%Y-%m-%d")
    slug = slugify(date_str)
    post_dir = NEWS_DIR / slug
    post_dir.mkdir(parents=True, exist_ok=True)

    # 記事HTML生成
    article_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Null-sensei</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <header>
    <a href="/" class="logo">Null-sensei</a>
    <nav>
      <a href="/news/">News</a>
      <a href="/blog/">Blog</a>
    </nav>
  </header>

  <div class="container">
    <h1 class="article-title">{title}</h1>
    <div class="article-date">{date_str} — by ナルエビ🦐</div>
    <div class="article-body">
{body_html}
    </div>
    <a href="/news/" class="back-link">← News一覧へ</a>
  </div>

  <footer>
    <p>by <a href="https://x.com/GOROman" target="_blank">@GOROman</a> &amp; <a href="https://x.com/naruevi" target="_blank">ナルエビ🦐</a></p>
  </footer>
</body>
</html>"""

    (post_dir / "index.html").write_text(article_html, encoding="utf-8")

    # index.json更新
    index_file = NEWS_DIR / "index.json"
    posts = []
    if index_file.exists():
        posts = json.loads(index_file.read_text(encoding="utf-8"))

    # 同じ日付があれば更新、なければ先頭に追加
    existing = next((p for p in posts if p["slug"] == slug), None)
    if existing:
        existing["title"] = title
        existing["excerpt"] = excerpt
    else:
        posts.insert(0, {
            "date": date_str,
            "slug": slug,
            "title": title,
            "excerpt": excerpt
        })

    index_file.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 記事を生成しました: /news/{slug}/")
    return slug

def git_push(message):
    os.chdir(REPO_DIR)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ GitHubにpushしました")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--excerpt", required=True)
    parser.add_argument("--push", action="store_true", default=True)
    args = parser.parse_args()

    slug = publish_news(args.title, args.body, args.excerpt)

    if args.push:
        date_str = JST_NOW.strftime("%Y-%m-%d")
        git_push(f"news: {date_str} AIニュース自動更新")
