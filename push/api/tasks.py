from celery import task
from push import settings
from apnsclient import *

# Persistent connection for intensive messaging.
# Keep reference to session instance in some class static/global variable,
# otherwise it will be garbage collected and all connections will be closed.
session = Session()

@task(ignore_result=True)
def apns_push(tokens=None, message=''):
    con = session.get_connection("push_sandbox", cert_file=settings.APNS_DEV_CERT_PATH)

    if tokens is None or len(tokens) == 0:
        return None
    print 'pushing to : ' + str(tokens)
    # New message to 3 devices. You app will show badge 10 over app's icon.
    message = Message(tokens, alert=message, badge=1)

    # Send the message.
    srv = APNs(con)
    res = srv.send(message)

    # Check failures. Check codes in APNs reference docs.
    for token, reason in res.failed.items():
        code, errmsg = reason
        print "Device failed: {0}, reason: {1}".format(token, errmsg)

    # Check failures not related to devices.
    for code, errmsg in res.errors:
        print "Error: ", errmsg

    # Check if there are tokens that can be retried
    if res.needs_retry():
        # repeat with retry_message or reschedule your task
        retry_message = res.retry()
