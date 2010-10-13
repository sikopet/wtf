import wtf.node as node

class APBase(node.NodeBase):
    """
    Access Point

    This represents the platform-independent AP that should be used by tests.

    Real APs should extend this class and implement the actual AP functions.
    """

    def __init__(self, comm):
        """
        Create an AP with the supplied default configuration.
        """
        node.NodeBase.__init__(self, comm=comm)

class APConfig():
    """
    Access Point configuration object

    Access Points have all sorts of configuration variables.  Perhaps the most
    familiar ones are the SSID and the channel.
    """

    def __init__(self, ssid, channel=None):
        self.ssid = ssid
        self.channel = channel

class Hostapd(node.LinuxNode, APBase):
    """
    Hostapd-based AP
    """
    def __init__(self, comm, iface, driver=None):
        node.LinuxNode.__init__(self, comm, iface, driver)
        self.config = None

    def start(self):
        if self.initialized != True:
            raise UninitializedError()
        if not self.config:
            raise node.InsufficientConfigurationError()
        self._configure()
        self._cmd_or_die("hostapd -B /tmp/hostapd.conf")

    def stop(self):
        self.comm.send_cmd("killall hostapd")
        self.comm.send_cmd("iw dev mon." + self.iface + " del")
        self.comm.send_cmd("rm -f /var/run/hostapd/" + self.iface)

    base_config = """
driver=nl80211
logger_syslog=-1
logger_syslog_level=2
logger_stdout=-1
logger_stdout_level=0
dump_file=/tmp/hostapd.dump
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
hw_mode=g
beacon_int=100
dtim_period=2
max_num_sta=255
rts_threshold=2347
fragm_threshold=2346
macaddr_acl=0
auth_algs=3
ignore_broadcast_ssid=0
eapol_key_index_workaround=0
eap_server=0
own_ip_addr=127.0.0.1
"""
    def _configure(self):
        config = self.base_config
        config += "ssid=" + self.config.ssid + "\n"
        config += "channel=%d\n" % self.config.channel
        config += "interface=" + self.iface + "\n"
        self._cmd_or_die("echo -e \"" + config + "\"> /tmp/hostapd.conf",
                         verbosity=0)
