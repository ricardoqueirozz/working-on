//* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2011-2018 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Authors: Jaume Nin <jaume.nin@cttc.cat>
 *          Manuel Requena <manuel.requena@cttc.es>
 */

#include "ns3/core-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/internet-module.h"
#include "ns3/applications-module.h"
#include "ns3/mobility-module.h"
#include "ns3/config-store-module.h"
#include "ns3/lte-module.h"
#include <ns3/string.h>
#include <fstream>
#include <ns3/buildings-helper.h>
#include "ns3/flow-monitor-module.h"
#include "ns3/flow-monitor-helper.h"
#include "ns3/flow-probe.h"
//#include "ns3/gtk-config-store.h"

using namespace std;
using namespace ns3;

/**
 * Sample simulation script for LTE+EPC. It instantiates several eNodeBs,
 * attaches one UE per eNodeB starts a flow for each UE to and from a remote host.
 * It also starts another flow between each UE pair.
 */

NS_LOG_COMPONENT_DEFINE ("LenaSimpleEpc");
  std::ofstream m_TxTraceFile;
  std::string m_TxTraceFileName;

void
TraceSentPacket (std::string context, Ptr<const Packet> m_txTrace)
{
  //Vector position = model->GetPosition ();
  //NS_LOG_UNCOND (context << "Time Tx: "
  //              << Simulator::Now ().GetSeconds ()
  //              << " Packet = " << m_txTrace);
  if (!m_TxTraceFile.is_open ())
    {
      m_TxTraceFileName = "TxSentTrace.txt";
      m_TxTraceFile.open (m_TxTraceFileName.c_str ());
      m_TxTraceFile << "Time" << std::endl;

      if (!m_TxTraceFile.is_open ())
        {
          NS_FATAL_ERROR ("Could not open tracefile");
        }
    }

  m_TxTraceFile << Simulator::Now () << std::endl;
}

