"""
Pipeline : Ingestion des hypothèques DLD
"""
from datetime import date, timedelta
from typing import Optional
from loguru import logger
from core.db import db
from connectors.dld_mortgages import DLDMortgagesConnector


def ingest_mortgages(start_date: Optional[date] = None, end_date: Optional[date] = None) -> int:
    """Ingérer les hypothèques DLD"""
    connector = DLDMortgagesConnector()
    mortgages = connector.fetch_mortgages(start_date, end_date)
    
    if not mortgages:
        logger.info("Aucune hypothèque à ingérer")
        return 0
    
    columns = [
        "mortgage_id", "mortgage_date",
        "community", "project", "building",
        "mortgage_amount_aed", "lender", "borrower"
    ]
    
    values = []
    for m in mortgages:
        values.append((
            m.mortgage_id,
            m.mortgage_date,
            m.community,
            m.project,
            m.building,
            m.mortgage_amount_aed,
            m.lender,
            m.borrower
        ))
    
    db.execute_batch_insert("mortgages", columns, values)
    
    logger.info(f"✅ Hypothèques ingérées : {len(mortgages)}")
    return len(mortgages)


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    count = ingest_mortgages(
        start_date=date.today() - timedelta(days=1),
        end_date=date.today()
    )
    print(f"Hypothèques ingérées : {count}")
