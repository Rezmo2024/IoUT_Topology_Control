import time,os,Show_Results
from Simulator import *
from Result_Extractor import *
import GenerateTopology
def deploy_sendernodes_grid(n, width, height,depth):
    nodes = []
    grid_size = math.ceil(math.sqrt(n))
    step_x = width / grid_size
    step_y = height / grid_size
    count = 0
    for i in range(grid_size):
        for j in range(grid_size):
            if count < n:
                x = (j + 0.5) * step_x
                y = (i + 0.5) * step_y
                nodes.append(f"{int(x)},{int(y)},{int(depth)}\n")
                count += 1
            else:
                break
        if count >= n:
            break
    return nodes
def generate_coordinates(toptype,filename, xc,yc,zc,nsenders,rc,rs):
        coordinates = []
        n=[]       
        #sender nodes
        coordinates=deploy_sendernodes_grid(nsenders, xc,yc,zc)
        #sink node
        coordinates.append(f"{xc//2},{yc//2},{0}\n")                                       
        with open(filename, 'w') as file:
                file.writelines(coordinates)
        if toptype=="CB":
            n=GenerateTopology.generate_CB_nodes(xc,yc,zc,rc,rs)
        elif toptype=="TO":
            n=GenerateTopology.generate_TO_nodes(xc,yc,zc,rc,rs)
        elif toptype=="HP":
            n=GenerateTopology.generate_HP_nodes(xc,yc,zc,rc,rs)
        elif toptype=="RD":
            n=GenerateTopology.generate_RD_nodes(xc,yc,zc,rc,rs)     
        elif toptype=="GRID":
            n=GenerateTopology.generate_3d_grid(xc,yc,zc,rs)
        f = open(filename, "a")  # Open file for writing coordinates
        f.writelines(n)  # Write coordinates to file
        f.close()
        return len(n)+nsenders

current_time=time.time()
simtime=240
Period_Length=10 # interval that SDN controller anounces new paths
log_file="log.txt"
total_results_file="Total_Results.txt"
result_file="Results.txt"
cor_file="coordinates.txt"
tr_file="Throughput\\Throughput" 
f=open(result_file, "w")   
f.close()
Sensor_Communication_Range=300
Sensor_sense_Range=(Sensor_Communication_Range/(4/math.sqrt(5)))
# IMPORTANT!!!!!!!For rc /rs ≥ 4/sqrt(5), all nodes are connected with their physically neighboring nodes and full coverage is always maintained.
Topology_type=["GRID","RD","CB","TO","HP"]
methods=["SDNHopCountShortestPath"]#,"NONSDNHopCountShortestPath","DelayShortestPath"]
rates=[1,2,3,4,5]
sizes=[40,60,80,100,120]
#os.remove(total_results_file)
#os.remove(cor_file)
nsenders=20
for t in range(len(Topology_type)):
    numnodes=generate_coordinates(Topology_type[t],cor_file,2000,2000,2000,nsenders,Sensor_Communication_Range,Sensor_sense_Range)#nn,x,y,z,nsenders,range
    src_dst_pairs=[]
    sink=nsenders+1 #sink ID
    for i in range(1,nsenders+1):
        src_dst_pairs.append([i,sink])
    for q in range(len(sizes)):
        for j in range(len(rates)):
            for k in range(len(methods)):
                m=Main()
                current_time=time.time()
                m.set_Range(Sensor_Communication_Range)
                m.set_SimTime(simtime)
                m.set_PacketSize(sizes[q])
                m.Create_Topology(cor_file,sink)
                m.set_PacketRate(rates[j])
                m.set_Method(methods[k])
                m.set_Srcdest_pairs(src_dst_pairs)
                m.set_pathrefresTime(10)
                m.set_Sink(sink)
                log_file="log_"+Topology_type[t]+""+methods[k]+"_"+str(rates[j])+"_"+str(sizes[q])+".txt"
                stringlabel=Topology_type[t]+""+methods[k]+"_"+str(rates[j])+"_"+str(sizes[q])
                f=open((tr_file+stringlabel+".txt"), "w")   
                f.close()
                f=open(log_file, "w")  
                f.close()
                m.set_LogFile(log_file)
                if methods[k]!="NONSDNHopCountShortestPath":#for non-SDN solutions there is no need to install path periodically
                    pthread = PathThread(m,current_time,Period_Length)
                    pthread.start()
                else:
                    m.Calculate_Paths() # this is called only once for Non-SDN solutiins (To prohibit null paths at the beginning of simulation)
                    
                for i in range(len(src_dst_pairs)):
                    thread = SenderThread(m,src_dst_pairs[i][0],src_dst_pairs[i][1])
                    thread.start()
                thread.join()
                if methods[k]!="NONSDNHopCountShortestPath":#for non-SDN solutions
                    pthread.join()
                m.WriteLog_ToFile()
                #Plot(Topology)
                print("\nSim Time=",time.time()-current_time)
                total_nodes=numnodes+1
                Extract_Results(log_file,result_file,(tr_file+stringlabel+".txt"),stringlabel,total_nodes,simtime)
                os.remove(log_file)
        Show_Results.extract_data(result_file,str(sizes[q]))
        with open(total_results_file, 'a') as f2:
            with open(result_file, 'r') as f1:
                f2.write(f1.read())
        f=open(result_file, "w")  # reset file and clean it 
        f.close()