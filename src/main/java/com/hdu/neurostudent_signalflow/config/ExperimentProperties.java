package com.hdu.neurostudent_signalflow.config;

import com.hdu.neurostudent_signalflow.entity.Experiment;
import com.hdu.neurostudent_signalflow.experiment.ExperimentState;

import java.util.Date;

public class ExperimentProperties {
    public static String experimentId = "OFFLINE";
    public static ExperimentState state;
    public static Experiment experiment = new Experiment();
}
