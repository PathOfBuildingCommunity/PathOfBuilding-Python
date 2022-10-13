#!/usr/bin/python3.10

import base64
import re
import hashlib

t1 = "https://www.pathofexile.com/fullscreen-passive-skill-tree/AAAABgMCBhslS65tGdlb34rpAgAA"
t2 = "https://www.pathofexile.com/passive-skill-tree/3.19.0/AAAABgMCE-kCI3udBFSuFvPyHhslv5fZWyY8fdIvnWwLbRnfiiL0S67JPZMnAALvYyN7vOadBA=="
# with cluster info
t3 = "https://www.pathofexile.com/passive-skill-tree/3.18.0/AAAABgMCIJ0EVK7o1hbz34ptGS-dbAvjhFsmyT1tbOkCI3si9FBCGo3yHud0GyUbyNlbf_t90g5IUzW_lyY8Nj1LrgW1kycHASMBKQErASoBIAEiASECvOadBO9jI3s="
t4 = "https://www.pathofexile.com/fullscreen-passive-skill-tree/AAAABgMAJwDwBAcQWBEPFLAdgx8CH8creCycLX0vXTBbMjQ2iTbFOlhEq0wtVa5VxlZIakN2EX6vghCD24-mrJesmLWFvOrBtNgk37Dk7OXA71D06QAD-vEA8LoaL13HMeXA?accountName=xyllywyt&characterName=XyllyWitchy"
# Mira_sentinal. masteryEffects="{33657,19422},{11505,6216},{41415,47642},{2828,11521},{44298,48385},{64406,59936},{32241,38454}"
t5 = "https://www.pathofexile.com/passive-skill-tree/3.19.0/AAAABgUBaeS82WGbIR0UFm_sOFnzdl73MqIAhnfEpNeWpwiFe6EjFy_vIVFgwGaApNgkPfxxeZx7v7iEgzD4ggfwH7v2jM9fP3GFOpHvDj0PBLMClvnd9kgGOYx2eWhoZY9Gdqxo8icvcqmAMPuqM2xXDYN5WGO3MeNq34ZmnizxGjiCm57NFCCbbny7rv862GTnCwxoWAirZlStCup_ocexHVXW-tKLjBccvrYSacEEkFXPftJ8PAX7lqyJ2rmsqn3x8kFlcq2N0iEpi_ObidjvfO1h6hjmfQcAqgCgAKIEhASABJMEkAdL3oN5GEgs8S0BCwy9Aa0Kuhqhx-og-5aWNn3x"
# Ziz Level 30 masteryEffects="{12125,47642},{240,64241}" 
t6 = "https://www.pathofexile.com/passive-skill-tree/AAAABgMCJBBYRKtVrjBb2CSsl6yYvOpqQyt4g9t2Ed-wL13k7I-mVcYsnC19HwIEB36vaZ6CEB2DAPA2xbWFH8fvUFZIMjQRD8G0OljmdgACuhovXfrxAPA="

tests = [t1, t2, t3, t4, t5, t6]

