# Copyright cozybit, Inc 2010-2011
# All rights reserved

import wtf.node.ap as ap
import wtf.node.sta as sta
import wtf.node.p2p as p2p
import wtf.node.mesh as mesh

class config():
    def __init__(self, suite=None, nodes=[], name="<unamed config>"):
        """
        A wtf config is a list of suites to run and the nodes to run them on.
        """
        self.suite = suite
        self.nodes = nodes

        # populate node lists used by tests.
        self.aps = []
        self.stas = []
        self.p2ps = []
        self.mps = []

        for n in nodes:
            if isinstance(n, p2p.P2PBase):
                # We check p2p before the other types because a p2p node might
                # extend an sta or an ap.
                self.p2ps.append(n)
            elif isinstance(n, ap.APBase):
                self.aps.append(n)
            elif isinstance(n, sta.STABase):
                self.stas.append(n)
            elif isinstance(n, mesh.MeshBase):
                self.mps.append(n)

        self.name = name

    def setUp(self):
        """
        setUp is called before this configuration is run
        """
        pass

    def tearDown(self):
        """
        tearDown is called after the configuration is run
        """
        pass
