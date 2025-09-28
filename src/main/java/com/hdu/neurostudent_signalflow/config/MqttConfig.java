package com.hdu.neurostudent_signalflow.config;

import com.hdu.neurostudent_signalflow.utils.mqtt.MqttAcceptClient;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;

/**
 * @Description : 启动服务的时候开启监听客户端
 * @Author : DZL
 * @Date : 2023/10/26 16:35
 */
@Configuration
@ConfigurationProperties("mqtt")
@Data
public class MqttConfig {
    private boolean mqttEnabled;
}
