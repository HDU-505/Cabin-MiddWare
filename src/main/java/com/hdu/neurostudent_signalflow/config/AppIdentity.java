package com.hdu.neurostudent_signalflow.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class AppIdentity {

    @Value("${app.name}")
    private String appName;

    @Value("${app.instance-id}")
    private String instanceId;

    public String getIdentity() {
        return appName + ":" + instanceId;
    }
}
