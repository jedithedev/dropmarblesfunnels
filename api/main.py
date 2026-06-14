from flask import Flask, request, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed
import json
import os
from datetime import datetime

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515732660230684914/h8cp8cvh0h5XoK-sgAnMihZpySTIbiPl2fcNVRYypAEJd9dS9GnfTfDU_31eMPmnEZuU"
FUNNELS_FILE = "/tmp/funnels.json"


def load_funnels():
    if not os.path.exists(FUNNELS_FILE):
        return []

    with open(FUNNELS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_funnels(data):
    with open(FUNNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@app.route("/funnel", methods=["POST"])
def funnel():
    data = request.json

    step = data.get("step")
    user_id = data.get("user_id")
    username = data.get("username")

    if step is None or user_id is None or username is None:
        return jsonify({"success": False, "error": "missing fields"}), 400

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "step": step,
        "user_id": user_id,
        "username": username
    }

    funnels = load_funnels()
    funnels.append(entry)
    save_funnels(funnels)

    webhook = DiscordWebhook(url=WEBHOOK_URL)

    embed = DiscordEmbed(
        title="Onboarding Funnel Step Completion",
        description=f"Step {step}",
        color="00ff00"
    )

    embed.add_embed_field(name="UserId", value=str(user_id))
    embed.add_embed_field(name="Username", value=username)

    webhook.add_embed(embed)
    webhook.execute()

    return jsonify({"success": True})
