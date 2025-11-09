package com.hdu.neurostudent_signalflow.websocket;

import com.hdu.neurostudent_signalflow.entity.Experiment;
import com.hdu.neurostudent_signalflow.experiment.ExperimentEvent;
import com.hdu.neurostudent_signalflow.experiment.ExperimentState;
import com.hdu.neurostudent_signalflow.utils.IdGenerator;
import lombok.Data;

@Data
public class ExperimentStateMessage {
    private String id;
    private String machineId;
    private ExperimentState state;
    private ExperimentEvent event;

    // 附加字段
    private Experiment experiment;

    public ExperimentStateMessage(String machineId, ExperimentState state, ExperimentEvent event, Experiment experiment){
        // 随机生成id
        id = IdGenerator.generateStateMessageId();
        this.machineId = machineId;
        this.state = state;
        this.event = event;
        this.experiment = experiment;
    }
}
