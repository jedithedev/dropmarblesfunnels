from flask import Flask, request, jsonify
from discord_webhook import DiscordWebhook, DiscordEmbed
from supabase import create_client
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1515732660230684914/h8cp8cvh0h5XoK-sgAnMihZpySTIbiPl2fcNVRYypAEJd9dS9GnfTfDU_31eMPmnEZuU"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/funnel", methods=["POST"])
def funnel():
    data = request.json

    step = data.get("step")
    user_id = data.get("user_id")
    username = data.get("username")

    if step is None or user_id is None or username is None:
        return jsonify({"success": False, "error": "missing fields"}), 400

    supabase.table("funnels").insert({
        "step": step,
        "user_id": user_id,
        "username": username
    }).execute()

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


if __name__ == "__main__":
    app.run()
