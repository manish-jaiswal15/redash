import json
from redash import models
from redash.worker import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task(name="redash.tasks.send_execution_results_to_subscribers", time_limit=300, soft_time_limit=240)
def send_execution_results_to_subscribers(query_id):
    logger.info("Checking query %d for active subscriptions", query_id)

    query = models.Query.query.get(query_id)
    last_execution_result = models.QueryResult.get_by_id_and_org(query.latest_query_data_id, query.org)
    logger.info("Sending result - %s over email" %(last_execution_result))

    for subscription in query.subscriptions:
        logger.info("Sending notification !")
        # sending last execution result to user
        
        subscription.notify()
