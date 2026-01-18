"""
Alias pour compatibilité avec les imports existants
Le vrai connecteur est dans dld_transactions.py
"""
from connectors.dld_transactions import DLDTransactionsConnector

__all__ = ['DLDTransactionsConnector']
