from threading import Thread
import collector


def on_server_loaded(server_context):
    ''' If present, this function is called when the server first starts. '''
    threads = [
        Thread(
            target=collector.stats_listener,
            args=('tcp://*:5506', server_context),
        ),
        Thread(
            target=collector.usrp_listener,
            args=('tcp://*:5507', server_context, "spec_low"),
        ),
        Thread(
            target=collector.usrp_listener,
            args=('tcp://*:5508', server_context, "spec_high"),
        ),
    ]
    for t in threads:
        t.setDaemon(True)
        t.start()


def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    print('Stop')
    pass
