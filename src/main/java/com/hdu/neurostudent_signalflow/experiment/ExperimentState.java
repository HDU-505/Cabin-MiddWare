package com.hdu.neurostudent_signalflow.experiment;

public enum ExperimentState {
    NOT_STARTED,   // 未开始
    PREPARING,     // 准备中   【由中间件前端触发该状态】
    RUNNING,       // 进行中   【由中间件前端触发该状态】
    PAUSED,        // 暂停
    ENDED,         // 结束
    ERROR          // 异常
}
