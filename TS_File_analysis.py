import re
import sys
from datetime import datetime, timedelta
from datetime import date
import time
# from memory_profiler import profile
import tracemalloc
from line_profiler import LineProfiler
import cProfile
import ts



class port():   

    def port_helth_check(self, port_id):
       
        self.temp_str = get_output_of_CliCmd("show port " + port_id + " detail")
        
        if self.temp_str!=None:
            matches_1 = re.findall(r"(Admin State)\s+:\s+(\S+)(.*)\s+(Oper State)\s+:\s+(\S+)", self.temp_str, re.MULTILINE)

            if matches_1[0][1]=='up' and matches_1[0][4]=='up':
                print_delay('Port {port} is operationally up.\n'.format(port=port_id))
                self.sfp_ddm_validation(port_id)
                
            elif matches_1[0][1]=='up' and matches_1[0][4]=='down':
                    print_delay('\nPort {port} is admin up but operationally down.\n'.format(port=port_id))

                    sfp_info = re.findall(r"(Transceiver Status)\s+:\s+((not-equipped)|(operational)|(unsupported))", self.temp_str)                    
                    if sfp_info[0][1]=='not-equipped':
                        print_delay('Port {port} is not equipped with SFP.\n'.format(port=port_id))
                       
                    elif sfp_info[0][1]=='unsupported':
                            print_delay('Port {port} shows "transceiver status" as {unsupported} SFP.\n'.format(port=port_id, unsupported=sfp_info[0][1]))
                            self.sfp_ddm_validation(port_id)                        
                    else:
                        self.sfp_ddm_validation(port_id)

            else:
                    print_delay('Port {port} is admin down.\n'.format(port=port_id))
        
        else:
            print_delay('Port {port} does not exist on this device.\n'.format(port=port_id))


    def sfp_ddm_validation(self, port_id):
        regex = r"(Temperature|Supply Voltage|Tx Bias Current|Tx Output Power|Rx Optical Power)\s+\(.*\)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)"
        matches1 = re.finditer(regex, self.temp_str, re.MULTILINE)
        for matchNum, match in enumerate(matches1, start=1):
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                if '!' in match.group(groupNum):
                    matches2 = re.findall(r"(.*)(Value High Alarm\s+High Warn\s+Low Warn\s+Low Alarm)", self.temp_str)
                    print('\n{OOR} out of range\n'.format(OOR=match.group(1)))
                    print(matches2[0][0],matches2[0][1])
                    print(match.group(),'\n')
                    break
                
        matches3 = re.findall(r"(Model Number|Vendor OUI|Serial Number|Part Number)\s+: (.*)", self.temp_str)
        if len(matches3)!=0:
            if '3HE' in matches3[3][1]:
                print_delay('SFP used on port {port} is unsupported SFP.\n'.format(port=port_id))
            elif '3HE' in matches3[0][1]:
                print_delay('SFP used on port {port} has Model Number starting wih 3HE. To further validate the SFP supportability please refer latest optical reference guide available at the below mentioned sharepoint location.\n https://nokia.sharepoint.com/sites/emea-ion-tech/SitePages/Home.aspx'.format(port=port_id))
            else:
                print_delay('SFP used on this port {port} is a unsupported SFP.\n'.format(port=port_id))




    def validate_port(self,port_id):
        # ([\d]+/[\d]+/[\d]+)                     # 1/1/1
        # ([\d]+/[\d]+/c[\d]+)                    # 1/1/c1
        # ([\d]+/[\d]+/c[\d]+/(\d\d|\d))          # 1/1/c1/1
        # ([\d]+/x[\d]+/[\d]+/c[\d]+)             # 1/x1/1/c1
        # ([\d]+/x[\d]+/[\d]+/c[\d]+/(\d\d|\d))   # 1/x1/1/c1/1
        # (esat-[/\d+]/[/\d+]/[/\d+]+)            # esat-1/1/1
        # (esat-[/\d+]/[/\d+]/c[/\d+]/u[/\d+]))   # esat-1/1/c65/u1
        
        reg = r"(([\d]+/[\d]+/[\d]+)|([\d]+/[\d]+/c[\d]+)|([\d]+/[\d]+/c[\d]+/(\d\d|\d))|([\d]+/x[\d]+/[\d]+/c[\d]+)|([\d]+/x[\d]+/[\d]+/c[\d]+/(\d\d|\d))|esat-[/\d+]/[/\d+]/[/\d+]+|esat-[/\d+]/[/\d+]/c[/\d+]/u[/\d+])"
        match = re.fullmatch(reg, port_id)
        if match:
            return True
        else:
            print_delay('Port {port} id is not valid port ID.\n'.format(port = port_id))
            return False


    def dump_port_details(self, search_port):
        search_str = "show port " + search_port + " detail"
        if self.validate_port(search_port):
            temp_str = self.get_output_of_CliCmd(search_str)
            if temp_str != None:
                print(temp_str)
            else:
                self.print_delay("Search port doesn't exist.")
        else:
            exit
         

    def dump_sfp_info(self, search_port):
        s1 = 'Transceiver Data'
        s2 = 'Link Length support'
        if self.validate_port(search_port):
            search_str = "show port " + search_port + " detail"
            temp_str = get_output_of_CliCmd(search_str)
            
            if temp_str != None:
                match_str = re.finditer(r"(Transceiver Status)\s+:\s+(not-equipped)|(Transceiver Status)\s+:\s+(unsupported)|(Transceiver Status)\s+:\s+(operational)", temp_str)
                
                for matchNum, match1 in enumerate(match_str, start=1):
                    ts1 = match1.group(2)
                    ts2 = match1.group(4)

                    if ts1 != 'not-equipped':
                        temp_output = ''
                        str_idx_1 = temp_str.index(s1)
                        str_idx_2 = temp_str.index(s2,str_idx_1)
                        # print(temp_str[str_idx_1:str_idx_2+38])
                        if ts2 == 'unsupported':
                            print_delay('Info: {port} is equipped with unsupported SFP.'.format(port=search_port))  
                                
                        for string1 in temp_str[str_idx_1:str_idx_2+38]:
                            temp_output += string1
                        return temp_output                    
                    else:
                        print_delay('Info: {port} is not equipped with SFP.'.format(port=search_port))          
                    exit
            else:
                print_delay("Info: Search {port} doesn't exist.".format(port=search_port))
        else:
            exit   
                             
  
    def dump_ddm_info(self,search_port):
        s1 = 'Transceiver Digital Diagnostic Monitoring (DDM)'
        s2 = 'Rx Optical Power'

        temp_output = ''

        
        if self.validate_port(search_port):
            search_str = "show port " + search_port + " detail"
            temp_str = get_output_of_CliCmd(search_str)

            if temp_str:
                match_str = re.findall(r"(Transceiver Status)\s+:\s+(not-equipped)", temp_str)

                reg = r"([\d]+/[\d]+/c[\d]+/(\d\d|\d))|([\d]+/x[\d]+/[\d]+/c[\d]+/(\d\d|\d))|(esat-[/\d+]/[/\d+]/c[/\d+]/u[/\d+])"
                matches = re.fullmatch(reg, search_port)

                if matches:
                    print_delay('Port {port} is a breakout port. Check corresponding connector port for DDM info.\n'.format(port=search_port))
                    return

                if len(match_str)==0:         

                    if 'copper' in temp_str[100:]:

                        print_delay('The {port} is equipped with copper SFP. DDM information is not available for ports equiped with copper SFP.\n'.format(port=search_port))
                    else:
                        str_idx_1 = temp_str.index(s1)

                        try:
                            str_idx_2 = temp_str.index(s2,str_idx_1)
                            # print(temp_str[str_idx_1-2:str_idx_2+164])
                            for string1 in temp_str[str_idx_1-2:str_idx_2+164]:
                                temp_output += string1
                        except ValueError as ex:
                            pass
                            # print(temp_str[str_idx_1-2:-1])
                            for string2 in temp_str[str_idx_1-2:-1]:
                                temp_output += string2                            
                        return temp_output                        
                else:
                    print_delay('Port {port} is not equipped with SFP.\n'.format(port=search_port))    
            else:
                print_delay("Port {port} doesn't exist.\n".format(port=search_port))
        else:
            exit


    def port_queue_drops(self, port_id):
        # breakpoint()
        if (self.validate_port(port_id)):
            if ((re.fullmatch(r"([\d]+/[\d]+/c[\d]+)|([\d]+/x[\d]+/[\d]+/c[\d]+)", port_id)) != None):    
                # print('Port {port} is a connector port.'.format(port = port_id))
                return None
        
            # test_str = self.get_output_of_CliCmd("show port " + port_id + " detail")
            test_str1 = TS_1.get_output_of_CliCmd("show port " + port_id + " detail")
            test_str2 = TS_2.get_output_of_CliCmd("show port " + port_id + " detail")
            match_str1 = re.findall(r"(Transceiver Status)\s+:\s+(not-equipped)", test_str1)
            match_str2 = re.findall(r"(Transceiver Status)\s+:\s+(not-equipped)", test_str2)
            
            if len(match_str1)!=0 and len(match_str2)!=0:
                # print('Port {port} is not equipped with SFP.'.format(port = port_id))
                return None
            
            if (test_str1 != '') | (test_str2 != ''):        
                matches1 = re.findall(r"Configured Mode\s+:\s+((access)|(network)|(hybrid))", test_str1)
                matches2 = re.findall(r"Configured Mode\s+:\s+((access)|(network)|(hybrid))", test_str2)
            
                if (matches1[0][0]=='access'):
                    # print('Port {port} is a access port. Check queues on SAP level.'.format(port = port_id))
                    return None
                
                regex = r"((Ingress Queue\s+\d+)\s+(Packets)\s+(Octets)(\n\s+)(In Profile forwarded  :)\s+(\d+)\s+(\d+)(\n\s+)(In Profile dropped    :)\s+(\d+)\s+(\d+)(\n\s+)(Out Profile forwarded :)\s+(\d+)\s+(\d+)(\n\s+)(Out Profile dropped   :)\s+(\d+)\s+(\d+))|((Egress Queue\s+\d+)\s+(Packets)\s+(Octets)(\n\s+)(In/Inplus Prof fwded  :)\s+(\d+)\s+(\d+)(\n\s+)(In/Inplus Prof dropped:)\s+(\d+)\s+(\d+)(\n\s+)(Out/Exc Prof fwded    :)\s+(\d+)\s+(\d+)(\n\s+)(Out/Exc Prof dropped  :)\s+(\d+)\s+(\d+))"
                matches1 = re.finditer(regex, test_str1, re.MULTILINE)
                matches2 = re.finditer(regex, test_str2, re.MULTILINE)
                matches3 = re.finditer(regex, test_str2, re.MULTILINE)
                count1, count2, count3, count4 = 0, 0, 0, 0
            
                for matchNum1, match1 in enumerate(matches1, start=1):
                    count2 = 0
                    
                    if (match1.group(11) != None) | (match1.group(19) != None):
            
                        if (int(match1.group(11)) != 0) | (int(match1.group(19)) != 0):
                            if count3 == 0:
                                print('='*60, "\nPort {port} has drops on Ingress Queue's.".format(port = port_id))
            
                            for matchNum2, match2 in enumerate(matches2, start=1):
                                if (match2.group(11) != None) | (match2.group(19) != None):
                                    if (int(match2.group(11)) != 0) | (int(match2.group(19)) != 0):
                                        print('\n>>',match1.group(2))
                                        if (int(match2.group(11)) > int(match1.group(11))):
                                            print('->In Profile Drops reported and are incrementing between TS file. <----')
                                            total_drops = int(match2.group(11)) - int(match1.group(11))
                                            print(TS_Path_1,'->', match1.group(10),match1.group(11))
                                            print(TS_Path_2,'->', match2.group(10),match2.group(11))                                                
                                            print('Total of {total_drops} packets dropped in time interval of {total_sec} seconds.\n'.format(total_drops=total_drops, total_sec=total_sec))
                                        else:
                                            print('->In Profile Drops reported and are not incrementing between TS file.')
                                        if (int(match2.group(19)) > int(match1.group(19))):
                                            print('->Out Profile Drops reported and are incrementing between TS file. <----')
                                            total_drops = int(match2.group(19)) - int(match1.group(19))
                                            print(TS_Path_1,'->', match1.group(18),match1.group(19))
                                            print(TS_Path_2,'->', match2.group(18),match2.group(19))
                                            print('Total of {total_drops} packets dropped in time interval of {total_sec} seconds.\n'.format(total_drops=total_drops, total_sec=total_sec))                                        
                                        else:
                                            print('->Out Profile Drops reported and are not incrementing between TS file.')
                                        break
                            count3 += 1
                        else:
                            count1 += 1
                    elif (match1.group(31) != None) | (match1.group(39) != None):
                        if (int(match1.group(31)) != 0) | (int(match1.group(39)) != 0):
                            if count4 == 0:
                                print('-'*60, "\nPort {port} has drops on Egress Queue's.".format(port = port_id))
                            for matchNum3, match3 in enumerate(matches3, start=1):
                                if (match3.group(31) != None) | (match3.group(39) != None):
                                    if (int(match3.group(31)) != 0) | (int(match3.group(39)) != 0):
                                        print('\n->',match1.group(22))
                                        if (int(match3.group(31)) > int(match1.group(31))):
                                            print('->In Profile Drops reported and are incrementing between TS file. <----')
                                            total_drops = int(match3.group(31)) - int(match1.group(31))
                                            print(TS_Path_1,'->', match1.group(30),match1.group(31))
                                            print(TS_Path_2,'->', match3.group(30),match3.group(31))                                                
                                            print('Total of {total_drops} packets dropped in time interval of {total_sec} seconds.\n'.format(total_drops=total_drops, total_sec=total_sec))
                                        else:
                                            print('->In Profile Drops reported and are not incrementing between TS file.')
                                        if (int(match3.group(39)) > int(match1.group(39))):                                                
                                            print('->Out Profile Drops reported and are incrementing between TS file. <----')
                                            total_drops = int(match3.group(39)) - int(match1.group(39))
                                            print(TS_Path_1,'->', match1.group(38),match1.group(39))
                                            print(TS_Path_2,'->', match3.group(38),match3.group(39))
                                            print('Total of {total_drops} packets dropped in time interval of {total_sec} seconds.\n'.format(total_drops=total_drops, total_sec=total_sec))
                                        else:
                                            print('->Out Profile Drops reported and are not incrementing between TS file.')
                                        break 
                            count4 += 1      
                        else:
                            count1 += 1                 
                #     count2 = matchNum1
                # if count1 == count2:
                #     print('Port {port} is clear with queue drops.'.format(port = port_id))
                #     exit
            else:
                print("Port {port} doesn't exist.".format(port = port_id))        


    def traffic_rate_per_port(total_sec):
        print('Note: Rate is calculated using collective time difference between two TS files.')
        test_str1 = TS_1.get_output_of_CliCmd("show port statistics")
        test_str2 = TS_2.get_output_of_CliCmd("show port statistics")

        regex = r"([/\d]/[/\d]/[/\d]+|[/\d]/[/\d]/c[/\d]+/[/\d]+|esat-[/\d]/[/\d]/[/\d]+|esat-[/\d]/[/\d]/c[/\d]+/u[/\d]+)+(\s+)+(\d+)+(\s+)+(\d+)+(\s+)+(\d+)+(\s+)+(\d+)"
        matches1 = re.finditer(regex, test_str1, re.MULTILINE)
        matches2 = re.finditer(regex, test_str2, re.MULTILINE)

        print('='*60)
        for matchNum, match1 in enumerate(matches1, start=1):
            port_1 = match1.group(1)

            for matchNum, match2 in enumerate(matches2, start=1):
                port_2 = match2.group(1)
                if port_1 == port_2:
                    InPacketsRate = (int(match2.group(3)) - int(match1.group(3)))/total_sec
                    # InOctateRate = (int(match2.group(5)) - int(match1.group(5)))/total_sec
                    OutPacketsRate = (int(match2.group(7)) - int(match1.group(7)))/total_sec
                    # OutOctateRate = (int(match2.group(9)) - int(match1.group(9)))/total_sec
                    print('Port: {port}\n Ingress Packets rate(pps): {InPacketsRate} \n Egress Packet rate(pps): {OutPacketsRate}'.format(port=port_1, InPacketsRate=int(InPacketsRate), OutPacketsRate=int(OutPacketsRate)))
                    print('-'*60)
                    break
                break
        matches1, matches2 = "", ""
        return None





