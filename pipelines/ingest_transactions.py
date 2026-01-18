"""
Pipeline : Ingestion des transactions DLD
"""
from datetime import date, timedelta
from typing import Optional
from loguru import logger
from core.db import db
from core.models import Transaction
from connectors.transactions import DLDTransactionsConnector


def ingest_transactions(start_date: Optional[date] = None, end_date: Optional[date] = None) -> int:
    """
    Ingérer les transactions DLD dans la base
    
    Returns:
        Nombre de transactions insérées
    """
    connector = DLDTransactionsConnector()
    
    # Récupérer les transactions
    transactions = connector.fetch_transactions(start_date, end_date)
    
    if not transactions:
        logger.info("Aucune transaction à ingérer")
        return 0
    
    # Préparer les données pour batch insert
    columns = [
        "transaction_id", "transaction_date", "transaction_type",
        "community", "project", "building", "unit_number",
        "property_type", "property_subtype", "rooms_count", "rooms_bucket", "area_sqft",
        "price_aed", "price_per_sqft",
        "buyer_name", "seller_name", "is_offplan"
    ]
    
    values = []
    for tx in transactions:
        values.append((
            tx.transaction_id,
            tx.transaction_date,
            tx.transaction_type,
            tx.community,
            tx.project,
            tx.building,
            tx.unit_number,
            tx.property_type,
            tx.property_subtype,
            tx.rooms_count,
            tx.rooms_bucket,
            tx.area_sqft,
            tx.price_aed,
            tx.price_per_sqft,
            tx.buyer_name,
            tx.seller_name,
            tx.is_offplan
        ))
    
    # Insert batch
    db.execute_batch_insert("transactions", columns, values)
    
    logger.info(f"✅ Transactions ingérées : {len(transactions)}")
    return len(transactions)


if __name__ == "__main__":
    # Test standalone
    from core.utils import setup_logging
    setup_logging()
    
    # Ingérer les dernières 24h
    count = ingest_transactions(
        start_date=date.today() - timedelta(days=1),
        end_date=date.today()
    )
    print(f"Transactions ingérées : {count}")
