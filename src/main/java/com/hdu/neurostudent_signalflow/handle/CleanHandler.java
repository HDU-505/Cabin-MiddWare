package com.hdu.neurostudent_signalflow.handle;

import com.hdu.neurostudent_signalflow.devicelister.mindtooth.MindToothDeviceLister;
import com.hdu.neurostudent_signalflow.service.ParadigmService;
import com.hdu.neurostudent_signalflow.utils.websocket.MindtoothWebSocketClient;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;

@Component
@Slf4j
public class CleanHandler {
    private CleanHandler() {}   // 私有构造方法，防止外部实例化

    @Resource
    private ParadigmService paradigmService;
    @Resource
    private MindtoothWebSocketClient mindtoothWebSocketClient;

    public void handleCleanState() {
        log.info("执行清理状态逻辑，停止当前范式");
        paradigmService.stopParadigm();
        mindtoothWebSocketClient.send("calibration");
    }
}
