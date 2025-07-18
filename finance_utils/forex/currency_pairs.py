"""
Currency Pairs Configuration

This module defines all supported currency pairs and their metadata.
"""

# Major Currency Pairs - Most liquid and widely traded
MAJOR_PAIRS = {
    'EUR/USD': {
        'name': 'Euro/US Dollar',
        'category': 'major',
        'pip_value': 0.0001,
        'typical_spread': 1.5,
        'session_overlap': ['London', 'New York'],
        'description': 'The most traded currency pair in the world'
    },
    'GBP/USD': {
        'name': 'British Pound/US Dollar',
        'category': 'major',
        'pip_value': 0.0001,
        'typical_spread': 2.0,
        'session_overlap': ['London', 'New York'],
        'description': 'Known as "Cable" in forex markets'
    },
    'USD/JPY': {
        'name': 'US Dollar/Japanese Yen',
        'category': 'major',
        'pip_value': 0.01,
        'typical_spread': 1.8,
        'session_overlap': ['Tokyo', 'New York'],
        'description': 'Popular pair for carry trades'
    },
    'USD/CHF': {
        'name': 'US Dollar/Swiss Franc',
        'category': 'major',
        'pip_value': 0.0001,
        'typical_spread': 2.5,
        'session_overlap': ['London', 'New York'],
        'description': 'Safe haven currency pair'
    },
    'AUD/USD': {
        'name': 'Australian Dollar/US Dollar',
        'category': 'major',
        'pip_value': 0.0001,
        'typical_spread': 2.0,
        'session_overlap': ['Sydney', 'New York'],
        'description': 'Commodity currency sensitive to gold prices'
    },
    'USD/CAD': {
        'name': 'US Dollar/Canadian Dollar',
        'category': 'major',
        'pip_value': 0.0001,
        'typical_spread': 2.5,
        'session_overlap': ['New York', 'London'],
        'description': 'Influenced by oil prices and interest rate differentials'
    },
    'NZD/USD': {
        'name': 'New Zealand Dollar/US Dollar',
        'category': 'major',
        'pip_value': 0.0001,
        'typical_spread': 3.0,
        'session_overlap': ['Sydney', 'New York'],
        'description': 'Commodity currency with high volatility'
    }
}

# Minor Currency Pairs - Cross-currency pairs (no USD)
MINOR_PAIRS = {
    'EUR/GBP': {
        'name': 'Euro/British Pound',
        'category': 'minor',
        'pip_value': 0.0001,
        'typical_spread': 2.5,
        'session_overlap': ['London'],
        'description': 'Popular European cross pair'
    },
    'EUR/JPY': {
        'name': 'Euro/Japanese Yen',
        'category': 'minor',
        'pip_value': 0.01,
        'typical_spread': 2.0,
        'session_overlap': ['Tokyo', 'London'],
        'description': 'Volatile cross pair popular with trend traders'
    },
    'GBP/JPY': {
        'name': 'British Pound/Japanese Yen',
        'category': 'minor',
        'pip_value': 0.01,
        'typical_spread': 3.0,
        'session_overlap': ['Tokyo', 'London'],
        'description': 'Known as "Dragon" - highly volatile'
    },
    'EUR/CHF': {
        'name': 'Euro/Swiss Franc',
        'category': 'minor',
        'pip_value': 0.0001,
        'typical_spread': 2.8,
        'session_overlap': ['London'],
        'description': 'Range-bound pair with occasional breakouts'
    },
    'GBP/CHF': {
        'name': 'British Pound/Swiss Franc',
        'category': 'minor',
        'pip_value': 0.0001,
        'typical_spread': 3.5,
        'session_overlap': ['London'],
        'description': 'Less liquid but offers good trading opportunities'
    },
    'AUD/JPY': {
        'name': 'Australian Dollar/Japanese Yen',
        'category': 'minor',
        'pip_value': 0.01,
        'typical_spread': 2.5,
        'session_overlap': ['Tokyo', 'Sydney'],
        'description': 'Risk-on/risk-off sentiment indicator'
    }
}

# Exotic Currency Pairs - Emerging market currencies
EXOTIC_PAIRS = {
    'USD/TRY': {
        'name': 'US Dollar/Turkish Lira',
        'category': 'exotic',
        'pip_value': 0.0001,
        'typical_spread': 15.0,
        'session_overlap': ['London'],
        'description': 'High volatility emerging market currency'
    },
    'EUR/TRY': {
        'name': 'Euro/Turkish Lira',
        'category': 'exotic',
        'pip_value': 0.0001,
        'typical_spread': 20.0,
        'session_overlap': ['London'],
        'description': 'Volatile emerging market cross pair'
    },
    'USD/ZAR': {
        'name': 'US Dollar/South African Rand',
        'category': 'exotic',
        'pip_value': 0.0001,
        'typical_spread': 12.0,
        'session_overlap': ['London'],
        'description': 'Commodity currency influenced by gold mining'
    },
    'USD/MXN': {
        'name': 'US Dollar/Mexican Peso',
        'category': 'exotic',
        'pip_value': 0.0001,
        'typical_spread': 8.0,
        'session_overlap': ['New York'],
        'description': 'North American emerging market currency'
    }
}