for test in tests:
    nodes = []
    cluster_nodes = []
    mastery_nodes = {}

    m = re.search(r"http.*passive-skill-tree/(.*/)?(.*)", test)
    # print(m)

    #group(1) is None or a version
    #group(2) is always the encoded string
    if m is not None:
        # print(m.group(1), m.group(2))
        output = m.group(2).split("?")
        # print(type(output), output)
        tree_version = m.group(1)
        encoded_str = output[0]
        del output[0]
        variables = output  # a list of variable=value or an empty list
        # print(type(variables), variables)
        decoded_str = base64.b64decode(encoded_str, "-_")
        # print(f"decoded_str: {len(decoded_str)},", "".join('{:02x} '.format(x) for x in decoded_str))
        string = " ".join('{:02x}'.format(x) for x in decoded_str)
        # print(string)
        print(hashlib.md5(string.encode('utf-8')).hexdigest())

        #the decoded_str is 0 based, so every index will be one smaller than the equivalent in lua
        if decoded_str and len(decoded_str) > 7:
            # print("Valid")
            # print("")

            version = int.from_bytes(decoded_str[0:4], "big")
            # print("version", version)
            # print("")

            class_id = decoded_str[4]
            ascend_id = version >= 4 and decoded_str[5] or 0
            # print("class_id, ascend_id", class_id, ascend_id)
            # print("")

            nodes_start = version >=4 and 7 or 6
            nodes_end = version >=5 and 7 + (decoded_str[6] * 2) or -1
            # print("nodes_start, end", nodes_start, nodes_end)
            decoded_nodes = decoded_str[nodes_start: nodes_end]
            # print(f"decoded_nodes: {len(decoded_nodes)},", "".join('{:02x} '.format(x) for x in decoded_nodes))
            # print("")

            # now decode the nodes structure to numbers
            for i in range(0, len(decoded_nodes), 2):
                # print(i, " ".join('{:02x}'.format(x) for x in decoded_nodes[i:i+2]), int.from_bytes(decoded_nodes[i:i+2], "big"))
                nodes.append(int.from_bytes(decoded_nodes[i:i+2], "big"))


            if version < 5:
                print("exiting as version is less than 5")
                return

            cluster_count = decoded_str[nodes_end]
            cluster_start = nodes_end + 1
            cluster_end = cluster_count == 0 and cluster_start or cluster_start + (cluster_count * 2)
            # print("cluster_start, end", cluster_start, cluster_end, cluster_count)
            if cluster_count > 0:
                decoded_cluster_nodes = decoded_str[cluster_start:cluster_end]
                # print(f"decoded_cluster_nodes: {len(decoded_cluster_nodes)},", ''.join('{:02x} '.format(x) for x in decoded_cluster_nodes))
                # now decode the cluster nodes structure to numbers
                for idx in range(0, len(decoded_cluster_nodes), 2):
                    # print(''.join('{:02x} '.format(x) for x in decoded_cluster_nodes[idx:idx+2]))
                    # print(idx, int.from_bytes(decoded_cluster_nodes[idx:idx+2], "big")+ 65536)
                    # print(int.from_bytes(decoded_cluster_nodes[idx:idx+2], "big"))
                    cluster_nodes.append(int.from_bytes(decoded_cluster_nodes[idx:idx+2], "big")+ 65536)
            # print("")
            mastery_count = decoded_str[cluster_end]
            if mastery_count > 0:
                mastery_start = cluster_end + 1
                mastery_end = mastery_count == 0 and mastery_start or mastery_start + (mastery_count * 4)
                # print("mastery_start, end", mastery_start, mastery_end, mastery_count)
     
                decoded_mastery_nodes = decoded_str[mastery_start:mastery_end]
                # print(f"decoded_mastery_nodes: {len(decoded_mastery_nodes)},", ''.join('{:02x} '.format(x) for x in decoded_mastery_nodes))
                # now decode the mastery nodes structure to numbers
                for idx in range(0, len(decoded_mastery_nodes), 4):
                    # print(''.join('{:02x} '.format(x) for x in decoded_mastery_nodes[idx:idx+4]))
                    # print(idx, int.from_bytes(decoded_mastery_nodes[idx:idx+2], "big"))
                    id = int.from_bytes(decoded_mastery_nodes[idx+2:idx+4], "big")
                    effect = int.from_bytes(decoded_mastery_nodes[idx:idx+2], "big")
                    # print(id, effect)
                    mastery_nodes[id] = effect

    #####################################################################################################
    # encode
    #####################################################################################################

    # remember cluster nodes are suppose to be part of active_nodes. 
    # id >= 65536 then
        # local clusterId = id - 65536

    byte_stream=[]
    byte_stream.extend(version.to_bytes(4, "big"))
    byte_stream.append(class_id)
    byte_stream.append(ascend_id)
    # print(''.join('{:02x} '.format(x) for x in byte_stream))

    byte_stream.append(len(nodes))
    for node in nodes:
        byte_stream.extend(node.to_bytes(2, "big"))
    # print(''.join('{:02x} '.format(x) for x in byte_stream))

    byte_stream.append(len(cluster_nodes))
    for cluster_node in cluster_nodes:
        cluster_node -= 65536
        byte_stream.extend(cluster_node.to_bytes(2, "big"))
    # print(''.join('{:02x} '.format(x) for x in byte_stream))

    byte_stream.append(len(mastery_nodes))
    for mastery_node in mastery_nodes:
        byte_stream.extend(mastery_nodes[mastery_node].to_bytes(2, "big"))
        byte_stream.extend(mastery_node.to_bytes(2, "big"))
    string = " ".join('{:02x}'.format(x) for x in byte_stream)
    # print(string)
    print(hashlib.md5(string.encode('utf-8')).hexdigest())
    print("")


