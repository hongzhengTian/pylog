from IPinforms import *
import jinja2
import numpy as np
import math 

def analyze_ip_configuration(node):
    ip_config = {}
    if (len(node.func_configs)!=len(Global_IP_func_configs[node.name])):
        print('The number of func_configs is incorrect!')
        raise NameError

    for i in node.func_configs:
        if i in Global_IP_func_configs[node.name]:
            ip_config[i] = node.func_configs[i]
        else:
            print(f'func_configs {i} should not appear!')
            raise NameError

    ip_name = analyze_ip_versions(node)
    for i in Global_IP_optm_configs_Default[ip_name]:
        if i in node.optm_configs:
            ip_config[i] = node.optm_configs[i]
        else:
            ip_config[i] = Global_IP_optm_configs_Default[ip_name][i]
    '''
    if (node.name == "argmax") or (node.name == "max") or(node.name=="min"):        
        if ('version' not in node.optm_configs) or \
           (node.optm_configs['version'] == 0):
            print("if branch ahs been executed")
            log2_kernel_size = int(np.log2(ip_config['s0']))
            ip_config['log2_kernel_size'] = log2_kernel_size
########add
            ip_config['kernel_size'] = int(np.log2(log2_kernel_size))
            #ip_config['II']  = int(ip_config['s0']) / int(kernel_size)
            ip_config['SIZE_']=2
            ip_config['BATCH_']=2
            ip_config['STAGE'] = 4

        else:
            print("else branch has been executed")
            kernel_size = ip_config['kernel_size']
            ip_config['log2_kernel_size'] = int(np.log2(kernel_size))
            ip_config['II']  = int(ip_config['s0']) / int(kernel_size)
    print(ip_config)
    '''
    if node.name == "argmax" or node.name == "argmin":
        if ('version' not in node.optm_configs) or \
           (node.optm_configs['version'] == 0):
            log2_kernel_size = math.ceil(np.log2(tupToInt(ip_config['s0'])))
            ip_config['log2_kernel_size'] = log2_kernel_size
            #print("log2_kernal_size = ", log2_kernel_size)
            index_temp=[]
            len_of_layer = tupToInt(ip_config['s0'])
            for i in range (1, log2_kernel_size+1):
                if(len_of_layer%2 ==0):
                    index_temp.append(len_of_layer//2)
                    len_of_layer = len_of_layer//2
                else:
                    index_temp.append(len_of_layer//2+1)
                    len_of_layer=len_of_layer//2+1
            ip_config['index_temp'] = index_temp
            #print("jiaweiIPcheck Yes")                                                                              
            #print(ip_config)
            
        else:
            kernel_size = ip_config['kernel_size']
            ip_config['log2_kernel_size'] = int(math.ceil(np.log2(kernel_size)))
            ip_config['II']  = int(ip_config['s0']) / int(kernel_size)
            ip_config['self_define'] = 123321
            #print("jiaweiIPcheck")
            #print(ip_config)
    
    if node.name == "max" or node.name =="min":
        #since we only exist argmax pipeline method, so dont need to detect if it is in Global_IP_versions
        log2_kernel_size = int((np.log2(ip_config['s0'])))
        ip_config['SIZE'] = tupToInt(ip_config['s0'])
        ip_config['BATCH'] = 4
        ip_config['ITERATION'] = math.ceil(tupToInt(ip_config['s0'])/ip_config['BATCH'])
    
    return ip_config


def analyze_ip_versions(node):
    ip_name = node.name
    if (node.name in Global_IP_versions):
        if 'version' in node.optm_configs:
            version_idx = node.optm_configs['version']
            ip_name = Global_IP_versions[node.name][version_idx]
        else:
            ip_name = Global_IP_versions[node.name][0]
    return ip_name


def ip_generator(node, project_path, recordip):

    ip_name = analyze_ip_versions(node)
    ip_config = analyze_ip_configuration(node)
    '''print("debug IPanalysis!")
    print(node.func_configs)
    print(node.func_configs['s0'][0])
    ip_config['s0'] = tupToInt(node.func_configs['s0'])
    ip_config['s1'] = tupToInt(node.func_configs['s2'])
    ip_config['s2'] = tupToInt(node.func_configs['s2'])
    
    print(node.func_configs)
    print(ip_config)
    '''
    
    
    if node.name !="matmul":
        templetShapeTransformer(ip_config, node)
    #debug!
    
    
    
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    file_path = Global_IP_file_path[ip_name]
    template_cpp = templateEnv.get_template(file_path+'.cpp.jinja')
    template_h = templateEnv.get_template(file_path+'.h.jinja')

    ip_config['recordip'] = recordip
    func_name = f'{ip_name}_{recordip}'
    ip_config['top_name'] = func_name
    cppoutputText = template_cpp.render(ip_config)
    houtputText = template_h.render(ip_config)
    f_h = open(f'{project_path}/{func_name}.h','w')
    f_cpp = open(f'{project_path}/{func_name}.cpp','w')
    f_h.write(houtputText)
    f_cpp.write(cppoutputText)

    file_h= project_path+"/configured_IPcores.h"
    include_str = f'#include "{func_name}.h"\n'
    if recordip == 0:
        f = open(file_h,'w')
        f.close()
    f=open(file_h, "a+")
    f.writelines(include_str)

    f.close()
    f_h.close()
    f_cpp.close()

def tupToInt(thistuple):
    res=""
    for i in thistuple:
        res+=str(i)
    res=int(res)
    return res

def templetShapeTransformer(ip_config, node):
    keylist = {'s0', 's1', 's2', 's3', 's4', 's5'}
    for i in keylist:
        if i in ip_config.keys():
            ip_config[i] = tupToInt(node.func_configs[i])
