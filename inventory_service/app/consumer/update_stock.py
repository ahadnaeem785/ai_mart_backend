from aiokafka import AIOKafkaConsumer
import json
from app.deps import get_session
from app.crud.inventory_crud import add_new_inventory_item
from app.models.inventory_model import InventoryItem


async def consume_order_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="update-inventory-stock",
        auto_offset_reset="earliest",
    )

    # Start the consumer.
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW UPDATE STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")

            order_data = json.loads(message.value.decode())
            print("TYPE", (type(order_data)))
            print(f"Order Data {order_data}")

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                updated_stock = update_inventory_stock(session, order_data["product_id"], -order_data["quantity"])
                print(f"Received order placed event: {order_data}")
                
                print("DB_INSERT_STOCK", updated_stock)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()