int
main (int argc, char *argv[])
{
  string lambda = "0.25";
  uint32_t packetSize = 125;
  uint16_t numEnbs= 1;
  uint16_t numUes= 1;
  Time simTime = Seconds (10);
  Time interPacketInterval = MilliSeconds (100);
  double radius = 10.0;
  double distance = 20;
  bool useUdp = false;
  bool usePoisson = true;
  bool useShadowing = false;
  bool useFading = true;
  bool disableDl = false;
  bool disableUl = true;
  bool disablePl = true;
  bool verbose = false;

  // Command line arguments
  CommandLine cmd;
  cmd.AddValue ("lambda", "Lambda to be used in the model traffic", numEnbs);
  cmd.AddValue ("packetSize", "Packet size (in bytes) to be used in the traffic with poisson distribution", packetSize);
  cmd.AddValue ("numEnbs", "Number of eNodeBs", numEnbs);
  cmd.AddValue ("numUes", "Number of UE", numUes);
  cmd.AddValue ("simTime", "Total duration of the simulation", simTime);
  cmd.AddValue ("distance", "Distance between eNBs [m]", distance);
  cmd.AddValue ("interPacketInterval", "Inter packet interval", interPacketInterval);
  cmd.AddValue ("radius", "Radius of the UE's distribution circle", radius);
  cmd.AddValue ("distance", "Distance between eNodeBs", distance);
  cmd.AddValue ("useUdp", "Use classic Udp traffic in the application", useUdp);
  cmd.AddValue ("usePoisson", "Allow use of poisson distribution in the application", usePoisson);
  cmd.AddValue ("useShadowing", "Disable the shadowing parameter of the propagation loss model", useShadowing);
  cmd.AddValue ("useFading", "Disable the shadowing parameter of the propagation loss model", useFading);
  cmd.AddValue ("disableDl", "Disable downlink data flows", disableDl);
  cmd.AddValue ("disableUl", "Disable uplink data flows", disableUl);
  cmd.AddValue ("disablePl", "Disable data flows between peer UEs", disablePl);
  cmd.AddValue ("verbose", "Allow debug LOGs", verbose);
  cmd.Parse (argc, argv);

  ConfigStore inputConfig;
  inputConfig.ConfigureDefaults ();

  // parse again so you can override default valuComandes from the command line
  cmd.Parse(argc, argv);

  Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
  //add fading
  if (useFading == true)
   {

	  lteHelper->SetAttribute ("FadingModel", StringValue ("ns3::TraceFadingLossModel"));

	  std::ifstream ifTraceFile;
	  ifTraceFile.open ("../../src/lte/model/fading-traces/fading_trace_EPA_3kmph.fad", std::ifstream::in);
	  if (ifTraceFile.good ())
	    {
	      // script launched by test.py
	      lteHelper->SetFadingModelAttribute ("TraceFilename", StringValue ("../../../src/lte/model/fading-traces/fading_trace_ETU_3kmph.fad"));
	    }
	  else
	    {
	      // script launched as an example
	      lteHelper->SetFadingModelAttribute ("TraceFilename", StringValue ("../src/lte/model/fading-traces/fading_trace_ETU_3kmph.fad"));
	    }

	  // these parameters have to be set only in case of the trace format
	  // differs from the standard one, that is
	  // - 10 seconds length trace
	  // - 10,000 samples
	  // - 0.5 seconds for window size
	  // - 100 RB
	  lteHelper->SetFadingModelAttribute ("TraceLength", TimeValue (Seconds (10.0)));
	  lteHelper->SetFadingModelAttribute ("SamplesNum", UintegerValue (10000));
	  lteHelper->SetFadingModelAttribute ("WindowSize", TimeValue (Seconds (0.5)));
	  lteHelper->SetFadingModelAttribute ("RbNum", UintegerValue (100));
   }

  lteHelper->SetAttribute ("PathlossModel", StringValue ("ns3::ThreeGppUmaPropagationLossModel"));
  //remove shadowing
  if (useShadowing == false){
	  lteHelper->SetPathlossModelAttribute ("ShadowingEnabled", BooleanValue (false));
  }

  Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper> ();
  lteHelper->SetEpcHelper (epcHelper);

  Ptr<Node> pgw = epcHelper->GetPgwNode ();

   // Create a single RemoteHost
  NodeContainer remoteHostContainer;
  remoteHostContainer.Create (1);
  Ptr<Node> remoteHost = remoteHostContainer.Get (0);
  InternetStackHelper internet;
  internet.Install (remoteHostContainer);

  // Create the Internet
  PointToPointHelper p2ph;
  p2ph.SetDeviceAttribute ("DataRate", DataRateValue (DataRate ("100Gb/s")));
  p2ph.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2ph.SetChannelAttribute ("Delay", TimeValue (MilliSeconds (10)));
  NetDeviceContainer internetDevices = p2ph.Install (pgw, remoteHost);
  Ipv4AddressHelper ipv4h;
  ipv4h.SetBase ("1.0.0.0", "255.0.0.0");
  Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign (internetDevices);
  // interface 0 is localhost, 1 is the p2p device
  Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress (1);

  Ipv4StaticRoutingHelper ipv4RoutingHelper;
  Ptr<Ipv4StaticRouting> remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
  remoteHostStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);

  NodeContainer ueNodes;
  NodeContainer enbNodes;
  enbNodes.Create (numEnbs);
  ueNodes.Create (numUes);

  // Install Mobility Model
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
  for (uint16_t i = 0; i < numEnbs; i++)
    {
      positionAlloc->Add (Vector (distance * i, 0, 0));
    }
  MobilityHelper enbMobility;
  enbMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
  enbMobility.SetPositionAllocator(positionAlloc);
  enbMobility.Install(enbNodes);

  MobilityHelper ueMobility;
	  ueMobility.SetPositionAllocator ("ns3::UniformDiscPositionAllocator",
                                       "X", DoubleValue (0.0),
                                       "Y", DoubleValue (0.0),
  									   "Z", DoubleValue (0.0),
                                       "rho", DoubleValue (radius));
  ueMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  ueMobility.Install (ueNodes);

  // Install LTE Devices to the nodes
  NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice (enbNodes);
  NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice (ueNodes);

  // Install the IP stack on the UEs
  internet.Install (ueNodes);
  Ipv4InterfaceContainer ueIpIface;
  ueIpIface = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueLteDevs));
  // Assign IP address to UEs, and install applications
  for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
    {
      Ptr<Node> ueNode = ueNodes.Get (u);
      // Set the default gateway for the UE
      Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ueNode->GetObject<Ipv4> ());
      ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);
    }

  // Attach one UE per eNodeB
  for (uint16_t i = 0; i < numEnbs; i++)
    {
	  for (uint16_t j = 0; j < numUes; j++)
	      {
		  lteHelper->Attach (ueLteDevs.Get(j), enbLteDevs.Get(i));
		  // side effect: the default EPS bearer will be activated
	      }
    }

  Ptr<EpcTft> tft = Create<EpcTft> ();
  EpcTft::PacketFilter pf;
  pf.localPortStart = 1100;
  pf.localPortEnd = 1100;
  tft->Add (pf);
  lteHelper->ActivateDedicatedEpsBearer (ueLteDevs,
                                         EpsBearer (EpsBearer::GBR_CONV_VIDEO),
                                         tft);
  
  // Install and start applications on UEs and remote host
  uint16_t dlPort = 1100;
  uint16_t ulPort = 2000;
  uint16_t otherPort = 3000;
  ApplicationContainer clientApps;
  ApplicationContainer serverApps;

  if ((useUdp == true) && (usePoisson == false))
    {
	 for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
	      {
	        if (!disableDl)
	          {
	            PacketSinkHelper dlPacketSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), dlPort));
	            serverApps.Add (dlPacketSinkHelper.Install (ueNodes.Get (u)));

	            UdpClientHelper dlClient (ueIpIface.GetAddress (u), dlPort);
	            dlClient.SetAttribute ("Interval", TimeValue (interPacketInterval));
	            dlClient.SetAttribute ("MaxPackets", UintegerValue (1000000));
	            clientApps.Add (dlClient.Install (remoteHost));
	          }

	        if (!disableUl)
	          {
	            ++ulPort;
	            PacketSinkHelper ulPacketSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), ulPort));
	            serverApps.Add (ulPacketSinkHelper.Install (remoteHost));

	            UdpClientHelper ulClient (remoteHostAddr, ulPort);
	            ulClient.SetAttribute ("Interval", TimeValue (interPacketInterval));
	            ulClient.SetAttribute ("MaxPackets", UintegerValue (1000000));
	            clientApps.Add (ulClient.Install (ueNodes.Get(u)));
	          }

	        if (!disablePl && numUes > 1)
	          {
	            ++otherPort;
	            PacketSinkHelper packetSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), otherPort));
	            serverApps.Add (packetSinkHelper.Install (ueNodes.Get (u)));

	            UdpClientHelper client (ueIpIface.GetAddress (u), otherPort);
	            client.SetAttribute ("Interval", TimeValue (interPacketInterval));
	            client.SetAttribute ("MaxPackets", UintegerValue (1000000));
	            clientApps.Add (client.Install (ueNodes.Get ((u + 1) % numUes)));
	          }
	      }
	 serverApps.Start (MilliSeconds (0.01));
	 clientApps.Start (MilliSeconds (0.01));
	 serverApps.Stop (simTime);
	 clientApps.Stop (simTime);
	 lteHelper->EnableTraces ();
    }
  
  if ((useUdp == false) && (usePoisson == true))
    {
	 for (uint32_t u = 0; u < ueNodes.GetN (); ++u)
	  	  {
	  	    if (!disableDl)
	  	      {
	  	        PacketSinkHelper dlPacketSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (ueIpIface.GetAddress(u), dlPort));
	  	        serverApps.Add (dlPacketSinkHelper.Install (ueNodes.Get (u)));

	  	        OnOffHelper dlClient ("ns3::UdpSocketFactory", InetSocketAddress (ueIpIface.GetAddress(u), dlPort));
	  	        dlClient.SetAttribute ("OnTime", StringValue ("ns3::ConstantRandomVariable[Constant=0.001]"));
	  	        dlClient.SetAttribute ("OffTime", StringValue ("ns3::ExponentialRandomVariable[Mean="+lambda+"]"));
	  	        dlClient.SetAttribute ("PacketSize", UintegerValue(packetSize));
	  	        dlClient.SetAttribute ("StartTime", TimeValue (MilliSeconds (100)));
	  	        dlClient.SetAttribute ("StopTime", TimeValue (simTime));
	  	        clientApps.Add (dlClient.Install (remoteHost));
	  	      }
	  	    if (!disableUl)
	  	  	  {
	  	  	    ++ulPort;
	  	  	    PacketSinkHelper ulPacketSinkHelper ("ns3::UdpSocketFactory", InetSocketAddress (remoteHostAddr, ulPort));
	  	  	    serverApps.Add (ulPacketSinkHelper.Install (remoteHost));

	  	  	    OnOffHelper ulClient ("ns3::UdpSocketFactory", InetSocketAddress (remoteHostAddr, ulPort));
	  	  	    ulClient.SetAttribute ("OnTime", StringValue ("ns3::ConstantRandomVariable[Constant=0.001]"));
	  	  	    ulClient.SetAttribute ("OffTime", StringValue ("ns3::ExponentialRandomVariable[Mean="+lambda+"]"));
	  	  	    ulClient.SetAttribute ("PacketSize", UintegerValue(packetSize));
	  	  	    ulClient.SetAttribute ("StartTime", TimeValue (MilliSeconds (100)));
	  	  	    ulClient.SetAttribute ("StopTime", TimeValue (simTime));
	  	  	    clientApps.Add (ulClient.Install (ueNodes.Get(u)));
	  	  	  }

	  	  }
	 serverApps.Start (MilliSeconds (0.01));
	 clientApps.Start (MilliSeconds (0.01));
	 serverApps.Stop (simTime);
	 clientApps.Stop (simTime);
	 lteHelper->EnableTraces ();
	 std::ostringstream oss;
	 	    oss << "/NodeList/"
	 	        << remoteHost->GetId ()
	 	        << "/ApplicationList/0"
	 	        << "/$ns3::OnOffApplication/Tx";

	 	    Config::Connect (oss.str (), MakeCallback (&TraceSentPacket));
    }

  // Uncomment to enable PCAP tracing
  //p2ph.EnablePcapAll("lena-simple-epc");

  Simulator::Stop (simTime);
  Simulator::Run ();

  Simulator::Destroy ();
  return 0;
}
