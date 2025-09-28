package com.hdu.neurostudent_signalflow;

import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.devicelister.MindToothEnvInit;
import com.hdu.neurostudent_signalflow.utils.IdGenerator;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

import javax.annotation.Resource;

@SpringBootApplication
@ComponentScan("com.hdu")
@EnableFeignClients
public class NeuroStudentSignalFlowApplication {
    @Resource
    MindToothEnvInit mindToothEnvInit;

    public static void main(String[] args) {
        SpringApplication.run(NeuroStudentSignalFlowApplication.class, args);

        // 添加 JVM 关闭钩子
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            // 在这里添加您需要的销毁操作
            System.out.println("Application is shutting down...");
            // 关闭数据库连接
        }));
    }



}
