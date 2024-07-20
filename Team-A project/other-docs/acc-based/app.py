from flask import Flask, request, render_template, jsonify
import paypalrestsdk
import json
import logging
import uuid

app = Flask(__name__)

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Use "live" for production
    "client_id": "YOUR_SANDBOX_CLIENT_ID",
    "client_secret": "YOUR_SANDBOX_CLIENT_SECRET"
})

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_payout', methods=['POST'])
def create_payout():
    recipient_email = request.form['email']
    amount_value = request.form['amount']

    # Generate a unique sender batch ID
    sender_batch_id = str(uuid.uuid4())

    # Create a payout
    payout = paypalrestsdk.Payout({
        "sender_batch_header": {
            "sender_batch_id": sender_batch_id,
            "email_subject": "You have a payout!"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": amount_value,
                    "currency": "USD"
                },
                "note": "Payment",
                "sender_item_id": "item_1",
                "receiver": recipient_email
            }
        ]
    })

    try:
        # Execute the payout in asynchronous mode
        if payout.create(sync_mode=False):
            return jsonify({
                "status": "success",
                "payout_batch_id": payout.batch_header.payout_batch_id,
                "details": payout.to_dict()
            })
        else:
            logging.debug(f"Payout creation failed: {json.dumps(payout.error, indent=2)}")
            error_message = payout.error.get('message', 'Unknown error')
            return jsonify({
                "status": "failure",
                "error": error_message
            })
    except paypalrestsdk.exceptions.ResourceInvalid as error:
        logging.debug(f"ResourceInvalid exception: {error}")
        error_message = error.message if hasattr(error, 'message') else str(error)
        return jsonify({
            "status": "failure",
            "error": error_message
        })
    except Exception as e:
        logging.debug(f"Exception: {e}")
        return jsonify({
            "status": "failure",
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
