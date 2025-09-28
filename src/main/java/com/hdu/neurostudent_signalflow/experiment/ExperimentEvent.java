package com.hdu.neurostudent_signalflow.experiment;

public enum ExperimentEvent {
    START_PREPARATION,  // 开始准备
    START_EXPERIMENT,   // 开始实验
    PAUSE_EXPERIMENT,   // 暂停实验
    RESUME_EXPERIMENT,  // 恢复实验
    END_EXPERIMENT,     // 结束实验
    ERROR_OCCURED       // 发生异常
}
