# Copyright cozybit, Inc 2010-2011
# All rights reserved

"""
Test mesh 11aa performance (using ath9k_htc cards)

NOTE: specify test video file with ennvironment variable REF_CLIP

These tests comprise scripts for assessing the feasibility of multicast HD
video over wifi. Things you will need:

    - qpsnr in your path, see: git://github.com/hsanson/qpsnr.git
    - cvlc installed on your test nodes
    - custom 9271 fw with mcast rate patch

    vlc (can't run as root):
        server:
        cvlc -I dummy $file :sout="#rtp{dst=$client_ip,port=5004,mux=ts,ttl=1}" :sout-all :sout-keep vlc://quit

        client:
        cvlc -I dummy rtp://$client_ip --sout file/ts:out.ts

    hint: sync multiple mcast recepients with '--netsync-master' on the server
          and '--netsync-master-ip=<server_ip>' on the clients.

    qpsnr:
        ./qpsnr -a avg_ssim -s100 -m1000 -o fpa=1000 -r <ref_vid> <recv_vid>
        ./qpsnr -a avg_psnr -s100 -m1000 -o fpa=1000 -r <ref_vid> <recv_vid>

TODO: The idea is to run these in a controlled environment simulating
"real-world" conditions by generating contention and collisions. For now the
tests are just run in an enclosure.

Each test surverys the link quality with iperf and some video streaming
metrics, but modifies the channel type and unicast / mcast address.
Test script:
    0. run UDP iperf and get throughput / losses
    1. stream video and do quality metric analysis
    2. change mesh conf for next test

We test the following link cases:
    1. unicast HT20.
    2. unicast noHT.
    3. mcast MCS7.
    4. mcast 54mb/s

"""

import wtf.node.mesh as mesh
import unittest
import time
import wtf
from wtf.util import *
import sys; err = sys.stderr
import time
import os

wtfconfig = wtf.conf
sta = wtfconfig.mps

mcast_dst = "224.0.0.0"
ref_clip = os.getenv("REF_CLIP")
# XXX: nose probably has something like this?
results={}

# global setup, called once during this suite
def setUp(self):
    for n in wtfconfig.mps:
        n.shutdown()
        n.init()
        n.start()

def tearDown(self):
    for n in wtfconfig.nodes:
        n.stop()

    print "                                                     ref_clip=%s" % (ref_clip,)
    print "TEST             THROUGHPUT(Mb/s)        LOSS(%)       SSIM        PSNR      DCM     FILE"
    for test, result in results.iteritems():
        line = "%s      " % (test,)

        if result.perf != None:
            perf = result.perf
            line += "%f         %f      " % (perf.tput, perf.loss)
        if result.vqm != None:
            vqm = result.vqm
            line += "%s     %s  %s  %s      " % (vqm.ssim, vqm.psnr, vqm.dcm, vqm.out_clip)

        print line

class Test11aa(unittest.TestCase):

# run before / after each test
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1_unicast_ht20(self):
        fname = sys._getframe().f_code.co_name

        perf_report = do_perf(sta[:2], sta[1].ip)
        vqm_report = do_vqm(sta[:2], sta[1].ip, ref_clip)

        results[fname] = LinkReport(perf_report=perf_report, vqm_report=vqm_report)

    def test_2_unicast_noht(self):
        fname = sys._getframe().f_code.co_name

        conf = sta[0].config
        conf.htmode = ""
        reconf_stas(wtfconfig.mps, conf)

        perf_report = do_perf(sta[:2], sta[1].ip)
        vqm_report = do_vqm(sta[:2], sta[1].ip, ref_clip)

        results[fname] = LinkReport(perf_report=perf_report, vqm_report=vqm_report)

    def test_3_mcast_mcs7(self):
        # XXX: need new firmware, derp
        # better to support mcast_rate in kernel and 9271 firmware
        pass

    def test_4_mcast_54mbps(self):
        # hard-coded to 54mbps for now
        fname = sys._getframe().f_code.co_name

        conf = sta[0].config
        conf.mesh_params = "mesh_ttl=1"
        conf.mcast_rate = "54"
        conf.mcast_route = mcast_dst
        reconf_stas(wtfconfig.mps, conf)

        perf_report = do_perf(sta[:2], mcast_dst)
        vqm_report = do_vqm(sta[:2], mcast_dst, ref_clip)

        results[fname] = LinkReport(perf_report=perf_report, vqm_report=vqm_report)