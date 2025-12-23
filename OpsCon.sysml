
part def 'OpsCon_UAV_basedAircraftInspection'{
part 'Human';
part 'Environment';
part 'Drone';
part 'Aircraft';
use case 'InspectAircraftAutomatically'{
subject SoI ;
actor DroneOperator;
actor CandidateAircraft ;
actor InspectionEnvironment ;
objective 'InspectAircraft' {
doc
/* FlyAutomatically
* AquireAircraftExternalVisuuaImages
* Safe_UAV_Flight
*/
}
connect Human to DroneOperator;
connect Environment to InspectionEnvironment;
connect Drone to SoI;
connect Aircraft to CandidateAircraft;
}
}