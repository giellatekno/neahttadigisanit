# Infra

Infrastructure notes.

## Files

  - `nds.service` - A template systemd unit file
  - `PROJ.conf` - Server block for nginx, one per project instance
  - `nds-PROJ.init.d-script` - _init.d_ script that has been used traditionally.

On the server, nginx proxy passes each server to each systemd service (see the
`PROJ.conf` file). The corresponding internal gunicorn server must listen on
the same port the `PROJ.conf` location block proxies to.

## init script

From `/etc/rc.d/init.d/README` on the server:

    Note that traditional init scripts continue to function on a systemd
    system. An init script /etc/rc.d/init.d/foobar is implicitly mapped
    into a service unit foobar.service during system initialization.

So that's how it currently operates. Can probably remove this, and just use
systemd unit files directly.
