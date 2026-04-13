"""
PayPal Payment Gateway Integration
Real international payments
"""
import requests
import base64
from decimal import Decimal


class PayPalGateway:
    """
    PayPal Payouts API Integration
    Documentation: https://developer.paypal.com/docs/payouts/
    """
    
    # SANDBOX (Testing)
    SANDBOX_API = "https://api-m.sandbox.paypal.com"
    # PRODUCTION (Real Money)
    PRODUCTION_API = "https://api-m.paypal.com"
    
    def __init__(self, client_id, client_secret, is_production=False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = self.PRODUCTION_API if is_production else self.SANDBOX_API
        self.is_production = is_production
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Get OAuth2 access token from PayPal"""
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            data={'grant_type': 'client_credentials'},
            headers={
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
        else:
            raise Exception(f"PayPal auth failed: {response.text}")
    
    def send_payout(self, amount, recipient_email, note="Survey Rewards Payment"):
        """
        Send real PayPal payout
        amount: Decimal amount in USD
        recipient_email: PayPal email of recipient
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'PayPal-Request-Id': f'survey_{int(time.time())}'
        }
        
        payload = {
            'sender_batch_header': {
                'sender_batch_id': f'batch_{int(time.time())}',
                'email_subject': 'You received a payment from SurveyRewards!',
                'recipient_type': 'EMAIL'
            },
            'items': [
                {
                    'recipient_type': 'EMAIL',
                    'amount': {
                        'value': str(amount),
                        'currency': 'USD'
                    },
                    'receiver': recipient_email,
                    'note': note,
                    'sender_item_id': f'item_{int(time.time())}'
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/payments/payouts",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            return {
                'success': response.status_code in [200, 201, 202],
                'message': result.get('batch_header', {}).get('batch_status', ''),
                'payout_batch_id': result.get('batch_header', {}).get('payout_batch_id', ''),
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }


# ============================================================================
# CONFIGURATION - ADD YOUR REAL CREDENTIALS HERE
# ============================================================================

# Get credentials from: https://developer.paypal.com/
PAYPAL_CONFIG = {
    'client_id': 'YOUR_PAYPAL_CLIENT_ID',
    'client_secret': 'YOUR_PAYPAL_CLIENT_SECRET',
    'is_production': False  # Set to True for REAL payments
}


def process_paypal_withdrawal(withdrawal):
    """
    Process real PayPal withdrawal
    """
    try:
        gateway = PayPalGateway(**PAYPAL_CONFIG)
        
        result = gateway.send_payout(
            amount=withdrawal.net_amount,
            recipient_email=withdrawal.account_number,  # PayPal email
            note=f"Survey Rewards Payment - {withdrawal.user.email}"
        )
        
        if result['success']:
            withdrawal.transaction_id = result.get('payout_batch_id')
            withdrawal.status = 'completed'
            withdrawal.save()
            return {
                'success': True,
                'message': f'Real payment of ${withdrawal.net_amount} sent to PayPal account {withdrawal.account_number}',
                'transaction_id': result.get('payout_batch_id')
            }
        else:
            return {
                'success': False,
                'message': f'PayPal payment failed: {result["message"]}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'PayPal error: {str(e)}'
        }
