import math
def is_float(string):
    if string.replace(".", "").isnumeric():
        return True
    else:
        return False
def Extract_Results(log_filename,OutputFile,trfile,strlabel,total_nodes,simtime):
    total_recv=0
    total_delay=0
    total_txenergy=0
    total_rxenergy=0
    total_size=0
    total_processenergy=0
    total_processtime=0
    count_loss=0
    count_delay=0
    count_txenergy=0
    count_rxenergy=0
    Energy_idle=0.001
    count_size=0
    count_processenergy=0
    count_processtime=0
    lifetime=0
    dead_node={}
    count=0
    first_time=0
    prev_time=0
    interval=3 #seconds
    ic=1
    throughtput=0
    with open(trfile, "a") as f:
        f.write("\n***"+strlabel+"***\n")
    with open(log_filename, "r") as f:
        for line in f:
            fields = line.strip().split()
            count+=1
            if first_time==0 and  is_float(fields[0]):
                    first_time=float(fields[0])
                    prev_time=first_time
            if is_float(fields[0]):
                if (float(fields[0])-prev_time>=interval):
                    prev_time=float(fields[0])
                    with open(trfile, "a") as f:
                        f.write(str(ic*interval)+" "+str(throughtput/interval)+"\n")
                    throughtput=0
                    ic+=1
            if fields[1] == "R":
                total_recv+=1
                if float(fields[8])>0:
                    #total_loss += float(fields[8])
                    count_loss += 1
                if float(fields[9])>0:                
                    total_delay += float(fields[9])
                    count_delay += 1
                if float(fields[10])>0: 
                    count_txenergy+=1
                    total_txenergy+=float(fields[10])
                if float(fields[11])>0: 
                    count_rxenergy+=1
                    total_rxenergy+=float(fields[11])
                if float(fields[12])>0: 
                    count_size+=1
                    total_size+=float(fields[12])
                    throughtput+=float(fields[12])
                if float(fields[13])>0: 
                    count_processenergy+=1
                    total_processenergy+=float(fields[13])
                if float(fields[13])>0: 
                    total_processtime+=float(fields[14])
                    count_processtime+=1       
            elif fields[1] == "E" and float(fields[3])<=0:
                dead_node[fields[2]]=fields[3]
            elif fields[1] == "No_Valid" and fields[6] == "Depletion" and lifetime==0:
                #if len(dead_node)>=total_nodes*0.1: #10 percent of nodes
                    lifetime=float(fields[0])-first_time

    print("Total Count:", count ," and Results stored in File",OutputFile)
    if count>0:
        with open(OutputFile, "a") as f:
            f.write("\n\n***"+strlabel+"***")
            if total_recv>0:
                f.write("\nAverage Loss:"+str(count_loss/total_recv))
            else:
                f.write("\nAverage Loss: 0.0")              
            if count_delay>0:
                f.write("\nAverage Delay:"+str(total_delay/count_delay))
            else:
                f.write("\nAverage Delay: 0.0")
            if count_processenergy>0:
                f.write("\nTotal Process Energy:"+str(total_processenergy/count_processenergy))
            else:
                f.write("\nTotal Process Energy: 0.0")
            if count_processtime>0:
                f.write("\nAverage Process time:"+str(total_processtime/count))
            else:
                f.write("\nAverage Process time: 0.0")
            if total_nodes>0:
                            f.write("\nTotal_Nodes:"+str(total_nodes))
            else:
                            f.write("nTotal_Nodes: 0")                  
            f.write("\nTotal Energy:"+str(total_rxenergy+total_txenergy+total_processenergy+total_nodes*Energy_idle*simtime))
            #f.write("\nTotal Rx Energy:"+str(total_rxenergy))
            #f.write("\nTotal TX Energy:"+str(total_txenergy))
            f.write("\nTotal Size:"+str(total_size))
            f.write("\nNumber of Dead Nodes:"+str(len(dead_node)))#+" "+str(dead_node))
            f.write("\nLifetime:"+str(lifetime))
