package OpsCon {

    part def SystemController {
        doc /* Main system controller component */
    }
    
    part def SensorModule {
        doc /* Sensor data collection module */
    }
    
    part def DataProcessor {
        doc /* Processes sensor data */
    }
    
    part def DisplayUnit {
        doc /* User interface display */
    }
    
    part def NetworkInterface {
        doc /* Network communication interface */
    }
    
    part def OpsConSystem {
        doc /* Operations Control System */
        
        part SystemController;
        part SensorModule;
        part DataProcessor;
        part DisplayUnit;
        part NetworkInterface;
        
        connect SystemController to SensorModule;
        connect SystemController to DataProcessor;
        connect DataProcessor to DisplayUnit;
        connect SystemController to NetworkInterface;
        connect SensorModule to DataProcessor;
    }
}

