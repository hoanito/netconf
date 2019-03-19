import sys
from argparse import ArgumentParser
from ncclient import manager
from xml.dom import minidom
from prettytable import PrettyTable

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    parser = ArgumentParser(description='Select options.')
    # Input parameters
    parser.add_argument('--host', type=str, required=True,
                        help="Device IP or DN")
    parser.add_argument('-u', '--username', type=str, default='cisco',
                        help="Your GF's name")
    parser.add_argument('-p', '--password', type=str, default='cisco',
                        help="Her birthday")
    parser.add_argument('--port', type=int, default=830,
                        help="Specify this if you want a non-default port")
    args = parser.parse_args()

    with manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password,
                         device_params={'name':"iosxe"}
                          ) as cisco_manager:

        getAll(cisco_manager)


def getAll (cisco_manager):
    ACL_name_filter = '''
                  <filter>
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                    </native>                        
                  </filter>
                      '''

    rawOutput = cisco_manager.get_config('running', ACL_name_filter)
    # Pretty print XML string
    XMLBeautifier(rawOutput)

def getInterfaceSP (cisco_manager, PMname):
    """
    # Filter for IOS > 16.6
    ACL_name_filter = '''
                      <filter>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <interface></interface>
                        </native>
                      </filter>
                      '''
    """
    ACL_name_filter = '''
                      <filter>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <interface></interface>
                        </native>                        
                      </filter>
                      '''
    rawOutput = cisco_manager.get_config('running', ACL_name_filter)
    XMLOutput = minidom.parseString(rawOutput.xml)
    GigInterfaces = XMLOutput.getElementsByTagName("GigabitEthernet")
    for interface in GigInterfaces:
        servicePolicies = interface.getElementsByTagName("service-policy")
        if servicePolicies.length > 0:
            inputServicePolicy = servicePolicies[0].getElementsByTagName("input")
            if inputServicePolicy.length > 0:
                if inputServicePolicy[0].firstChild.nodeValue == PMname:
                    print("\t\tApplied to:\n\t\t\tGigabitEthernet%s [input]"%interface.firstChild.firstChild.nodeValue)

            outputServicePolicy = servicePolicies[0].getElementsByTagName("output")
            if outputServicePolicy.length > 0:
                if outputServicePolicy[0].firstChild.nodeValue == PMname:
                    print("\t\tApplied to:\n\t\t\tGigabitEthernet%s [output]"%interface.firstChild.firstChild.nodeValue)


def getPM(cisco_manager):
    """
    # Filter for IOS > 16.6
    ACL_name_filter = '''
                  <filter>
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <policy><policy-map xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-policy"></policy-map></policy>
                    </native>
                  </filter>
                      '''
    """
    ACL_name_filter = '''
                  <filter>
                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                        <policy-map></policy-map>
                    </native>                        
                  </filter>
                  '''

    rawOutput = cisco_manager.get_config('running', ACL_name_filter)
    XMLOutput = minidom.parseString(rawOutput.xml)
    policyMaps = XMLOutput.getElementsByTagName("policy-map")
    for pm in policyMaps:
        classes = pm.getElementsByTagName("class")
        PM_name =  pm.firstChild.firstChild.nodeValue
        print("\n\n===========================================")
        print("--- Policy-map: %s" % PM_name)
        getInterfaceSP(cisco_manager, PM_name)

        for c in classes:
            CM_name = c.firstChild.firstChild.nodeValue
            getCM(cisco_manager, CM_name)

            actionList = c.getElementsByTagName("action-list")
            if actionList.length > 0:
                print("--- Action")
                getDomContent(actionList)
                print("-------------------------------------")


def getCM(cisco_manager, CM_name):
    """
    # Filter for IOS >16.6
    ACL_name_filter = '''
                      <filter>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <policy><class-map xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-policy"></class-map></policy>
                        </native>
                      </filter>
                      '''
    """
    ACL_name_filter = '''
                      <filter>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <class-map></class-map>
                        </native>                        
                      </filter>
                      '''

    rawOutput = cisco_manager.get_config('running', ACL_name_filter)
    XMLOutput = minidom.parseString(rawOutput.xml)
    classMaps = XMLOutput.getElementsByTagName("class-map")
    CM_isFound = False
    for cm in classMaps:
        name = cm.firstChild.firstChild.nodeValue
        if CM_name ==  "class_default":
             print("\n--- Class-map: %s"%(CM_name))
        elif name == CM_name:
            CM_isFound = True
            accessGroups = cm.getElementsByTagName("access-group")
            prematch = cm.getElementsByTagName("prematch")[0].firstChild.nodeValue
            print("\n--- Class-map: %s [%s]"%(name, prematch))

            if accessGroups.length > 0:
                for ag in accessGroups:
                    agName = ag.firstChild.firstChild.nodeValue
                    getACLfromCM(cisco_manager, agName)
            break
    if not CM_isFound:
        print("%s%s--- Class-map: %s [IGNORE 'class-default']%s" % (color.BOLD, color.FAIL, CM_name, color.ENDC))


