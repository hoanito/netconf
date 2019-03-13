# netconf

The script will check for Policy maps (PM) in the configuration and the interfaces to which each they are applied to as service policies. Under each PM, the ACLs and actions will be displayed. It saves a lot of time typing show commands repeatedly. A sample output is shown below.

===========================================
--- Policy-map: PM-IB-Trunk
		Applied to:
			GigabitEthernet1/0/45 [input]
		Applied to:
			GigabitEthernet1/0/46 [input]
		Applied to:
			GigabitEthernet1/0/47 [input]
		Applied to:
			GigabitEthernet1/1/1 [input]
		Applied to:
			GigabitEthernet1/1/2 [input]

--- Class-map: CM-IB-RC-GeneralSIP [match-any]
	--- ACL: ACL-IB-RC-GeneralSIP ---
+--------+----------+--------+----------+----------+---------------+------------+-------------+
| Action | Protocol | Src Nw | Src mask | Src Port |     Dst NW    |  Dst Mask  |   Dst Port  |
+--------+----------+--------+----------+----------+---------------+------------+-------------+
| permit |   tcp    |  Any   |          |    []    |  80.81.128.0  | 0.0.15.255 | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  80.81.128.0  | 0.0.15.255 | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    |  103.44.68.0  | 0.0.3.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  103.44.68.0  | 0.0.3.255  | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    |  104.245.56.0 | 0.0.7.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  104.245.56.0 | 0.0.7.255  | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    |  185.23.248.0 | 0.0.3.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  185.23.248.0 | 0.0.3.255  | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    |  192.209.24.0 | 0.0.7.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  192.209.24.0 | 0.0.7.255  | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    | 199.255.120.0 | 0.0.3.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    | 199.255.120.0 | 0.0.3.255  | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    |  199.68.212.0 | 0.0.3.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  199.68.212.0 | 0.0.3.255  | 5060 - 5099 |
| permit |   tcp    |  Any   |          |    []    |  208.87.40.0  | 0.0.3.255  | 5060 - 5099 |
| permit |   udp    |  Any   |          |    []    |  208.87.40.0  | 0.0.3.255  | 5060 - 5099 |
+--------+----------+--------+----------+----------+---------------+------------+-------------+
--- Action
		<action-list>
		<action-type>
			set
		<set>
		<qos-group>
		<qos-group-value>
			3
-------------------------------------

By default, IOS will not verify ACL names in class maps. This makes it really difficult to troubleshoot when we make a small typo and cannot figure out why our voice traffic is left un-tagged or transferred in lower priority queues. The script will also help to troubleshoot this common mistake as we can see from the next output:

-------------------------------------

--- Class-map: CM-IB-RC-Other [match-any]
	  --- ACL: ACL-IB-RC-Networks-All DOES NOT EXIST
--- Action
		<action-list>
		<action-type>
			set
		<set>
		<qos-group>
		<qos-group-value>
			4
-------------------------------------

The script is implemented based on a simple configuration, so it will not work perfectly. I will be adding more to the script as I see more variations of MQC configuration.
