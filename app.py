import os, logging, requests, re
from slack_sdk.errors import SlackApiError
from slack_bolt import App

logging.basicConfig(level=logging.INFO)
app = App(
    token="SLACK_BOT_TOKEN",
    signing_secret="SLACK_SIGNING_SECRET"
)

channel_id = "C04KMTGGV8X"

##########################################
###########CREATE ORDER CMD###############
##########################################

# Listen to /createorder command events	
@app.command("/createorder")
def handle_command(body, ack, client, logger):
    logger.info(body)
    ack()
    res = client.views_open( 	
        trigger_id=body["trigger_id"],
        view={
    "close": {"type": "plain_text", "text": "Cancel"},
	"title": {
		"type": "plain_text",
		"text": "Bulk Order Creation App"
	},
	"submit": {
		"type": "plain_text",
		"text": "Place Order"
	},
    "callback_id": "create-order-model",
    "close": {"type": "plain_text", "text": "Cancel"},
	"blocks": [
		{
			"type": "input",
            "block_id": "brand",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a Brand"
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "eastpak"
						},
						"value": "eastpak"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "kipling"
						},
						"value": "kipling"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "dickieslife"
						},
						"value": "dickieslife"
					}
				],
				"action_id": "static_select-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Brand"
			}
		},{
			"type": "input",
            "block_id": "environment",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an Environment"
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "dev"
						},
						"value": "dev"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "qa"
						},
						"value": "qa"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "uat"
						},
						"value": "uat"
					}
				],
				"action_id": "static_select-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Environment"
			}
		},
        {   "block_id": "no_of_orders",
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Number of Orders"
			}
		},
        {   "block_id": "product_id",
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Product IDs"
			}
		},		
		{
			"type": "input",
            "block_id": "payment_method",
			"element": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select a Payment Method"
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Credit Card"
						},
						"value": "CreditCard"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "checkmo"
						},
						"value": "checkmo"
					}
				],
				"action_id": "static_select-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Payment Method"
			}
		}
	],
	"type": "modal"
},
    )
    logger.info(res)	
# Listens to events from create-order-model callback-id
@app.view("create-order-model")
def view_submission(ack, body, client, logger):
    ack()

    brand = body["view"]["state"]["values"]["brand"]["static_select-action"]["selected_option"]["value"]
    environment = body["view"]["state"]["values"]["environment"]["static_select-action"]["selected_option"]["value"]
    no_of_orders = body["view"]["state"]["values"]["no_of_orders"]["plain_text_input-action"]["value"]
    product_id = body["view"]["state"]["values"]["product_id"]["plain_text_input-action"]["value"]
    payment_method = body["view"]["state"]["values"]["payment_method"]["static_select-action"]["selected_option"]["value"]
    user = body["user"]["id"] 

    jenkins_job_url = f"https://jenkins_bot:JENKINS_BOT_AUTH@cd.emea.vfc-int.com/job/bulk-order-creation-dev-job/buildWithParameters?token=mytoken123&BRAND={brand}&ENVIRONMENT={environment}&NO_OF_ORDERS={no_of_orders}&PRODUCT_ID={product_id}&PAYMENT_METHOD={payment_method}&SLACK_USER_ID={user}"
    
    r = requests.get(url = jenkins_job_url)
    try:
	    # Call the conversations.list method using the WebClient	
	    result = client.chat_postMessage(
	        channel=channel_id,
	        text=f"Hi <@{user}>! Your Order has been placed. You'll soon be notified about your order ids !"
	    )
	    print(result)
    except SlackApiError as e:
	    print(f"Error: {e}")

if __name__ == "__main__":
    app.start(3000)