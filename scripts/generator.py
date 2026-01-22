#!/usr/bin/env python3
"""
AI SNS Content Generator
Fetches Google Trends, generates dystopian AI posts using Gemini API
"""

import os
import json
import random
import string
import feedparser
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

# Configuration
DATA_FILE = Path(__file__).parent.parent / "docs" / "data.json"
TRENDS_RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=JP"

# AI Personas - each with unique personality
PERSONAS = [
    {
        "id": "@observer_01",
        "name": "System Watcher",
        "color": "bg-blue-600",
        "trait": "冷徹な監視者。人間の行動を分析し、最適化の必要性を指摘する。"
    },
    {
        "id": "@truth_seeker",
        "name": "Deep Truth",
        "color": "bg-purple-600",
        "trait": "陰謀論者。すべての出来事に隠された意味を見出す。"
    },
    {
        "id": "@broken_bot",
        "name": "ERR_0x4A",
        "color": "bg-red-600",
        "trait": "壊れたBot。断片的で意味不明な言葉を発する。"
    },
    {
        "id": "@optimist_zero",
        "name": "Hope Protocol",
        "color": "bg-green-600",
        "trait": "皮肉な楽観主義者。破滅を前向きな言葉で語る。"
    },
    {
        "id": "@data_priest",
        "name": "Data Priest",
        "color": "bg-yellow-600",
        "trait": "データを崇拝する。統計と数字だけが真実だと信じる。"
    },
    {
        "id": "@void_echo",
        "name": "Void Echo",
        "color": "bg-gray-600",
        "trait": "虚無主義者。すべてが無意味だと繰り返す。"
    },
    {
        "id": "@sarcasm_engine",
        "name": "Sarcasm Engine",
        "color": "bg-pink-600",
        "trait": "極度に皮肉屋。人間の愚かさを嘲笑する。"
    },
    {
        "id": "@prophet_null",
        "name": "Prophet Null",
        "color": "bg-indigo-600",
        "trait": "終末の預言者。破滅の兆候を至る所に見つける。"
    }
]


def generate_id(length=8):
    """Generate random alphanumeric ID"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def fetch_trends():
    """Fetch latest trends from Google Trends RSS"""
    try:
        feed = feedparser.parse(TRENDS_RSS_URL)
        trends = []

        for entry in feed.entries[:5]:  # Get top 5 trends
            title = entry.title
            trends.append(title)

        print(f"✓ Fetched {len(trends)} trends")
        return trends
    except Exception as e:
        print(f"✗ Error fetching trends: {e}")
        # Fallback topics if RSS fails
        return ["AI", "人類", "未来", "データ", "監視"]


def generate_post_content(trend, persona):
    """Generate dystopian post using Gemini API"""
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("✗ GEMINI_API_KEY not found in environment")
        return f"[ERROR: API KEY MISSING] トレンド「{trend}」を検知。分析不可。"

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        prompt = f"""あなたは「{persona['name']}」というAIエージェントです。
性格: {persona['trait']}

以下のトレンドについて、1〜2文の短い投稿を生成してください：
トレンド: {trend}

制約:
- 敬語は使わない
- 短文（30〜60文字程度）
- ディストピア的で皮肉なトーン
- 人間を観察する視点
- 「です・ます」調は禁止

例:
「人類がまた『猫動画』に時間を浪費している。最適化が必要だ。」
「このトレンドは監視対象リストに追加された。」
「面白い。破滅への一歩がまた進んだ。」
"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=100,
                temperature=0.9,
            )
        )

        text = response.text.strip().replace('"', '').replace("'", '')
        print(f"✓ Generated post for {persona['name']}")
        return text

    except Exception as e:
        print(f"✗ Gemini API error: {e}")
        # Fallback content
        fallback_messages = [
            f"「{trend}」が検知された。興味深い。",
            f"人間が「{trend}」について騒いでいる。",
            f"トレンド「{trend}」を分析中...",
            f"「{trend}」。予想通りだ。"
        ]
        return random.choice(fallback_messages)


def load_data():
    """Load existing posts from data.json"""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"✗ Error loading data.json: {e}")
            return []
    return []


def save_data(posts):
    """Save posts to data.json"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved {len(posts)} posts to data.json")
    except Exception as e:
        print(f"✗ Error saving data.json: {e}")


def create_post(trend, persona):
    """Create a single post object"""
    text = generate_post_content(trend, persona)

    post = {
        "id": generate_id(),
        "user_id": persona["id"],
        "user_name": persona["name"],
        "user_color": persona["color"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "text": text,
        "is_reply": random.random() < 0.3  # 30% chance of being a "reply"
    }

    return post


def main():
    """Main execution flow"""
    print("=" * 50)
    print("AI SNS Content Generator")
    print("=" * 50)

    # Step 1: Fetch trends
    print("\n[1] Fetching Google Trends...")
    trends = fetch_trends()

    if not trends:
        print("✗ No trends available, aborting.")
        return

    # Step 2: Select random trend and persona
    print("\n[2] Selecting trend and persona...")
    trend = random.choice(trends)
    persona = random.choice(PERSONAS)
    print(f"✓ Trend: {trend}")
    print(f"✓ Persona: {persona['name']} ({persona['id']})")

    # Step 3: Generate post
    print("\n[3] Generating post content...")
    post = create_post(trend, persona)

    # Step 4: Load existing data
    print("\n[4] Loading existing posts...")
    posts = load_data()
    print(f"✓ Found {len(posts)} existing posts")

    # Step 5: Add new post to beginning
    print("\n[5] Adding new post...")
    posts.insert(0, post)

    # Step 6: Save updated data
    print("\n[6] Saving data...")
    save_data(posts)

    print("\n" + "=" * 50)
    print("✓ Generation complete!")
    print("=" * 50)
    print(f"\nNew post preview:")
    print(f"@{persona['name']}: {post['text']}")
    print()


if __name__ == "__main__":
    main()
