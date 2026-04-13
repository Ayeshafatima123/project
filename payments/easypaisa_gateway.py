"""
EasyPaisa Payment Gateway Integration
Supports both payment collection and disbursement (payouts)

Configuration is loaded from Django settings (EASYPAISA_CONFIG).
"""
import requests
import hashlib
import time
import logging
from decimal import Decimal
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

# Load configuration from Django settings
_config = getattr(settings, 'EASYPAISA_CONFIG', {})
DEFAULT_STORE_ID = _config.get('store_id', '')
DEFAULT_PASSWORD = _config.get('password', '')
DEFAULT_IS_PRODUCTION = _config.get('is_production', False)


class EasyPaisaGateway:
    """
    EasyPaisa Merchant API Integration
    
    Collection API: Customers pay you
    Disbursement API: You send money to EasyPaisa accounts
    
    Documentation: https://developer.easypaisa.com.pk
    Registration: https://www.easypaisa.com.pk/merchant
    """

    # Collection (Payment IN) URLs
    COLLECTION_SANDBOX = "https://easypaystg.easypaisa.com.pk/easypay/Index.jsf"
    COLLECTION_PRODUCTION = "https://easypay.easypaisa.com.pk/easypay/Index.jsf"

    # Disbursement (Payout OUT) URLs
    DISBURSEMENT_SANDBOX = "https://easypaystg.easypaisa.com.pk/easypay-disbursement/api/v1/payout"
    DISBURSEMENT_PRODUCTION = "https://easypay.easypaisa.com.pk/easypay-disbursement/api/v1/payout"

    # Status Check URL
    STATUS_SANDBOX = "https://easypaystg.easypaisa.com.pk/easypay/Order.jsf"
    STATUS_PRODUCTION = "https://easypay.easypaisa.com.pk/easypay/Order.jsf"

    def __init__(self, store_id=None, password=None, is_production=None):
        self.store_id = store_id or DEFAULT_STORE_ID
        self.password = password or DEFAULT_PASSWORD
        self.is_production = is_production if is_production is not None else DEFAULT_IS_PRODUCTION
        
        if not self.store_id or not self.password:
            logger.warning("EasyPaisa credentials not configured. Using demo mode.")

    def _get_base_url(self, api_type='collection'):
        if api_type == 'disbursement':
            return self.DISBURSEMENT_PRODUCTION if self.is_production else self.DISBURSEMENT_SANDBOX
        elif api_type == 'status':
            return self.STATUS_PRODUCTION if self.is_production else self.STATUS_SANDBOX
        return self.COLLECTION_PRODUCTION if self.is_production else self.COLLECTION_SANDBOX

    def initiate_collection(self, amount, order_id, customer_mobile, customer_name, post_back_url=None):
        """
        Initiate EasyPaisa payment (Customer pays you)
        """
        if not self.store_id or not self.password:
            return {
                'success': False,
                'message': 'EasyPaisa credentials not configured. Contact admin.'
            }

        amount_in_cents = int(amount * 100)
        post_back = post_back_url or 'https://yourdomain.com/payments/easypaisa/callback/'

        payload = {
            'storeId': self.store_id,
            'amount': str(amount_in_cents),
            'postBackURL': post_back,
            'orderRefNum': order_id,
            'merchantHash': self._generate_collection_hash(order_id, amount_in_cents),
        }

        try:
            response = requests.post(
                self._get_base_url('collection'),
                data=payload,
                timeout=30
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Payment initiated',
                    'order_id': order_id,
                    'redirect_url': response.url,
                    'form_html': response.text,
                    'is_demo': False
                }
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}'
                }
        except Exception as e:
            logger.error(f"EasyPaisa collection error: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    def process_disbursement(self, amount, account_number, account_name, request_id=None):
        """
        Send money to EasyPaisa account (Payout/Disbursement)
        
        This requires EasyPaisa Disbursement API access.
        For now, returns demo response if credentials not configured.
        """
        if not self.is_configured():
            # DEMO MODE: Simulate successful payout
            logger.info(f"[DEMO MODE] EasyPaisa payout of {amount} to {account_number}")
            return {
                'success': True,
                'message': f'[DEMO] Payout of PKR {amount} initiated to EasyPaisa {account_number}',
                'transaction_id': f"EP_DEMO_{int(time.time())}",
                'status': 'processing',
                'is_demo': True
            }

        request_id = request_id or f"EP_REQ_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
        amount_in_cents = int(amount * 100)

        payload = {
            'storeId': self.store_id,
            'requestId': request_id,
            'accountNumber': account_number,
            'accountName': account_name,
            'amount': str(amount_in_cents),
            'currency': 'PKR',
            'description': f'Withdrawal payout on {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'merchantHash': self._generate_disbursement_hash(request_id, amount_in_cents, account_number),
        }

        try:
            response = requests.post(
                self._get_base_url('disbursement'),
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                timeout=30
            )

            data = response.json() if response.content else {}

            if response.status_code in (200, 201):
                return {
                    'success': True,
                    'message': data.get('message', 'Disbursement initiated'),
                    'transaction_id': data.get('transactionId', request_id),
                    'status': data.get('status', 'processing'),
                    'is_demo': False
                }
            else:
                return {
                    'success': False,
                    'message': data.get('message', f'HTTP {response.status_code}'),
                    'is_demo': False
                }
        except Exception as e:
            logger.error(f"EasyPaisa disbursement error: {e}")
            return {
                'success': False,
                'message': str(e),
                'is_demo': False
            }

    def check_transaction_status(self, order_id):
        """Check status of a transaction"""
        if not self.store_id or not self.password:
            return {'status': 'unknown', 'is_demo': True}

        try:
            response = requests.get(
                self._get_base_url('status'),
                params={'orderRefNum': order_id},
                timeout=30
            )

            if response.status_code == 200:
                return {
                    'status': 'completed' if 'success' in response.text.lower() else 'pending',
                    'response': response.text,
                    'is_demo': False
                }
            return {'status': 'error', 'is_demo': False}
        except Exception as e:
            logger.error(f"EasyPaisa status check error: {e}")
            return {'status': 'error', 'message': str(e), 'is_demo': False}

    def _generate_collection_hash(self, order_id, amount):
        """Generate EasyPaisa collection hash"""
        hash_string = f"{self.store_id}:{order_id}:{amount}:{self.password}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def _generate_disbursement_hash(self, request_id, amount, account_number):
        """Generate EasyPaisa disbursement hash"""
        hash_string = f"{self.store_id}:{request_id}:{amount}:{account_number}:{self.password}"
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def is_configured(self):
        """Check if gateway is properly configured"""
        return bool(self.store_id and self.password and 
                   self.store_id != 'YOUR_EASYPAISA_STORE_ID' and 
                   self.password != 'YOUR_EASYPAISA_PASSWORD' and
                   self.store_id != DEFAULT_STORE_ID and
                   self.password != DEFAULT_PASSWORD)


# ============================================================================
# Convenience function for processing withdrawals
# ============================================================================

def process_easypaisa_withdrawal(withdrawal):
    """
    Process EasyPaisa withdrawal (payout/disbursement)
    
    If credentials are configured, calls the real API.
    Otherwise, runs in demo mode (simulates successful payout).
    """
    gateway = EasyPaisaGateway()
    is_configured = gateway.is_configured()
    
    request_id = f"EP_{withdrawal.id}_{int(time.time())}"
    
    result = gateway.process_disbursement(
        amount=withdrawal.net_amount,
        account_number=withdrawal.account_number,
        account_name=withdrawal.account_name,
        request_id=request_id,
    )
    
    if result['success']:
        withdrawal.transaction_id = result.get('transaction_id', request_id)
        if not is_configured:
            # Demo mode: mark as processing (admin needs to send manually)
            withdrawal.status = 'processing'
        else:
            # Real API: use the status returned by API
            withdrawal.status = result.get('status', 'processing')
        withdrawal.save()
        
        mode_label = "[DEMO] " if result.get('is_demo') else ""
        return {
            'success': True,
            'message': f'{mode_label}Payout of PKR {withdrawal.net_amount} initiated to EasyPaisa {withdrawal.account_number}',
            'transaction_id': result.get('transaction_id'),
            'is_demo': result.get('is_demo', False),
        }
    else:
        return {
            'success': False,
            'message': f'EasyPaisa payout failed: {result["message"]}',
            'is_demo': False,
        }
