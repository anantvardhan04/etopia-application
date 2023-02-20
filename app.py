import os, logging, requests, re
import mysql.connector
from slack_sdk.errors import SlackApiError
from slack_bolt import App

logging.basicConfig(level=logging.INFO)
app = App(
    token="SLACK_BOT_TOKEN",
    signing_secret="SLACK_SIGNING_SECRET"
)

channel_id = "C04QFLU974Z"

# Listen to /post command events	
@app.command("/post")
def handle_command(body, ack, client, logger):
    logger.info(body)
    ack()
    res = client.views_open( 	
        trigger_id=body["trigger_id"],
        view={
    "close": {"type": "plain_text", "text": "Cancel"},
	"title": {
		"type": "plain_text",
		"text": "Fonetwish Application"
	},
	"submit": {
		"type": "plain_text",
		"text": "Post Message"
	},
    "callback_id": "post-message",
	"blocks": [
        {   
			"block_id": "user",
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "User"
			}
		},
        {   "block_id": "message",
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Message"
			}
		}
	],
	"type": "modal"
     },
    )

# Listen to /get command events	
@app.command("/get")
def handle_command(body, ack, client, logger):
    logger.info(body)
    ack()
    res = client.views_open( 	
        trigger_id=body["trigger_id"],
        view={
    "close": {"type": "plain_text", "text": "Cancel"},
	"title": {
		"type": "plain_text",
		"text": "Fonetwish Application"
	},
	"submit": {
		"type": "plain_text",
		"text": "Get Updates"
	},
    "callback_id": "get-message",
	"blocks": [
        {   
			"block_id": "user",
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "User"
			}
		}
	],
	"type": "modal"
     },
    )

# Listens to events from post-message callback-id
@app.view("post-message")
def view_submission(ack, body, client, logger):
    ack()
    user_name = body["view"]["state"]["values"]["user"]["plain_text_input-action"]["value"]
    message =  body["view"]["state"]["values"]["message"]["plain_text_input-action"]["value"]
    try:
	    conn = mysql.connector.connect(
            host="etopia-dev-cluster.cluster-c0zdw8u2xc3b.us-east-1.rds.amazonaws.com",
            user="admin",
            password="ETOPIA_DB_PASSWORD",
            database="etopia_master"
          )
            # Create a cursor
        cur = conn.cursor()
        cur.execute("SET @user_name = %s", (user_name,))
        cur.execute("SET @message = %s", (message,))
        cur.execute("SELECT COUNT(*) INTO @user_count FROM user_table WHERE user_name = @user_name")
        cur.execute("SELECT @user_count")
        user_count = cur.fetchone()[0]
        if user_count == 0:
            cur.execute("INSERT INTO user_table (user_name) VALUES (@user_name)")
        cur.execute("INSERT INTO message_table (user_name, message) VALUES (@user_name, @message)")
        conn.commit()
        result = client.chat_postMessage(
                channel=channel_id,
                text=f"Hi {user_name}! Your message '{message}' has been posted."
            )
    except SlackApiError as e:
            print(f"Error: {e}")

# Listens to events from post-message callback-id
@app.view("get-message")
def view_submission(ack, body, client, logger):
    ack()
    user_name = body["view"]["state"]["values"]["user"]["plain_text_input-action"]["value"]
    try:
	    conn = mysql.connector.connect(
            host="etopia-dev-cluster.cluster-c0zdw8u2xc3b.us-east-1.rds.amazonaws.com",
            user="admin",
            password="ETOPIA_DB_PASSWORD",
            database="etopia_master"
        )
        cur = conn.cursor()
        # Fetch the messages
        cur.execute("SELECT message FROM message_table WHERE user_name = %s ORDER BY id DESC LIMIT 3", (user_name,))
        messages = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        result = client.chat_postMessage(
              channel=channel_id,
              text='\n'.join([f'Message {i+1}: {message}' for i, message in enumerate(messages)])
          )
    except SlackApiError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    app.start(3000)