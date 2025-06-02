from uuid import UUID

from loguru import logger
from sqlmodel import col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.database.models.transactions.model import (
    TransactionBase,
    TransactionReadResponse,
    TransactionTable,
)
from langflow.services.deps import get_settings_service


async def get_transactions_by_flow_id(
    db: AsyncSession, flow_id: UUID, limit: int | None = 1000
) -> list[TransactionTable]:
    stmt = (
        select(TransactionTable)
        .where(TransactionTable.flow_id == flow_id)
        .order_by(col(TransactionTable.timestamp))
        .limit(limit)
    )

    transactions = await db.exec(stmt)
    return list(transactions)


async def log_transaction(db: AsyncSession, transaction: TransactionBase) -> TransactionTable | None:
    """Log a transaction and maintain a maximum number of transactions in the database.

    This function logs a new transaction into the database and ensures that the number of transactions
    does not exceed the maximum limit specified in the settings. If the number of transactions exceeds
    the limit, the oldest transactions are deleted to maintain the limit.

    Args:
        db: Database session
        transaction: Transaction data to log

    Returns:
        The created TransactionTable entry

    Raises:
        IntegrityError: If there is a database integrity error
    """
    if not transaction.flow_id:
        logger.debug("Transaction flow_id is None")
        return None
    table = TransactionTable(**transaction.model_dump())

    try:
        # Get max entries setting
        max_entries = get_settings_service().settings.max_transactions_to_keep

        # Add new entry first
        db.add(table)
        
        # Get IDs of transactions to keep (newest max_entries including the one we just added)
        keep_ids_stmt = (
            select(TransactionTable.id)
            .where(TransactionTable.flow_id == transaction.flow_id)
            .order_by(col(TransactionTable.timestamp).desc())
            .limit(max_entries)
        )
        keep_ids_result = await db.exec(keep_ids_stmt)
        keep_ids = [row for row in keep_ids_result]
        
        if len(keep_ids) >= max_entries:
            # Delete transactions that are not in the keep_ids list
            delete_older = delete(TransactionTable).where(
                TransactionTable.flow_id == transaction.flow_id,
                ~col(TransactionTable.id).in_(keep_ids)
            )
            await db.exec(delete_older)
        
        await db.commit()
        
        logger.debug(f"Logged transaction for flow {transaction.flow_id} and maintained limit of {max_entries}")


    except Exception:
        await db.rollback()
        raise
    return table


def transform_transaction_table(
    transaction: list[TransactionTable] | TransactionTable,
) -> list[TransactionReadResponse]:
    if isinstance(transaction, list):
        return [TransactionReadResponse.model_validate(t, from_attributes=True) for t in transaction]
    return TransactionReadResponse.model_validate(transaction, from_attributes=True)
