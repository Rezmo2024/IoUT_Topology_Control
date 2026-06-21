import networkx as nx
import matplotlib.pyplot as plt
import math,random,time,threading
import ILP_MO_Weighted
import heapq
ENRGY_PER_NODE=0.001
TIME_PER_NODE=0.002
TX_ENERGY=0.02
BUCKET_SIZE=300
RX_ENERGY=0.01
INITIAL_ENERGY=10 #joule
SINK_ENERGY=99#joule
SINK_TO_MAINSTATION=2000 #distance in meters
BROADCAT_PACKET=60*8 #BIT
BANDWIDTH=10000 #kbps
FREQUENCY=25 #KHZ
TRANSMISSION_POWER=0.02 #WATT
SOUND_SPEED=1500 #M/S
class Packet:
    def __init__(self,ID, source, destination, size,path):
        self.ID = ID
        self.source = source
        self.destination = destination
        self.size = size
        self.delay = 0
        self.loss = 0
        self.tx_energy = 0
        self.rx_energy = 0
        self.process_time = 0
        self.process_energy = 0
        self.path = path

class Main():
    def __init__(self):
        self.Event_Log=[]
        self.Topology=None
        self.Nodes_Energy=[]
        self.SIMULATION_TIME=0
        self.PACKET_RATE=0 #per second
        self.PACKET_SIZE=0 #bit
        self.log_file=""
        self.TRANSMISSION_RANGE=0 #METERS
        self.method="HopCountShortestPath" #default
        self.srcdest_pairs={}
        self.paths={}
        self.Is_Paths=False
        self.path_refresh_interval=10
        self.sinkid=1

    def set_SimTime(self,t):
        self.SIMULATION_TIME=t
    def set_PacketRate(self,pr):
        self.PACKET_RATE=pr
    def set_PacketSize(self,ps):
        self.PACKET_SIZE=ps*8 #bit
    def set_LogFile(self,lf):
        self.log_file=lf 
    def set_Method(self,met):
        self.method=met
    def set_Range(self,met):
        self.TRANSMISSION_RANGE=met        
    def set_Srcdest_pairs(self,srde):
        self.srcdest_pairs=srde  
    def set_pathrefresTime(self,t):
        self.path_refresh_interval=t   
    def set_Sink(self,s):
        self.sinkid=s                        
                               
    def Create_Topology(self,cor_file,sinkid):
        self.Topology=self.LoadTo_Networkx(self.TRANSMISSION_RANGE,cor_file)
        node_list = list(self.Topology.nodes())
        for i in node_list:
            if i!=sinkid:
                self.Nodes_Energy.append([i,INITIAL_ENERGY])
            else:
                self.Nodes_Energy.append([i,SINK_ENERGY])

    def calculate_gamma(self,P, r, dab, f):
        log_P = math.log10(P)
        log_r_sq = math.log10(4 * math.pi * r * r)
        log_const = math.log10(0.67 * 1e-18)
        term1 = 10 * (log_P - log_r_sq - log_const) - 20 * math.log10(dab)
        f_sq = f * f
        term2 =((
            (0.11 * f_sq / (1 + f_sq)) + (44 * f_sq / (4100 + f_sq ))+  2.75e-4 * f_sq + 0.003)*dab * 1e-3)
        term3 = -50 + 18 * math.log10(f)
        gamma = term1 - term2 + term3
        return gamma
    def calculate_Link_Reliability(self,n, gamma):
        term1 = 1 / 2
        term2 = 1 / 2
        term3 = 10**(gamma / 10)
        term4 = 1 + 10**(gamma / 10)
        r = (term1 + term2 * (term3 / term4))**n
        return r   
    def LoadTo_Networkx(self,Range,fname):
        G = nx.Graph()
        with open(fname, 'r') as file:
            i=1
            for line in file:
                x, y, z = map(int, line.strip().split(","))
                G.add_node(int(i), pos=(x, y, z))
                i+=1
        for node1 in G.nodes():
            for node2 in G.nodes():
                if node1 != node2:
                    pos1 = G.nodes[node1]['pos']
                    pos2 = G.nodes[node2]['pos']
                    distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)
                    if distance <= Range and distance>0:
                        link_delay=distance/SOUND_SPEED
                        link_reliability=self.calculate_Link_Reliability(self.PACKET_SIZE,self.calculate_gamma(TRANSMISSION_POWER,self.TRANSMISSION_RANGE,distance,FREQUENCY))
                        G.add_edge(node1, node2,weight=link_delay,length=link_reliability)
        return G  
    def LossBased_Dijkstra(self,graph, start, end):
            #Computes the shortest path considering the multiplicative loss rate.
            distance = {node: float('inf') for node in graph}
            distance[start] = 1.0
            previous = {node: None for node in graph}
            # Create a priority queue
            pq = [(1.0, start)]
            i=0
            while pq:
                # Get the node with the smallest loss rate
                #print(pq)
                i+=1
                current_loss, current_node = heapq.heappop(pq)
                if current_node == end:
                    path = []
                    node = end
                    while node is not None:
                        path.append(node)
                        node = previous[node]
                    path.reverse()
                    return path, current_loss
                # If the current loss rate is greater than the stored loss rate, skip this node
                if current_loss > distance[current_node]:
                    continue
                # Update the distance and previous dictionaries for the neighbors
                for neighbor, loss_rate in graph[current_node].items():
                    #because the weight of links are very small, I multiply by 10^6. If I don't do this, 
                    #the algorithm cannot solve the path due to precision in floating points
                    new_loss = current_loss * (loss_rate) 
                    if new_loss < distance[neighbor]:
                        distance[neighbor] = new_loss
                        previous[neighbor] = current_node
                        heapq.heappush(pq, (new_loss, neighbor))
            # If no path is found, return None
            return None, None
    def Popular_dijkstra(self,graph, start, end):
        #Computes the shortest path considering the distance or delay values.
        # Initialize the distance and previous dictionaries
        distance = {node: float('inf') for node in graph}
        distance[start] = 0
        previous = {node: None for node in graph}
        # Create a priority queue
        pq = [(0, start)]
        while pq:
            # Get the node with the smallest distance
            current_distance, current_node = heapq.heappop(pq)
            # If we've reached the end node, return the path and distance
            if current_node == end:
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = previous[node]
                path.reverse()
                return path, current_distance
            # If the current distance is greater than the stored distance, skip this node
            if current_distance > distance[current_node]:
                continue
            # Update the distance and previous dictionaries for the neighbors
            for neighbor, weight in graph[current_node].items():
                new_distance = current_distance + weight
                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_distance, neighbor))
        # If no path is found, return None
        return None, None
         
    def Plot(self,G):    
        pos = nx.spring_layout(G) 
        nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=10, font_color='black', font_weight='bold')
        plt.title("Graph of Nodes and Edges")
        plt.show()    

    def create_graph_dictionary(self,G,field):
        delay_dic = {}
        # Populate the outer dictionary with nodes as keys
        for node in G.nodes():
            delay_dic[node] = {}
        # Populate the inner dictionaries with edges and weights
        for edge in G.edges(data=True):
            node1, node2, edge_data = edge
            weight = edge_data[field]
            delay_dic[node1][node2] = weight
            delay_dic[node2][node1] = weight
        return delay_dic        

    def Eliminate_DeadNodes(self,topo):
        for node in topo:
            for neighbor in topo[node]:
                for j in range(len(self.Nodes_Energy)):
                    if self.Nodes_Energy[j][0]==node and self.Nodes_Energy[j][1]<=0.0:
                        topo[node][neighbor]=999999999#float('inf')
                        #print("changed status")

    def Set_Links_EnergyScore(self,topo):
        head=0
        tail=0
        Ret_Topo=topo
        for node in topo:
            for neighbor in topo[node]:
                for j in range(len(self.Nodes_Energy)):
                    if self.Nodes_Energy[j][0]==node and self.Nodes_Energy[j][1]>0.0:
                        head=self.Nodes_Energy[j][1]
                    if self.Nodes_Energy[j][0]==neighbor and self.Nodes_Energy[j][1]>0.0:
                        tail=self.Nodes_Energy[j][1]                        
                if head!=0 and tail!=0:
                    if tail > head: #min value of head or tail
                        Ret_Topo[node][neighbor]=head
                    else:
                        Ret_Topo[node][neighbor]=tail                        
        return Ret_Topo
    def find_max_value(self,graph):
        max_value = 0  
        for node, neighbors in graph.items():
            for neighbor, value in neighbors.items():
                if value > max_value:
                    max_value = value
        return max_value

    def Set_Links_Cost(self,topo1,topo2,alpha):
        Ret_Topo=topo1
        max_topo1=self.find_max_value(topo1)
        max_topo2=self.find_max_value(topo2)
        for node in topo1:
            for neighbor in topo1[node]:
                for j in range(len(self.Nodes_Energy)):
                        Ret_Topo[node][neighbor]=alpha*(topo1[node][neighbor]/max_topo1) +(1-alpha)*(topo2[node][neighbor]/max_topo2)
        return Ret_Topo  

    def Set_Links_Cost(self,topo1,topo2,alpha):
        Ret_Topo=topo1
        max_topo1=self.find_max_value(topo1)
        max_topo2=self.find_max_value(topo2)
        for node in topo1:
            for neighbor in topo1[node]:
                for j in range(len(self.Nodes_Energy)):
                        Ret_Topo[node][neighbor]=alpha*(topo1[node][neighbor]/max_topo1) +(1-alpha)*(topo2[node][neighbor]/max_topo2)
        return Ret_Topo          
    def Set_Links_Cost2(self,topo1,topo2,topo3,alpha):
        Ret_Topo=topo1
        max_topo1=self.find_max_value(topo1)
        max_topo2=self.find_max_value(topo2)
        max_topo3=self.find_max_value(topo3)
        for node in topo1:
            for neighbor in topo1[node]:
                for j in range(len(self.Nodes_Energy)):
                        Ret_Topo[node][neighbor]=alpha*((topo1[node][neighbor]/max_topo1) +(topo2[node][neighbor]/max_topo2)+(topo3[node][neighbor]/max_topo3))
        return Ret_Topo  
    def Reverse_values(self,topo1):
        Ret_Topo=topo1
        for node in topo1:
            for neighbor in topo1[node]:
                for j in range(len(self.Nodes_Energy)):
                    if topo1[node][neighbor]>0:
                        Ret_Topo[node][neighbor]=1/(topo1[node][neighbor])
                    else:
                        topo1[node][neighbor]=9999999999999 #ecause 1/0 means infinity
        return Ret_Topo                          
    def Update_Energy_For_Broadcat(self,sinkid):
        for j in range(len(self.Nodes_Energy)):
            if self.Nodes_Energy[j][0]==sinkid: #sink node
                self.Nodes_Energy[j][1]=self.Nodes_Energy[j][1]-ENRGY_PER_NODE-((BROADCAT_PACKET/BANDWIDTH)*TX_ENERGY)
            else:
                self.Nodes_Energy[j][1]=self.Nodes_Energy[j][1]-ENRGY_PER_NODE-((BROADCAT_PACKET/BANDWIDTH)*RX_ENERGY)
    def Scale_values(self,graph,rmin,rmax):
        all_values = [value for edges in graph.values() for value in edges.values()]
        min_value = min(all_values)
        max_value = max(all_values)
        # Calculate the range of current values
        value_range = max_value - min_value
        # Calculate the scaling factor
        scaling_factor=0
        if value_range>0:
            scaling_factor = (rmax - rmin) / value_range #in [min,max]
        # Apply the transformation to each value in the graph
        transformed_graph = {}
        for node, edges in graph.items():
            transformed_edges = {}
            for neighbor, value in edges.items():
                if scaling_factor>0:
                    new_value = (value - min_value) * scaling_factor + rmin
                else:
                    new_value=value
                transformed_edges[neighbor] = new_value
            transformed_graph[node] = transformed_edges
        return transformed_graph

    def Calculate_Paths(self):
            topo1=self.create_graph_dictionary(self.Topology,'weight')
            topo2=self.create_graph_dictionary(self.Topology,'length')
            for item in self.srcdest_pairs:
                s=item[0]
                d=item[1]
                path=None
                try:
                    if self.method=="NON-SDNHop-CountShortestPath":
                        path = nx.shortest_path(self.Topology, source=s, target=d)#hop count
                    elif self.method=="SDNHopCountShortestPath":
                        #path = nx.shortest_path(self.Topology, source=s, target=d, weight='weight')
                        path = nx.shortest_path(self.Topology, source=s, target=d)#hop count                    
                    elif self.method=="DelayShortestPath":
                            self.Eliminate_DeadNodes(topo1)
                            path,pathcost=self.Popular_dijkstra(topo1,s,d)  
                except:
                    print("There is no path")
 
                if path!=None:
                    self.paths[(s,d)]=path
                else:
                    self.paths[(s,d)]=None
            print(self.paths)
            if len(self.paths)>0:
                self.Is_Paths=True
            self.Update_Energy_For_Broadcat(self.sinkid) #update energy consumption for broadcast packet receive and send
    def is_packet_corrupted(self,path_loss):
        random_value = random.uniform(0, 1)
        if  path_loss > random_value:
            #print("loss",path_loss,random_value)
            return True
        else:
            return False   

    def calculate_path_loss(self,G, path):
        total_weight = 1
        if path!=None  and len(path)>0:
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                total_weight *= (1-G[u][v]['length'])
        return (total_weight)
    def calculate_path_delay(self,G, path):
        total_weight = 1
        if path!=None  and len(path)>0:
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                total_weight += G[u][v]['weight']
        return total_weight        
    def Simulate(self,src,dst):
        self.Perform(src,dst)
    def Perform(self,src,dst):
        #wait until paths to be computed
        """"
        while True:
            if self.Is_Paths==True:
                break
        """
        # Set the average rate of events (e.g., cars, packets) per unit time
        _lambda = self.PACKET_RATE #5
        # Set the number of total events to generate
        _num_total_arrivals = self.SIMULATION_TIME*_lambda #150
        # Initialize the number of arrivals per unit time
        _num_arrivals = 0
        # Initialize the arrival time
        _arrival_time = time.time()
        # Initialize the list of arrivals per unit time
        _num_arrivals_in_unit_time = []
        # Set the time tick (i.e., the length of each unit time interval)
        _time_tick = _arrival_time+1
        # Generate the events and record the number of arrivals per unit time
        Start_time=time.time()
        packet_id=1
        for i in range(_num_total_arrivals):
            # Get the next probability value from Uniform(0,1)
            p = random.random()
            # Plug it into the inverse of the CDF of Exponential(_lambda)
            #  In other words, the inverse CDF at a specific probability p gives you the number x for which Pr(X <= x) = p.
            #F(x) = 1 – e^(–Lx)   ==>  x = –log(1–u)/L
            #  This quantile helps in understanding the distribution and can be used to generate random numbers from the distribution using a uniform random variable.
            #By knowing the cumulative distribution function (CDF) of a distribution, you can always generate a random sample from that distribution using the inverse CDF technique. 
            _inter_arrival_time = -math.log(1.0 - p)/_lambda
            # Add the inter-arrival time to the running sum
            _arrival_time = _arrival_time + _inter_arrival_time
            # Increment the number of arrivals per unit time
            _num_arrivals = _num_arrivals + 1
            # If the arrival time is greater than the time tick, reset the number of arrivals and increment the time tick
            if _arrival_time > _time_tick:
                _num_arrivals_in_unit_time.append(_num_arrivals)
                _num_arrivals = 0
                _time_tick = _time_tick + 1
            while time.time()<_arrival_time:
                time.sleep(0.00000001)
                #print(".",end="")
            else:
                if self.Is_Paths==True:
                    path= self.paths[(src, dst)]
                else:
                    path=None
                #print(path)
                if path!=None and len(path)>0 :
                    if self.Is_Valid_Path(path):
                        p=Packet(packet_id,src,dst,self.PACKET_SIZE,path)
                        self.Update_Packet_State(p,self.Topology)
                        str_packet="| "+str(p.loss)+"  "+str(p.delay)+"  "+str(p.tx_energy)+"  "+str(p.rx_energy)+ \
                        "  "+str(p.size)+"  "+str(p.process_energy)+"  "+str(p.process_time)
                        str1=" S "+str(packet_id)+" s "+str(src)+' d '+str(dst)+" "+str_packet
                        self.Event_Log.append([_arrival_time,str1])
                        str2=" R "+str(packet_id)+" s "+str(src)+' d '+str(dst)+" "+str_packet
                        self.Event_Log.append([_arrival_time+p.delay,str2])
                        packet_id=packet_id+1
                    else:
                        self.Event_Log.append([time.time(),"No_Valid Path Due To ENERGY Depletion"])
                else:
                    self.Event_Log.append([time.time(),"No Valid Path Due To Connectivity"])                        
            if len(self.Event_Log) > BUCKET_SIZE:
                for item in range(len(self.Nodes_Energy)):
                    str3=" E "+str(self.Nodes_Energy[item][0])+" "+str(self.Nodes_Energy[item][1])
                    self.Event_Log.append([time.time(),str3])
                """self.WriteLog_ToFile()
                self.Event_Log.clear() """ 
    def Is_Valid_Path(self,p):# check validation of path in terms of energy
        flag=True
        for i in p:
            for j in range(len(self.Nodes_Energy)):
                if self.Nodes_Energy[j][0]==i and self.Nodes_Energy[j][1]<=0.0:
                    flag=False
        return flag
    def WriteLog_ToFile(self):
        #sort accordint to the time of event
        sorted_list = sorted(self.Event_Log, key=lambda x: x[0])
        with open(self.log_file, "a") as f:
                f.write("time  Send/Receive  packet_id  s=source  d=destination  | loss   delay  Tx_energy  RX_enery  packet_size  Process_energy  Process_time\n")
                for item in sorted_list:
                    f.write(str(item[0])+" "+item[1]+"\n")
        self.Event_Log.clear()
    def Update_Packet_State(self,p,Topo):
        if p.path!=None and (len(p.path)>0):
            p.delay=self.calculate_path_delay(Topo,p.path)+(SINK_TO_MAINSTATION/(3*10**8))
            flag=True
            for i in p.path:
                for j in range(len(self.Nodes_Energy)):
                    if self.Nodes_Energy[j][0]==i and self.Nodes_Energy[j][1]<=0.0: #Drop due to energy depletion of nodes in the path
                        p.loss=1
                        flag=False
            if flag==True:
                loss=self.calculate_path_loss(Topo,p.path)
                if self.is_packet_corrupted(loss)==True:
                    p.loss=1  # it means packet is corrupted and will not be received  by destination
                else:
                    p.loss=0 # it means packet is not corrupted and will be received  by destination
            p.process_energy=len(p.path)*ENRGY_PER_NODE
            p.process_time=len(p.path)*TIME_PER_NODE
            p.rx_energy=(len(p.path)-1)*((self.PACKET_SIZE/BANDWIDTH)*TX_ENERGY)
            p.tx_energy=(len(p.path)-1)*((self.PACKET_SIZE/BANDWIDTH)*RX_ENERGY)
            self.Update_Energy(p.path)

        else:
            print("Path is Invalid")
    def Update_Energy(self,p):
        if p!=None and (len(p)>0):
            for i in range(len(p)):
                for j in range(len(self.Nodes_Energy)):
                    if self.Nodes_Energy[j][0]==p[i]: #node Number
                        if i==0 and self.Nodes_Energy[j][1]>0: #source node
                            self.Nodes_Energy[j][1]=self.Nodes_Energy[j][1]-ENRGY_PER_NODE-((self.PACKET_SIZE/BANDWIDTH)*TX_ENERGY)
                        elif i==len(p)-1 and self.Nodes_Energy[j][1]>0: #dest node
                            self.Nodes_Energy[j][1]=self.Nodes_Energy[j][1]-ENRGY_PER_NODE-((self.PACKET_SIZE/BANDWIDTH)*RX_ENERGY)
                        elif self.Nodes_Energy[j][1]>0:# intermediate nodes
                            self.Nodes_Energy[j][1]=self.Nodes_Energy[j][1]-ENRGY_PER_NODE-((self.PACKET_SIZE/BANDWIDTH)*(RX_ENERGY+TX_ENERGY))


class SenderThread(threading.Thread):
    def __init__(self, m,src,dst):
        threading.Thread.__init__(self)
        self.src=src
        self.dst=dst
        self.m=m
    def run(self):
        self.m.Simulate(self.src,self.dst)

class PathThread(threading.Thread):
    def __init__(self, m,st,period_len):
        threading.Thread.__init__(self)
        self.m=m
        self.starttime=st
        self.plen=period_len
    def run(self):
            while True:
                if time.time()-self.starttime >= self.m.SIMULATION_TIME :
                    return
                self.m.Calculate_Paths()        
                time.sleep(self.plen)





