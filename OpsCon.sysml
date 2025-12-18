part def 'OpsCon_UAV_Based_Aircraft_Inspection_v2' {

    part 'Human';
    part 'Environment';
    part 'Drone';
    part 'Aircraft';
    part 'GroundStation';

    actor 'UAVOperator';
    actor 'MaintenanceEngineer';
    actor 'InspectionEnvironment';
    actor 'TargetAircraft';

    use case 'InspectAircraftAutomatically' {
        subject SoI;

        objective 'InspectAircraft' {
            doc
            /*
             - Autonomous UAV navigation
             - Capture aircraft surface images
             - Detect visible damage
             - Maintain safe flight path
            */
        }
    }

    use case 'EmergencyLanding' {
        objective 'LandSafely' {
            doc
            /*
             - Detect critical battery level
             - Identify safe landing zone
             - Execute controlled landing
            */
        }
    }

    connect Human to UAVOperator;
    connect Human to MaintenanceEngineer;
    connect Environment to InspectionEnvironment;
    connect Drone to SoI;
    connect Aircraft to TargetAircraft;
    connect GroundStation to UAVOperator;
}
