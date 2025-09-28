package com.hdu.neurostudent_signalflow.service;

import com.hdu.neurostudent_signalflow.utils.mqtt.MqttSendClient;
import com.hdu.neurostudent_signalflow.utils.websocket.MindtoothWebSocketClient;
import lombok.Setter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.concurrent.*;

/*
 * 数据转发服务
 * 功能：将数据转发到目标地址，可扩展写
 */
@Component
@Scope("prototype")
public class DataTransmitService {
    private static final Logger logger = LoggerFactory.getLogger(DataTransmitService.class);

    @Resource
    private MqttSendClient mqttSendClient;

    @Resource
    private MindtoothWebSocketClient mindtoothWebSocketClient;

    @Setter
    private BlockingQueue<String> sendQueue;

    private final ExecutorService consumer = Executors.newSingleThreadExecutor();

    public void start() {
        consumer.submit(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    String data = sendQueue.take();
                    DataTran(data);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
    }

    public void stop() {
        consumer.shutdownNow();
    }

    private void DataTran(String data) {
        mqttSendClient.publish(false, "test", data);
        mindtoothWebSocketClient.send(data);
    }
}
