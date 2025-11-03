package com.hdu.neurostudent_signalflow.handle;

import com.hdu.neurostudent_signalflow.monitor.CameraMonitor;
import com.hdu.neurostudent_signalflow.monitor.ScreenMonitor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
@Slf4j
public class RunningHandler {
    // 私有构造方法，防止外部实例化
    private RunningHandler() {}

    // 处理运行状态的逻辑
    public void handleRunningState() {
        log.info("实验状态处于运行期，执行相关逻辑");
        CameraMonitor.startCameraMonitor(); //开始摄像头监控
        ScreenMonitor.startScreenMonitor(); //开始屏幕监控
    }
}