def print_delay(print_str):
    for char in print_str:
        print(char, end='', flush=True)
        time.sleep(0.001)

        
def get_output_of_CliCmd(search_str):
    # pattern_1 = "CLI Command: '" + search_str + "'\n"
    pattern_1 = "cli command: '" + search_str + "'\n"
    pattern_2 = r"\w+ \w+ \d+ \d{2}:\d{2}:\d{2} \d{4} \w+:"
    temp_output = ''
    try:
        # li = TS_1.master_tuple.index(pattern_1)
        li = TS_1.master_dict.get(pattern_1)
        
        if li:
            for each_line in TS_1.master_tuple[li::]:
                matches = re.findall(pattern_2, each_line)
                if matches:
                    break
                else:
                    temp_output += each_line     
            return temp_output
    except ValueError as ex:
        # print_delay('Searched command does not exist or not a valid command.\n')
        return
        

def get_output_of_ShellCmd(search_str):
    pattern_1 = "local shell command: '" + search_str.lower() + "'\n"
    pattern_2 = r"(\S+): ==> shell command on (slot|XIOM|mda) (\S+): '(\S+)'"      
    pattern_3 = r"\w+ \w+ \d+ \d{2}:\d{2}:\d{2} \d{4} \w+:"
  
    temp_output = ''
    li1 = TS_1.master_dict.get(pattern_1)
    if li1:
        temp_output += "====== '"+search_str+"' shell output from active CPM ======\n"
        for each_line1 in TS_1.master_tuple[li1::]:
            matches = re.findall(pattern_3, each_line1)
            if matches:
                break
            else:
                temp_output += each_line1

    for each_line2 in TS_1.master_dict:
        matches_1 = re.findall(pattern_2, each_line2)
        if matches_1 and (matches_1[0][3].lower()==search_str.lower()):
            if (matches_1[0][0] == 'a')|(matches_1[0][0] == 'b'):    
                temp_output += "====== '"+matches_1[0][3]+"' shell output from standby CPM "+matches_1[0][2].upper()+' ======\n'
            elif (matches_1[0][1] == 'slot')|(matches_1[0][1] == 'XIOM'):
                temp_output += "====== '"+matches_1[0][3]+"' shell output from "+matches_1[0][1]+' '+matches_1[0][2]+' ======\n'
            else:
                temp_output += "====== '"+matches_1[0][3]+"' shell output from "+matches_1[0][1]+' '+matches_1[0][2]+' ======\n'
                
            li2 = TS_1.master_dict.get(each_line2.lower())
            for each_line3 in TS_1.master_tuple[li2::]:
                matches_2 = re.findall(pattern_3, each_line3)
                if matches_2:
                    temp_output += '\n'
                    break
                else:
                    temp_output += each_line3
    if temp_output == '':
        print_delay("'{cmd}' doesnt not exist or is not a shell valid command.".format(cmd=search_str))

    return temp_output