def getACLfromCM(cisco_manager, AGname):
    """
    # Filter for IOS >16.6
    ACL_name_filter = '''
                      <filter>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <ip><access-list>
                                <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
                                </extended>
                            </access-list></ip>
                        </native>
                      </filter>
                      '''
    """
    ACL_name_filter = '''
                      <filter>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <ip><access-list>
                                <extended>
                                </extended>
                            </access-list></ip>
                        </native>                        
                      </filter>
                      '''
    # IOS-XE pre-16.2     YANG model called urn:ios
    # IOS-XE 16.2 - 16.4  YANG model called http://cisco.com/ns/yang/ned/ios
    # IOS-XE 16.5+        YANG model called http://cisco.com/ns/yang/Cisco-IOS-XE-native
    rawOutput = cisco_manager.get_config('running', ACL_name_filter)

    XMLOutput = minidom.parseString(rawOutput.xml)
    ACLs = XMLOutput.getElementsByTagName("extended")
    ACL_isFound = False
    #iterate through each ACL
    for ACL in ACLs:
        name = ACL.childNodes[0].firstChild.nodeValue
        if (name == AGname):
            ACL_isFound = True
            print("\t--- ACL: %s ---" % name)
            AclEntries = ACL.getElementsByTagName("ace-rule")

            table = PrettyTable(["Action","Protocol","Src Nw", "Src mask", "Src Port", "Dst NW", "Dst Mask", "Dst Port"])

            for entry in AclEntries:
                action = entry.getElementsByTagName("action")[0].firstChild.nodeValue
                protocol = entry.getElementsByTagName("protocol")[0].firstChild.nodeValue

                # Check source
                source = checkSrcDest(entry,"ipv4-address")
                # Check source port
                srcPort = checkSrcDestPort(entry,protocol,"src-eq")

                # Check destination
                destination = checkSrcDest(entry,"dest-ipv4-address")
                # Check destination port
                dstPort = checkSrcDestPort(entry,protocol,"dst-eq")

                if action == "deny":
                    table.add_row([action,protocol,source[0],source[1],srcPort,destination[0],destination[1],dstPort])
                else:
                    table.add_row([action,protocol,source[0],source[1],srcPort,destination[0],destination[1],dstPort])

            print(table)

    if not ACL_isFound:
        print("\t%s%s--- ACL: %s DOES NOT EXIST%s"%(color.BOLD, color.FAIL, AGname, color.ENDC))


# Used to check both source or destination tag. Use either "dest-ipv4-address" or "ipv4-address"  for "tag" param
def checkSrcDest (ACLEntry, tag):
    source = ACLEntry.getElementsByTagName(tag)
    if source.length <= 0:
        mask = ''
        src_host = ACLEntry.getElementsByTagName("host")
        if src_host.length > 0:
            source = src_host[0].firstChild.nodeValue
            mask = '0.0.0.0'
        else:
            source = 'Any'
    else:
        source = source[0].firstChild.nodeValue
        if tag == "dest-ipv4-address":
            mask_tag = "dest-mask"
        elif tag == "ipv4-address":
            mask_tag = "mask"
        mask = ACLEntry.getElementsByTagName(mask_tag)[0].firstChild.nodeValue
    return [source, mask]


# Used to check both source or destination tag. Use either "src-eq" or "dst-eq" for "tag" param
def checkSrcDestPort (ACLEntry, protocol,tag):
    port = '[]'
    if protocol == "tcp" or protocol == "udp":
        port = ACLEntry.getElementsByTagName(tag.split("-")[0]+"-eq")
        if port.length > 0:
            port = port[0].firstChild.nodeValue
        else:
            range_tag = tag.split("-")[0]+"-range"
            port_1 = ACLEntry.getElementsByTagName((range_tag + "1"))
            if(port_1.length > 0):
                port_2 = ACLEntry.getElementsByTagName((range_tag + "2"))
                port = "%s - %s"%(port_1[0].firstChild.nodeValue, port_2[0].firstChild.nodeValue)
    else:
        port = "[]"
    return port


# Pretty print a raw XML String
def XMLBeautifier (rawXML):
    print(minidom.parseString(rawXML.xml).toprettyxml())


def getDomContent (element):
    for node in element:
        if node.nodeType == node.TEXT_NODE:
            print("\t\t\t%s" % node.data)
        else:
            print("\t\t<%s>" % node.tagName)
            getDomContent(node.childNodes)


if __name__ == '__main__':
    main()

