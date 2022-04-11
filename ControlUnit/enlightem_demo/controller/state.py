def _open_session():
    return connections[env.host_string].get_transport().open_session(timeout=env.timeout)