# Function to calculate time difference between two TS files.        
def time_dif():
    
    pattern = r"\w+ \w+ \d+ \d{2}:\d{2}:\d{2} \d{4} \w+" # Regular expression to extract date and time from the give string.
    matches_1 = re.findall(pattern, TS_1.master_tuple[0])
    matches_2 = re.findall(pattern, TS_2.master_tuple[0])
    if matches_1:
        # Convert the timestamps to datetime objects
        datetime_str1 = matches_1[0]
        if matches_2:
            # Convert the timestamps to datetime objects
            datetime_str2 = matches_2[0]
            # Format string for parsing the timestamp
            format_string_1 = "%a %b %d %H:%M:%S %Y %Z"
            TS1_datetime = datetime.strptime(datetime_str1, format_string_1)
            TS2_datetime = datetime.strptime(datetime_str2, format_string_1)
            # Calculate the time difference
            time_difference = TS2_datetime - TS1_datetime
            # print("First TS file collected on ", TS1_datetime)
            # print("Second TS file collected on ", TS2_datetime)
            print("Time difference between two TS files: ", time_difference,'\n')
            dt = timedelta(days=0, hours=0, minutes=15)
            if time_difference < dt:
                print("Time difference between two TS files is less that 15min.\n")
            total_sec = int(time_difference.total_seconds())
            
    if (TS_1.chassis_mac_addr == TS_2.chassis_mac_addr) & (TS_1.sys_name == TS_2.sys_name):
        # print("Both TS files belongs to same node..!\n")
        print("Device details:") 
        print('-'*49)
        print('System Name         : ', TS_1.sys_name)
        print('System Type         : ', TS_1.sys_type)
        print('System Version      : ', TS_1.sys_version)
        print('Chassis MAC address : ', TS_1.chassis_mac_addr)
        print('-'*50,'\n')
    elif (TS_1.chassis_mac_addr != TS_2.chassis_mac_addr) & (TS_1.sys_name == TS_2.sys_name):
        print("Both TS file have the same name. But chassis MAC address does not match..!\n")
        print('Device details:')
        print('-'*49)
        print('Chassis MAC address of TS file ', TS_Path_1, 'is >>', TS_1.chassis_mac_addr)        
        print('Chassis MAC address of TS file ', TS_Path_2, 'is >>', TS_2.chassis_mac_addr)  
        print('-'*50,'\n')
    else:
        print("Both TS files belongs to different nodes..!")
        
    return total_sec    

           

