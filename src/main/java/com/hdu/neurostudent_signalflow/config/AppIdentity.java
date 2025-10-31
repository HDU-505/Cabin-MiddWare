package com.hdu.neurostudent_signalflow.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;

@Configuration
@ConfigurationProperties(prefix = "app")
public class AppIdentity {
    private static String name;
    private static String instanceId;

    public void setName(String name) {
        AppIdentity.name = name;
    }

    public void setInstanceId(String instanceId) {
        AppIdentity.instanceId = instanceId;
    }

    public static String getIdentity() {
        return name + ":" + instanceId;
    }
}
