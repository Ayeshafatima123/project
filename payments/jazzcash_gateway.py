"""
JazzCash Payment Gateway Integration
Real payment processing for Pakistan
"""
import requests
import hashlib
import time
from decimal import Decimal


class JazzCashGateway:
    """
    JazzCash Merchant Payment API Integration
    Documentation: https://developer.jazzcash.com.pk/
    """
    
    # SANDBOX (Testing) - Change to PRODUCTION when ready
    SANDBOX_URL = "https://payments.jazzcash.com.pk/api/api/2.0/purchase/complete-payment"
    PRODUCTION_URL = "https://payments.jazzcash.com.pk/api/api/2.0/purchase/complete-payment"
    
    def __init__(self, merchant_id, password, integrity_salt, is_production=False):
        self.merchant_id = merchant_id
        self.password = password
        self.integrity_salt = integrity_salt
        self.base_url = self.PRODUCTION_URL if is_production else self.SANDBOX_URL
        self.is_production = is_production
    
    def _generate_hash(self, data):
        """Generate secure hash for JazzCash API"""
        sorted_data = sorted(data.items())
        hash_string = self.integrity_salt
        for key, value in sorted_data:
            if value:
                hash_string += f"&{value}"
        return hashlib.sha256(hash_string.encode()).hexdigest().upper()
    
    def initiate_payment(self, amount, transaction_id, customer_mobile, customer_name):
        """
        Initiate JazzCash payment
        amount: Decimal amount in PKR
        transaction_id: Unique transaction ID
        customer_mobile: Customer mobile number (03XXXXXXXXX)
        customer_name: Customer name
        """
        amount_in_cents = int(amount * 100)  # Convert to paisa
        
        payload = {
            'pp_Version': '2.0',
            'pp_TxnType': 'MWALLET',
            'pp_Language': 'EN',
            'pp_MerchantID': self.merchant_id,
            'pp_SubMerchantID': self.merchant_id,
            'pp_TxnRefNo': transaction_id,
            'pp_Amount': str(amount_in_cents),
            'pp_TxnCurrency': 'PKR',
            'pp_TxnDateTime': str(int(time.time() * 1000)),
            'pp_BillReference': transaction_id,
            'pp_Description': 'Survey Rewards Withdrawal',
            'pp_CustomerName': customer_name,
            'pp_CustomerMobileNumber': customer_mobile,
            'pp_CustomerEmailAddress': 'customer@example.com',
        }
        
        # Generate secure hash
        payload['pp_SecureHash'] = self._generate_hash(payload)
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=30
            )
            result = response.json()
            
            return {
                'success': result.get('pp_ResponseCode') == '000',
                'message': result.get('pp_ResponseMessage', ''),
                'transaction_id': transaction_id,
                'jazzcash_txn_id': result.get('pp_RetreivalReferenceNo', ''),
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e),
                'transaction_id': transaction_id
            }
    
    def check_transaction_status(self, transaction_id):
        """Check status of a transaction"""
        payload = {
            'pp_Version': '2.0',
            'pp_MerchantID': self.merchant_id,
            'pp_TxnRefNo': transaction_id,
        }
        
        payload['pp_SecureHash'] = self._generate_hash(payload)
        
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=30
            )
            result = response.json()
            
            return {
                'success': result.get('pp_ResponseCode') == '000',
                'status': result.get('pp_ResponseCode'),
                'message': result.get('pp_ResponseMessage', '')
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}


# ============================================================================
# CONFIGURATION - ADD YOUR REAL CREDENTIALS HERE
# ============================================================================

# For TESTING (Sandbox Mode):
JAZZCASH_CONFIG = {
    'merchant_id': 'MC119613',  # Your JazzCash Merchant ID
    'password': '5cg8v9s8jv',  # Your JazzCash Password
    'integrity_salt': '86v8j3tsz4',  # Your JazzCash Integrity Salt
    'is_production': False  # Set to True for REAL payments
}

# For PRODUCTION (Real Money):
# Get credentials from: https://merchant.jazzcash.com.pk/
# JAZZCASH_CONFIG = {
#     'merchant_id': 'YOUR_REAL_MERCHANT_ID',
#     'password': 'YOUR_REAL_PASSWORD',
#     'integrity_salt': 'YOUR_REAL_INTEGRITY_SALT',
#     'is_production': True
# }


def process_jazzcash_withdrawal(withdrawal):
    """
    Process real JazzCash withdrawal
    Call this when admin approves withdrawal
    """
    gateway = JazzCashGateway(**JAZZCASH_CONFIG)
    
    transaction_id = f"JC_{withdrawal.id}_{int(time.time())}"
    
    result = gateway.initiate_payment(
        amount=withdrawal.net_amount,
        transaction_id=transaction_id,
        customer_mobile=withdrawal.account_number,
        customer_name=withdrawal.account_name
    )
    
    if result['success']:
        withdrawal.transaction_id = transaction_id
        withdrawal.status = 'completed'
        withdrawal.save()
        return {
            'success': True,
            'message': f'Real payment of PKR {withdrawal.net_amount} sent to JazzCash account {withdrawal.account_number}',
            'transaction_id': transaction_id
        }
    else:
        return {
            'success': False,
            'message': f'Payment failed: {result["message"]}'
        }