# Trading Sessions
TRADING_SESSIONS = {
    'Sydney': {
        'start': '21:00',
        'end': '06:00',
        'timezone': 'UTC',
        'peak_hours': ['22:00', '02:00'],
        'active_pairs': ['AUD/USD', 'NZD/USD', 'AUD/JPY']
    },
    'Tokyo': {
        'start': '00:00',
        'end': '09:00',
        'timezone': 'UTC',
        'peak_hours': ['01:00', '04:00'],
        'active_pairs': ['USD/JPY', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY']
    },
    'London': {
        'start': '08:00',
        'end': '17:00',
        'timezone': 'UTC',
        'peak_hours': ['09:00', '12:00'],
        'active_pairs': ['EUR/USD', 'GBP/USD', 'USD/CHF', 'EUR/GBP']
    },
    'New York': {
        'start': '13:00',
        'end': '22:00',
        'timezone': 'UTC',
        'peak_hours': ['14:00', '18:00'],
        'active_pairs': ['EUR/USD', 'GBP/USD', 'USD/CAD', 'AUD/USD']
    }
}

# Economic Indicators that affect currency pairs
ECONOMIC_INDICATORS = {
    'USD': [
        'Non-Farm Payrolls',
        'Federal Reserve Interest Rate Decision',
        'Consumer Price Index',
        'Gross Domestic Product',
        'Unemployment Rate',
        'Producer Price Index'
    ],
    'EUR': [
        'European Central Bank Interest Rate Decision',
        'Consumer Price Index',
        'Gross Domestic Product',
        'Unemployment Rate',
        'Manufacturing PMI',
        'Services PMI'
    ],
    'GBP': [
        'Bank of England Interest Rate Decision',
        'Consumer Price Index',
        'Gross Domestic Product',
        'Unemployment Rate',
        'Manufacturing PMI',
        'Brexit-related news'
    ],
    'JPY': [
        'Bank of Japan Interest Rate Decision',
        'Consumer Price Index',
        'Gross Domestic Product',
        'Unemployment Rate',
        'Tankan Business Survey',
        'Trade Balance'
    ]
}

# Currency strength factors
CURRENCY_STRENGTH_FACTORS = {
    'USD': {
        'economic_strength': 0.3,
        'political_stability': 0.2,
        'interest_rates': 0.25,
        'inflation': 0.15,
        'trade_balance': 0.1
    },
    'EUR': {
        'economic_strength': 0.25,
        'political_stability': 0.2,
        'interest_rates': 0.25,
        'inflation': 0.15,
        'trade_balance': 0.15
    },
    'GBP': {
        'economic_strength': 0.25,
        'political_stability': 0.15,
        'interest_rates': 0.25,
        'inflation': 0.15,
        'trade_balance': 0.2
    },
    'JPY': {
        'economic_strength': 0.3,
        'political_stability': 0.25,
        'interest_rates': 0.2,
        'inflation': 0.15,
        'trade_balance': 0.1
    }
}

def get_all_pairs():
    """Get all currency pairs combined"""
    all_pairs = {}
    all_pairs.update(MAJOR_PAIRS)
    all_pairs.update(MINOR_PAIRS)
    all_pairs.update(EXOTIC_PAIRS)
    return all_pairs

def get_pairs_by_category(category):
    """Get currency pairs by category"""
    if category == 'major':
        return MAJOR_PAIRS
    elif category == 'minor':
        return MINOR_PAIRS
    elif category == 'exotic':
        return EXOTIC_PAIRS
    else:
        return {}

def get_pair_info(pair_symbol):
    """Get information about a specific currency pair"""
    all_pairs = get_all_pairs()
    return all_pairs.get(pair_symbol, None)

def is_market_open(session_name):
    """Check if a trading session is currently open"""
    from datetime import datetime, timezone
    
    if session_name not in TRADING_SESSIONS:
        return False
    
    session = TRADING_SESSIONS[session_name]
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    
    start_hour = int(session['start'].split(':')[0])
    end_hour = int(session['end'].split(':')[0])
    
    if start_hour <= end_hour:
        return start_hour <= current_hour < end_hour
    else:  # Session crosses midnight
        return current_hour >= start_hour or current_hour < end_hour

def get_active_sessions():
    """Get all currently active trading sessions"""
    active_sessions = []
    for session_name in TRADING_SESSIONS:
        if is_market_open(session_name):
            active_sessions.append(session_name)
    return active_sessions

def get_most_active_pairs():
    """Get the most active currency pairs based on current trading sessions"""
    active_sessions = get_active_sessions()
    active_pairs = set()
    
    for session in active_sessions:
        session_pairs = TRADING_SESSIONS[session].get('active_pairs', [])
        active_pairs.update(session_pairs)
    
    return list(active_pairs)
