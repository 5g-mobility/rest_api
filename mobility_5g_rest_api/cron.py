from osmclient import client

hostname = "10.0.13.252"
myclient = client.Client(host=hostname)


def turn_off_cameras():
    myclient.ns.delete("non_static_5g_mobility")


def turn_on_cameras():
    myclient.ns.create("non_static_5g_mobility-ns", "non_static_5g_mobility", "Openstack")