# Main program starts..!
if __name__ == '__main__':

    current_time = time.ctime()
    print("Today's date and time is",current_time)

    # TS_Path_1 = 'Database/ESA_TS_File_1.txt'
    # TS_Path_2 = 'Database/ESA_TS_File_2.txt'
    TS_Path_1 = 'Database/SR_TS_File_1.txt'
    TS_Path_2 = 'Database/SR_TS_File_2.txt'
    # TS_Path_1 = 'Database/Satellite_TS_File_1.txt'
    # TS_Path_2 = 'Database/Satellite_TS_File_2.txt'
    # TS_Path_1 = 'Database/Port_info.txt'

    TS_1 = ts.TsFile(TS_Path_1)
    TS_2 = ts.TsFile(TS_Path_2)

    port = port()

    while True:
        input1 = input('\nEnter port number: ')
        if input1:
            port.port_helth_check(input1)
        else:
            break


    total_sec = time_dif() # Check time difference between two TS files.
    # total_sec = cProfile.run('time_dif()')
    # traffic_rate_per_port(total_sec)
    # cProfile.run('traffic_rate_per_port(total_sec)')

    # Python provides a built-in module to measure execution time and the module name is LineProfiler.It gives a detailed report on the time consumed by a program.
    # profile = LineProfiler(traffic_rate_per_port(total_sec))
    # profile.print_stats()


