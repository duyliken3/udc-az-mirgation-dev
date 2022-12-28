import azure.functions as func
import logging
import os
from datetime import datetime
import psycopg2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)
 
    # Done: Get connection to database
    connection = psycopg2.connect(dbname="techconfdb", user="az_admin@az-postgre-mi-udc-dc", password="th3_flatw0rld", host="az-postgre-mi-udc-dc.postgres.database.azure.com")
    cursor = connection.cursor()
    try:
        notification_query = cursor.execute(f"SELECT message, subject FROM notification WHERE id = {notification_id};")

        cursor.execute("SELECT first_name, last_name, email FROM attendee;")
        attendees = cursor.fetchall()

        for attendee in attendees:
            Mail('{}, {}, {}'.format({'duyliken2@gmail.com'}, {attendee[2]}, {notification_query}))

        notification_completed_date = datetime.utcnow()

        notification_status = 'Notified {} attendees'.format(len(attendees))
        
        _ = cursor.execute(f"UPDATE notification SET status = '{notification_status}', completed_date = '{notification_completed_date}' WHERE id = {notification_id};")        

        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
