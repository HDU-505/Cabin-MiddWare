package com.hdu.neurostudent_signalflow.websocket;

import com.hdu.neurostudent_signalflow.experiment.ExperimentState;
import com.hdu.neurostudent_signalflow.utils.IdGenerator;
import lombok.Data;

@Data
public class ExperimentStateMessage {
    private String id;
    private String machineId;
    private String experimentId;
    private ExperimentState state;

    // 附加字段
    private String experimentInfo;

    public ExperimentStateMessage(String machineId,String experimentId, ExperimentState state){
        // 随机生成id
        id = IdGenerator.generateStateMessageId();
        this.machineId = machineId;
        this.experimentId = experimentId;
        this.state = state;
    }
}
