package com.hdu.neurostudent_signalflow.handle;

import com.hdu.neurostudent_signalflow.experiment.ExperimentEvent;
import com.hdu.neurostudent_signalflow.experiment.ExperimentStateMachine;
import com.hdu.neurostudent_signalflow.monitor.CameraMonitor;
import com.hdu.neurostudent_signalflow.monitor.ScreenMonitor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
@Slf4j
public class EndHandler {
    // 私有构造方法，防止外部实例化
    private EndHandler(){}

    public void handleEndState() {
        log.info("实验状态处于结束,执行相关逻辑");
        ScreenMonitor.stopScreenMonitor();  // 停止屏幕监控
        CameraMonitor.stopCameraMonitor();  // 停止摄像头监控
        ExperimentStateMachine.getInstance().handleEvent(ExperimentEvent.RESET_EXPERIMENT); // 触发重置实验事件
    }
}
