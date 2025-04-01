import json
import requests
webhook_address = "https://ryu365.webhook.office.com/webhookb2/585cc2b0-ed47-41cd-8bd1-39b5befc07b2@23b65fdf-a4e3-4a19-b03d-12b1d57ad76e/IncomingWebhook/eee629f8a82b4427baf47019708e6b1b/3662ba78-b3f0-47e3-9820-376798dc17d5"
post_json = json.dumps(
    {
        'title': "タイトル",
        'text': "メッセージ"
    }
)
requests.post(webhook_address, post_json)
