package com.hdu.neurostudent_signalflow.utils.mqtt;

import com.hdu.neurostudent_signalflow.config.MqttConfig;
import com.hdu.neurostudent_signalflow.config.MqttProperties;
import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;
import java.util.UUID;

@Component
public class MqttSendClient {

    private static final Logger logger = LoggerFactory.getLogger(MqttSendClient.class);

    @Resource
    MqttConfig mqttConfig;

    private boolean mqttEnabled;

    private boolean mqttConnected ;

    private final MqttSendCallBack mqttSendCallBack;
    private final MqttProperties mqttProperties;
    private MqttClient mqttClient;
    private int connNum = 0;

    @PostConstruct
    private void init() {
        this.mqttEnabled = mqttConfig.isMqttEnabled();
        connect(); // 初次连接
    }

    @Autowired
    public MqttSendClient(@Lazy MqttSendCallBack mqttSendCallBack, MqttProperties mqttProperties) {
        this.mqttSendCallBack = mqttSendCallBack;
        this.mqttProperties = mqttProperties;
//        connect(); // 初次连接
    }

    public void connect() {
        while (mqttEnabled) {
            try {
                String uuid = UUID.randomUUID().toString().replaceAll("-", "");
                mqttClient = new MqttClient(mqttProperties.getHostUrl(), uuid, new MemoryPersistence());
                MqttConnectOptions options = new MqttConnectOptions();
                options.setUserName(mqttProperties.getUsername());
                options.setPassword(mqttProperties.getPassword().toCharArray());
                options.setConnectionTimeout(mqttProperties.getTimeout());
                options.setKeepAliveInterval(mqttProperties.getKeepAlive());
                options.setCleanSession(true);
                mqttClient.setCallback(mqttSendCallBack);
                mqttClient.connect(options);
                logger.info("MqttSendClient 成功连接到服务器");

                // 调用 connectComplete 手动通知回调
                mqttSendCallBack.connectComplete(connNum > 0, mqttClient.getServerURI());
                connNum++;
                break; // 连接成功，跳出循环
            } catch (MqttException e) {
                logger.error("MqttSendClient 连接失败，正在重试，错误信息: {}", e.getMessage());
                try {
                    Thread.sleep(5000); // 等待5秒后重试
                } catch (InterruptedException ex) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("重试连接时线程被中断", ex);
                }
            }
        }
    }

    public void reconnection() {
        logger.info("正在尝试重连");
        connect(); // 调用连接方法重新连接
    }

    public void publish(boolean retained, String topic, String content) {
        try {
            MqttMessage message = new MqttMessage();
            message.setQos(mqttProperties.getQos());
            message.setRetained(retained);
            message.setPayload(content.getBytes());
            mqttClient.publish(mqttProperties.getServerTopic(topic), message);
        } catch (MqttException e) {
            logger.error("MqttSendClient publish error, message: {}", e.getMessage(), e);
        }
    }

    public static void disconnect(MqttClient mqttClient) {
        try {
            if (mqttClient != null) {
                mqttClient.disconnect();
            }
        } catch (MqttException e) {
            logger.error("MqttSendClient disconnect error, message: {}", e.getMessage(), e);
        }
    }

    public static void close(MqttClient mqttClient) {
        try {
            if (mqttClient != null) {
                mqttClient.close();
            }
        } catch (MqttException e) {
            logger.error("MqttSendClient close error, message: {}", e.getMessage(), e);
        }
    }
}
